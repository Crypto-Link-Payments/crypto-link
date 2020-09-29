import discord
from discord.ext import commands
from discord import User
import re
from backOffice.profileRegistrations import AccountManager
from backOffice.statsManager import StatsManager
from backOffice.userWalletManager import UserWalletManager
from backOffice.stellarActivityManager import StellarManager
from backOffice.guildServicesManager import GuildProfileManager
from cogs.utils import monetaryConversions
from cogs.utils.customCogChecks import is_public, has_wallet
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
account_mng = AccountManager()
stellar = StellarManager()
user_wallets = UserWalletManager()
stats_manager = StatsManager()
guild_profiles = GuildProfileManager()
customMessages = CustomMessages()

d = helper.read_json_file(file_name='botSetup.json')
integrated_coins = helper.read_json_file(file_name='integrateCoins.json')

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_TX_ERROR_TITLE = ":exclamation: __Transaction Error__ :exclamation: "


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
        self.list_of_coins = ["xlm"]

    async def update_stats(self, ctx, transaction_data: dict, type: str):

        if type == "public":
            global_stats = {
                "totalTx": 1,
                'totalMoved': transaction_data["amount"],
                "totalPublicCount": 1,
                "totalPublicMoved": transaction_data["amount"],
            }

            sender_stats = {
                "xlmStats.publicTxSendCount": 1,
                "xlmStats.publicSent": transaction_data["amount"],
            }

            recipient_stats = {
                "xlmStats.publicTxReceivedCount": 1,
                "xlmStats.publicReceived": transaction_data["amount"],
            }

            guild_stats = {
                "communityStats.xlmVolume": transaction_data["amount"],
                "communityStats.txCount": 1,
                "communityStats.publicCount": 1
            }

        # Update stats stats
        await stats_manager.update_cl_tx_stats(ticker='xlm', ticker_stats=global_stats)

        # Updates sender and recipient public transaction stats
        await stats_manager.update_usr_tx_stats(user_id=ctx.message.author.id,
                                                tx_stats_data=sender_stats)
        await stats_manager.update_usr_tx_stats(user_id=transaction_data["recipientId"],
                                                tx_stats_data=recipient_stats)

        await stats_manager.update_guild_stats(guild_id=ctx.message.guild.id,
                                               guild_stats_data=guild_stats)

    async def stream_transaction(self, ctx, recipient, tx_details: dict, message: str):
        """
        Send reports out to all destinations
        """
        await customMessages.transaction_report_to_channel(ctx=ctx, recipient=recipient,
                                                           amount=tx_details["amount"], currency=tx_details["ticker"])

        msg = process_message(message=message)

        # report to sender
        await customMessages.transaction_report_to_user(ctx=ctx, direction=0, amount=tx_details["amount"],
                                                        symbol='xlm',
                                                        user=recipient,
                                                        destination=ctx.message.author,
                                                        message=msg)

        # report to recipient
        await customMessages.transaction_report_to_user(ctx=ctx, direction=1, amount=tx_details["amount"],
                                                        symbol='xlm', user=ctx.message.author,
                                                        destination=recipient, message=msg)

        # Send out explorer
        in_dollar = monetaryConversions.convert_to_usd(amount=tx_details["amount"], coin_name='stellar')
        load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                         guild_profiles.get_all_explorer_applied_channels()]
        explorer_msg = f'💵  {tx_details["amount"]} {CONST_STELLAR_EMOJI} (${in_dollar["total"]}) on ' \
                       f'{ctx.message.guild} channel {ctx.message.channel}'
        await customMessages.explorer_messages(applied_channels=load_channels,
                                               message=explorer_msg)

    @commands.group()
    @commands.check(is_public)
    @commands.check(has_wallet)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def send(self, ctx, amount: float, ticker: str, recipient: User, *, message: str = None):
        coin = ticker.lower()
        if amount > 0:
            if not ctx.message.author == recipient and not recipient.bot:
                if not re.search("[~!#$%^&*()_+{}:;\']", coin) and coin in self.list_of_coins:
                    coin_data = helper.read_json_file(file_name='integratedCoins.json')[ticker]
                    atomic_value = (int(amount * (10 ** int(coin_data["decimal"]))))
                    # Get user wallet ticker balance
                    wallet_value = user_wallets.get_ticker_balance(ticker=ticker, user_id=ctx.message.author.id)
                    if wallet_value >= atomic_value:
                        # Check if recipient has wallet or not
                        if not account_mng.check_user_existence(user_id=recipient.id):
                            account_mng.register_user(discord_id=recipient.id, discord_username=f'{recipient}')

                        if user_wallets.update_coin_balance(coin=ticker, user_id=ctx.message.author.id,
                                                            amount=int(atomic_value), direction=2):
                            if user_wallets.update_coin_balance(coin=ticker, user_id=recipient.id,
                                                                amount=int(atomic_value), direction=1):
                                coin_data["amount"] = (atomic_value / (10 ** 7))
                                coin_data["ticker"] = ticker

                                # Produce dict for streamer
                                await self.stream_transaction(ctx=ctx, recipient=recipient, tx_details=coin_data,
                                                              message=message)

                                coin_data["recipientId"] = recipient.id

                                await self.update_stats(ctx=ctx, transaction_data=coin_data, type='public')

                            else:
                                user_wallets.update_coin_balance(coin=ticker, user_id=ctx.message.author.id,
                                                                 amount=int(atomic_value), direction=1)
                                message = f'{amount} XLA could not be sent to the {recipient} please try again later'
                                await customMessages.system_message(ctx=ctx, color_code=1, message=message,
                                                                    destination=1,
                                                                    sys_msg_title=CONST_TX_ERROR_TITLE)

                        else:
                            message = f'There has been an error while making P2P transaction please try again later'
                            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                                sys_msg_title=CONST_TX_ERROR_TITLE)
                    else:

                        message = f'You have insufficient balance! Your current wallet balance is' \
                                  f' {wallet_value / 10000000} XLM'
                        await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                            sys_msg_title=CONST_TX_ERROR_TITLE)
                else:

                    message = f'Coin {coin} has not been integrated yet into {self.bot.user}.'
                    await customMessages.system_message(ctx=ctx, color_code=1, message=message,
                                                        destination=1,
                                                        sys_msg_title=CONST_TX_ERROR_TITLE)
            else:

                message = f'You are not allowed to send {amount} xlm to either yourself or the bot.'
                await customMessages.system_message(ctx=ctx, color_code=1, message=message,
                                                    destination=1,
                                                    sys_msg_title=CONST_TX_ERROR_TITLE)
        else:
            message = 'Amount needs to be greater than 0.0000000 XLM'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=CONST_TX_ERROR_TITLE)

    @send.error
    async def send_error(self, ctx, error):
        print(f'ERR SEND TRIGGERED  : {error}')
        if isinstance(error, commands.CheckFailure):
            title = f'__System Transaction Error__'
            message = f'In order to execute P2P transaction you need to be registered into the system, and ' \
                      f'transaction request needs to be executed on one of the text public text channels ' \
                      f'on {ctx.message.guild}'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)
        elif isinstance(error, commands.BadArgument):
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


def setup(bot):
    bot.add_cog(TransactionCommands(bot))
