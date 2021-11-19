from discord.ext import commands
from discord import User
import re
from cogs.utils import monetaryConversions
from utils.customCogChecks import is_public, has_wallet
from cogs.utils.systemMessaages import CustomMessages

custom_messages = CustomMessages()
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
        self.backoffice = bot.backoffice

    def build_stats(self, transaction_data: dict, tx_type: str):
        """
        Process data according to the type of transaction
        """
        if tx_type == "public":
            processed = {"globalBot": {"totalTx": 1,
                                       'totalMoved': transaction_data["amount"],
                                       "totalPublicCount": 1,
                                       "totalPublicMoved": transaction_data["amount"]},
                         "senderStats": {f"{transaction_data['ticker']}.publicTxSendCount": 1,
                                         f"{transaction_data['ticker']}.publicSent": transaction_data["amount"],
                                         },
                         "recipientStats": {f"{transaction_data['ticker']}.publicTxReceivedCount": 1,
                                            f"{transaction_data['ticker']}.publicReceived": transaction_data[
                                                "amount"],
                                            },
                         "guildStats": {
                             f'{transaction_data["ticker"]}.publicCount': 1,
                             f"{transaction_data['ticker']}.txCount": 1,
                             f"{transaction_data['ticker']}.volume": transaction_data["amount"]
                         }
                         }

        elif tx_type == 'private':
            processed = {"globalBot": {"totalTx": 1,
                                       'totalMoved': transaction_data["amount"],
                                       "totalPrivateCount": 1,
                                       "totalPrivateMoved": transaction_data["amount"]},
                         "senderStats": {f"{transaction_data['ticker']}.privateTxSendCount": 1,
                                         f"{transaction_data['ticker']}.privateSent": transaction_data["amount"],
                                         },
                         "recipientStats": {f"{transaction_data['ticker']}.privateTxReceivedCount": 1,
                                            f"{transaction_data['ticker']}.privateReceived": transaction_data[
                                                "amount"],
                                            },
                         "guildStats": {
                             f'{transaction_data["ticker"]}.privateCount': 1,
                             f"{transaction_data['ticker']}.txCount": 1,
                             f"{transaction_data['ticker']}.volume": transaction_data["amount"]
                         }
                         }

        return processed

    async def update_stats(self, ctx, transaction_data: dict, tx_type: str):
        """
        Update all required stats when transaction is executed
        """
        processed_stats = self.build_stats(transaction_data=transaction_data, tx_type=tx_type)

        # Update stats stats
        await self.backoffice.stats_manager.update_cl_off_chain_stats(ticker=transaction_data["ticker"],
                                                                      ticker_stats=processed_stats["globalBot"])

        # Updates sender and recipient public transaction stats
        await self.backoffice.stats_manager.update_usr_tx_stats(user_id=ctx.message.author.id,
                                                                tx_stats_data=processed_stats['senderStats'])
        await self.backoffice.stats_manager.update_usr_tx_stats(user_id=transaction_data["recipientId"],
                                                                tx_stats_data=processed_stats["recipientStats"])

        await self.backoffice.stats_manager.update_guild_stats(guild_id=ctx.message.guild.id,
                                                               guild_stats_data=processed_stats["guildStats"])

    async def stream_transaction(self, ctx, recipient, tx_details: dict, message: str, tx_type: str):
        """
        Send reports out to all destinations
        """
        # Process message
        msg = process_message(message=message)
        # Send to channel where tx has been executed
        native_token = None
        if tx_details['ticker'] == 'xlm':
            native_token = "stellar"

        if native_token:
            in_dollar = monetaryConversions.convert_to_usd(amount=tx_details["amount"], coin_name='stellar')
            tx_report_msg = f"{ctx.message.author} just sent {recipient.mention} {tx_details['amount']:.7f}" \
                            f" {tx_details['emoji']} (${in_dollar['total']:.4f})"
            explorer_msg = f'💵  {tx_details["amount"]:.7f} {CONST_STELLAR_EMOJI} (${in_dollar["total"]:.4f}) on ' \
                           f'{ctx.message.guild} channel {ctx.message.channel}'
            total_dollar_value = in_dollar['total']
            conversion_rate = in_dollar["usd"]
        else:
            explorer_msg = f'💵  {tx_details["amount"]} {tx_details["assetCode"].upper()} on ' \
                           f'{ctx.message.guild} channel {ctx.message.channel}'
            tx_report_msg = f"{ctx.message.author} just sent {recipient.mention} {tx_details['amount']:.7f} " \
                            f"{tx_details['assetCode'].upper()}"
            total_dollar_value = 0
            conversion_rate = 0

        if tx_type == 'private':
            explorer_msg = ":detective: "

        await custom_messages.transaction_report_to_channel(ctx=ctx, message=tx_report_msg, tx_type=tx_type)

        tx_details["conversion"] = total_dollar_value
        tx_details["conversionRate"] = conversion_rate

        # report to sender

        await custom_messages.transaction_report_to_user(ctx=ctx, user=recipient, transaction_data=tx_details,
                                                         destination=ctx.message.author,
                                                         direction=0, tx_type=tx_type,
                                                         message=msg)

        # report to recipient
        await custom_messages.transaction_report_to_user(ctx=ctx, user=ctx.message.author, transaction_data=tx_details,
                                                         destination=recipient,
                                                         direction=1, tx_type=tx_type,
                                                         message=msg)

        # Send out explorer

        load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                         self.backoffice.guild_profiles.get_all_explorer_applied_channels()]

        await custom_messages.explorer_messages(applied_channels=load_channels, message=explorer_msg)

    async def send_impl(self, ctx, amount: float, ticker: str, recipient: User, *, tx_type: str, message: str = None):
        coin = ticker.lower()
        if amount > 0:
            if not ctx.message.author == recipient and not recipient.bot:
                supported = [sup["assetCode"] for sup in self.bot.backoffice.token_manager.get_registered_tokens() if
                             sup["assetCode"] == coin]
                if supported or coin == 'xlm':
                    coin_data = self.backoffice.token_manager.get_token_details_by_code(coin)
                    atomic_value = (int(amount * (10 ** 7)))

                    # Get user wallet ticker balance
                    wallet_value = self.backoffice.wallet_manager.get_ticker_balance(asset_code=coin,
                                                                                     user_id=ctx.message.author.id)

                    if wallet_value:
                        if wallet_value >= atomic_value:
                            # Check if recipient has wallet or not
                            if not self.backoffice.account_mng.check_user_existence(user_id=recipient.id):
                                self.backoffice.account_mng.register_user(discord_id=recipient.id,
                                                                          discord_username=f'{recipient}')

                                # Update user count in guild system
                                await self.backoffice.stats_manager.update_registered_users(
                                    guild_id=ctx.message.guild.id)

                                # Increase bridge
                                await self.backoffice.stats_manager.create_bridge(user_id=ctx.message.author.id)

                                # Send up link
                                load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                                                 self.backoffice.guild_profiles.get_all_explorer_applied_channels()]
                                current_total = self.backoffice.account_mng.count_registrations()

                                explorer_msg = f':new: user registered into ***{self.bot.user} System*** ' \
                                               f'(Σ {current_total})'
                                for chn in load_channels:
                                    if chn is not None:
                                        await chn.send(content=explorer_msg)

                                await custom_messages.bridge_notification(ctx, recipient=recipient)

                            # Deduct balance from sender
                            if self.backoffice.wallet_manager.update_coin_balance(coin=coin,
                                                                                  user_id=ctx.message.author.id,
                                                                                  amount=int(atomic_value),
                                                                                  direction=2):
                                # Append to recipient
                                if self.backoffice.wallet_manager.update_coin_balance(coin=coin, user_id=recipient.id,
                                                                                      amount=int(atomic_value),
                                                                                      direction=1):

                                    normal_value = (atomic_value / (10 ** 7))

                                    coin_data["amount"] = normal_value
                                    coin_data["ticker"] = coin

                                    # Produce dict for streamer
                                    await self.stream_transaction(ctx=ctx, recipient=recipient, tx_details=coin_data,
                                                                  message=message, tx_type=tx_type)

                                    coin_data["recipientId"] = recipient.id

                                    await self.update_stats(ctx=ctx, transaction_data=coin_data, tx_type=tx_type)

                                else:
                                    self.backoffice.wallet_manager.update_coin_balance(coin=coin,
                                                                                       user_id=ctx.message.author.id,
                                                                                       amount=int(atomic_value),
                                                                                       direction=1)
                                    message = f'{amount} {coin.upper()} could not be sent to the {recipient} ' \
                                              f'please try again later'
                                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                         destination=1,
                                                                         sys_msg_title=CONST_TX_ERROR_TITLE)

                            else:
                                message = f'There has been an error while making P2P transaction please try again later'
                                await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                     destination=1,
                                                                     sys_msg_title=CONST_TX_ERROR_TITLE)
                        else:
                            message = f'You have insufficient balance! Your current wallet balance is' \
                                      f' {wallet_value / (10 ** 7)} XLM'
                            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                                 sys_msg_title=CONST_TX_ERROR_TITLE)
                    else:
                        message = f'Your wallet balance of token ***{coin.upper()}*** is 0.0000000. Before you can ' \
                                  f'make payment you need to first deposit some.'
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                             destination=1,
                                                             sys_msg_title=CONST_TX_ERROR_TITLE)
                else:

                    message = f'Coin {coin} has not been integrated yet into {self.bot.user}.'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                         destination=1,
                                                         sys_msg_title=CONST_TX_ERROR_TITLE)
            else:
                message = f'You are not allowed to send {amount} xlm to either yourself or the bot.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                     destination=1,
                                                     sys_msg_title=CONST_TX_ERROR_TITLE)
        else:
            message = 'Amount needs to be greater than 0.0000000 XLM'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=CONST_TX_ERROR_TITLE)

    @commands.group()
    @commands.check(is_public)
    @commands.check(has_wallet)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def send(self, ctx, recipient: User, amount: float, asset_code: str, *, message: str = None):
        if not re.search("[~!#$%^&*()_+{}:;\']", asset_code.lower()):
            if amount > 0:
                await self.send_impl(ctx, amount, asset_code.lower(), recipient, tx_type="public", message=message)
            else:
                message = f'Amount needs to be greater than 0.0000000  {asset_code.upper()}'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                     sys_msg_title=CONST_TX_ERROR_TITLE)
        else:
            message = 'Special characters are not allowed in token code'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=CONST_TX_ERROR_TITLE)

    @commands.group()
    @commands.check(is_public)
    @commands.check(has_wallet)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def private(self, ctx, recipient: User, amount: float, asset_code: str, *, message: str = None):
        if not re.search("[~!#$%^&*()_+{}:;\']", asset_code.lower()):
            if amount > 0:
                await self.send_impl(ctx, amount, asset_code.lower(), recipient, tx_type="private", message=message)
            else:
                message = f'Amount needs to be greater than 0.0000000 {asset_code.upper()}'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                     sys_msg_title=CONST_TX_ERROR_TITLE)
        else:
            message = 'Special characters are not allowed in token code'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=CONST_TX_ERROR_TITLE)

    @send.error
    async def send_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__System Transaction Error__'
            message = f'In order to execute P2P transaction you need to be registered into the system, and ' \
                      f'transaction request needs to be executed on one of the text public text channels ' \
                      f'on {ctx.message.guild}'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)
        elif isinstance(error, commands.BadArgument):
            title = f'__Bad Argument Provided __'
            message = f'You have provided wrong argument either for amount or than for the recipient'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)
        elif isinstance(error, AssertionError):
            title = f'__Amount Check failed __'
            message = f'You have provided wrong amount for tx value.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)
        elif isinstance(error, commands.CommandOnCooldown):
            title = f'__Command on cool-down__!'
            message = f'{error}. Please try again after {error.retry_after}s'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)

        elif isinstance(error, commands.MissingRequiredArgument):
            title = f'__Missing Required Argument Error __'
            message = f'{str(error)}'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(TransactionCommands(bot))
