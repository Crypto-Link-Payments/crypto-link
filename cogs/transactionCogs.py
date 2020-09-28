import discord
from discord.ext import commands

from backOffice.profileRegistrations import AccountManager
from backOffice.statsManager import StatsManager
from backOffice.stellarActivityManager import StellarManager
from backOffice.guildServicesManager import GuildProfileManager
from cogs.utils import monetaryConversions
from cogs.utils.customCogChecks import is_public, has_wallet
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
account_mng = AccountManager()
stellar = StellarManager()
stats_manager = StatsManager()
guild_profiles = GuildProfileManager()
customMessages = CustomMessages()
d = helper.read_json_file(file_name='botSetup.json')
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'


def process_message(message):
    """
    Filter message so it is not too long for transaction report
    """
    if message:
        if len(message) > 100:
            message = message[:98] + '...'
    else:
        message = 'None'

    return message


class TransactionCommands(commands.Cog):
    """
    Class handling off-chain discord transactions
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(is_public)
    @commands.check(has_wallet)
    async def send(self, ctx):
        """
        Command entry point for making peer to peer transactions
        """

        print(f'SEND: {ctx.author} -> {ctx.message.content}')

        if ctx.invoked_subcommand is None:
            title = '💵 __Available p2p transaction commands__ 💵'
            description = "Bellow are presented all available currencies for P2P transactions"
            list_of_values = [
                {"name": f"{CONST_STELLAR_EMOJI} Stellar Lumen {CONST_STELLAR_EMOJI}",
                 "value": f"{d['command']}send xlm <amount> <@DiscordUser>\n"
                          f"\nexample:\n"
                          f"{d['command']}send xlm 100 @Animus#4608"}]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values)

    @send.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def xlm(self, ctx, amount: float, recipient: discord.User, *, message: str = None):
        """
        Initiates off chain transaction for stellar lumen currency
        :param ctx:
        :param amount:
        :param recipient:
        :param message: User message to recipient
        :return:
        """

        print(f'SEND XLM: {ctx.author} -> {ctx.message.content}')
        stroops = (int(amount * (10 ** 7)))
        if stroops > 0:
            if not ctx.message.author == recipient and not recipient.bot:
                wallet_value = stellar.get_stellar_wallet_data_by_discord_id(discord_id=ctx.message.author.id)[
                    'balance']
                if int(wallet_value) >= int(stroops):
                    if not account_mng.check_user_existence(user_id=recipient.id):
                        account_mng.register_user(discord_id=recipient.id, discord_username=f'{recipient}')
                    decimal_point = monetaryConversions.get_decimal_point('xlm')
                    assert amount == float(monetaryConversions.get_normal(str(stroops),
                                                                          decimal_point=decimal_point))

                    if stellar.update_stellar_balance_by_discord_id(discord_id=ctx.message.author.id,
                                                                    stroops=int(stroops), direction=2):
                        if stellar.update_stellar_balance_by_discord_id(discord_id=recipient.id, stroops=int(stroops),
                                                                        direction=1):

                            final_xlm = round(float(stroops / 10000000), 7)

                            await customMessages.transaction_report_to_channel(ctx=ctx, recipient=recipient,
                                                                               amount=amount, currency='xlm')

                            msg = process_message(message=message)

                            # report to sender
                            await customMessages.transaction_report_to_user(ctx=ctx, direction=0, amount=amount,
                                                                            symbol='xlm',
                                                                            user=recipient,
                                                                            destination=ctx.message.author,
                                                                            message=msg)

                            # report to recipient
                            await customMessages.transaction_report_to_user(ctx=ctx, direction=1, amount=amount,
                                                                            symbol='xlm', user=ctx.message.author,
                                                                            destination=recipient, message=msg)

                            global_ticker_stats = {
                                "totalTx": 1,
                                'totalMoved': final_xlm,
                                "totalPublicCount": 1,
                                "totalPublicMoved": final_xlm,
                            }

                            # Updateing bot global stats
                            await stats_manager.update_cl_tx_stats(ticker='xlm', ticker_stats=global_ticker_stats)

                            sender_stats = {
                                "xlmStats.publicTxSendCount": 1,
                                "xlmStats.publicSent": final_xlm,
                            }

                            recipient_stats = {
                                "xlmStats.publicTxReceivedCount": 1,
                                "xlmStats.publicReceived": final_xlm,
                            }

                            # Updates sender and recipient public transaction stats
                            await stats_manager.update_usr_tx_stats(user_id=ctx.message.author.id,
                                                                    tx_stats_data=sender_stats)
                            await stats_manager.update_usr_tx_stats(user_id=recipient.id, tx_stats_data=recipient_stats)

                            guild_stats = {
                                "communityStats.xlmVolume": final_xlm,
                                "communityStats.txCount": 1,
                                "communityStats.publicCount": 1
                            }

                            await stats_manager.update_guild_stats(guild_id=ctx.message.guild.id,
                                                                   guild_stats_data=guild_stats)

                            # Explorer notification
                            in_dollar = monetaryConversions.convert_to_usd(amount=final_xlm, coin_name='stellar')
                            load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                                             guild_profiles.get_all_explorer_applied_channels()]
                            explorer_msg = f'💵  {final_xlm} {CONST_STELLAR_EMOJI} (${in_dollar["total"]}) on ' \
                                           f'{ctx.message.guild} channel {ctx.message.channel}'
                            await customMessages.explorer_messages(applied_channels=load_channels,
                                                                   message=explorer_msg)

                        else:
                            stellar.update_stellar_balance_by_discord_id(discord_id=ctx.message.author.id,
                                                                         stroops=int(stroops),
                                                                         direction=1)
                            title = '__Error in transaction__'
                            message = f'{amount} XLA could not be sent to the {recipient} please try again later'
                            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                                sys_msg_title=title)

                    else:
                        title = '__Error in transaction__'
                        message = f'There has been an error while making P2P transaction please try again later'
                        await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                            sys_msg_title=title)

                else:
                    title = '__Insufficient balance__'
                    message = f'You have insufficient balance! Your current wallet balance is' \
                              f' {wallet_value / 10000000} XLM'
                    await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                        sys_msg_title=title)
            else:
                title = '__Recipient error__'
                message = f'You are not allowed to send {amount} xlm to either yourself or the bot.'
                await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                    sys_msg_title=title)
        else:
            title = '__Amount error__'
            message = 'Amount needs to be greater than 0.0000000 XLM'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)

    @send.error
    async def send_error(self, ctx, error):
        print(f'ERR SEND TRIGGERED  : {error}')
        if isinstance(error, commands.CheckFailure):
            title = f':warning:  __Conditions not met __ :warning: '
            message = f'In order to successfully execute transaction, following conditions need to be met:\n' \
                      f'```-> You have to have registered wallet and sufficient balance\n' \
                      f'-> Command needs to be executed on public channel```'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)

    @xlm.error
    async def xlm_send_error(self, ctx, error):
        print(f'ERR XLM SEND TRIGGERED  : {error}')
        if isinstance(error, commands.BadArgument):
            title = f'__Bad Argument Provided __'
            message = f'You have provided wrong argument either for amount or than for the recipient'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)
        elif isinstance(error, AssertionError):
            title = f'__Amount Check failed __'
            message = f'You have provided wrong amount for tx value.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)
        elif isinstance(error, commands.CommandOnCooldown):
            title = f'__Command on cool-down__!'
            message = f'{error}. Please try again after {error.retry_after}s'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)

        elif isinstance(error, commands.MissingRequiredArgument):
            title = f'__Missing Required Argument Error __'
            message = f'{str(error)}'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)

        elif isinstance(error, commands.CheckFailure):
            title = f'__System Transaction Error__'
            message = f'In order to execute P2P transaction you need to be registered into the system, and ' \
                      f'transaction request needs to be executed on one of the text channels on {ctx.message.guild}'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)
        else:
            print(f"Unknown error which ahs not been handled: {error}")


def setup(bot):
    bot.add_cog(TransactionCommands(bot))
