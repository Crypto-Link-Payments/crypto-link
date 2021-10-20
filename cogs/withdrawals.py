from discord.ext import commands
import time
from utils.customCogChecks import has_wallet, check
from cogs.utils.monetaryConversions import convert_to_usd
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
custom_messages = CustomMessages()
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_WITHDRAWAL_ERROR = "__Withdrawal error___"


class WithdrawalCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.earnings = bot.backoffice.auto_messaging_channels["earnings"]
        self.with_channel = bot.backoffice.auto_messaging_channels["withdrawals"]
        self.help_functions = bot.backoffice.helper

    @commands.command()
    @commands.check(has_wallet)
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def withdraw(self, ctx, amount: float, asset_code: str, address: str, memo=None):
        """
        Command to initiate withdrawals
        """
        try:
            token = asset_code.lower()
            address = address.strip()
            if address != self.bot.backoffice.stellar_wallet.public_key:
                if self.help_functions.check_public_key(
                        address=address) and not self.help_functions.check_for_special_char(string=address):

                    # Checks if asset is registered
                    if [sup["assetCode"] for sup in self.bot.backoffice.token_manager.get_registered_tokens() if
                        sup["assetCode"] == token]:

                        asset_details = self.backoffice.token_manager.get_token_details_by_code(code=token)

                        minimum_withdrawal = asset_details["minimumWithdrawal"]  # Reactivate
                        micro_units = int(amount * (10 ** 7))
                        macro_units = micro_units / (10 ** 7)

                        if minimum_withdrawal < micro_units:
                            withdrawal_fee = \
                                self.backoffice.bot_manager.get_fees_by_category(key='withdrawals')["fee_list"][token]
                            fee_micro = int(withdrawal_fee * (10 ** 7))

                            # Fee deduction
                            for_owner_micro = micro_units - fee_micro  # Calculating NET withdrawal in micro
                            for_owner_macro = for_owner_micro / (10 ** 7)  # Converting NET withdrawal in normal

                            wallet_details = self.backoffice.wallet_manager.get_ticker_balance(asset_code=token,
                                                                                               user_id=ctx.message.author.id)
                            if wallet_details:
                                if wallet_details >= micro_units:
                                    message_content = f"{ctx.message.author.mention} You have requested to withdraw " \
                                                      f"***{macro_units:,.7f} {token.upper()}***. Current system withdrawal fee" \
                                                      f" is set to ***{withdrawal_fee:,.7f} {token.upper()}***. Final withdrawal " \
                                                      f"amount is  ***{for_owner_macro:,.7f} {token.upper()}***." \
                                                      f" Would you still like to withdraw? \n" \
                                                      f"Please answer either with ***yes*** or ***no***."

                                    verification = await ctx.channel.send(content=message_content)
                                    msg_usr = await self.bot.wait_for('message', check=check(ctx.message.author))

                                    if str(msg_usr.content.lower()) == 'yes':
                                        processing_msg = ':robot: Processing withdrawal request, please wait few moments....'
                                        processing_msg = await ctx.channel.send(content=processing_msg)

                                        asset_issuer = None

                                        # Get issuer if not xlm
                                        if token != 'xlm':
                                            asset_issuer = asset_details["assetIssuer"]

                                        result = self.backoffice.stellar_wallet.token_withdrawal(address=address,
                                                                                                 token=token,
                                                                                                 amount=str(
                                                                                                     for_owner_macro),
                                                                                                 asset_issuer=asset_issuer,
                                                                                                 memo=memo)

                                        if result.get("hash"):
                                            to_deduct = {f'{token}': int(micro_units) * (-1)}
                                            if self.backoffice.wallet_manager.update_user_balance_off_chain(
                                                    user_id=int(ctx.author.id),
                                                    coin_details=to_deduct):

                                                # Store withdrawal details to database
                                                result['userId'] = int(ctx.message.author.id)
                                                result["time"] = int(time.time())
                                                result["memo"] = memo
                                                result['offChainData'] = {f"{token}Fee": withdrawal_fee}

                                                # Insert in the history of withdrawals
                                                await self.backoffice.stellar_manager.insert_to_withdrawal_hist(
                                                    tx_type=1,
                                                    tx_data=result)

                                                # Update user withdrawal stats
                                                withdrawal_data = {
                                                    f"{token}.withdrawalsCount": 1,
                                                    f"{token}.totalWithdrawn": for_owner_macro,
                                                }
                                                await self.backoffice.stats_manager.update_usr_tx_stats(
                                                    user_id=ctx.message.author.id,
                                                    tx_stats_data=withdrawal_data)

                                                # Update bot stats
                                                bot_stats_data = {
                                                    "withdrawalCount": 1,
                                                    "withdrawnAmount": for_owner_macro
                                                }
                                                await self.backoffice.stats_manager.update_cl_on_chain_stats(
                                                    ticker=token,
                                                    stat_details=bot_stats_data)

                                                # Stores in earnings for tax office
                                                await self.backoffice.stats_manager.update_cl_earnings(
                                                    time=int(time.time()),
                                                    amount=fee_micro,
                                                    system='withdrawal',
                                                    token=token,
                                                    user=f'{ctx.author}',
                                                    user_id=ctx.message.author.id)

                                                self.backoffice.bot_manager.update_cl_wallet_balance(ticker=token,
                                                                                                     to_update={
                                                                                                         'balance': int(
                                                                                                             fee_micro)})

                                                # Send message to user on withdrawal
                                                await custom_messages.withdrawal_notify(ctx, withdrawal_data=result,
                                                                                        fee=f'{withdrawal_fee:,.7f} {token.upper()}',memo = memo)

                                                # # System channel notification on withdrawal processed
                                                channel_sys = self.bot.get_channel(id=int(self.with_channel))
                                                await custom_messages.withdrawal_notification_channel(ctx=ctx,
                                                                                                      channel=channel_sys,
                                                                                                      withdrawal_data=result)

                                                # Notify staff on incoming funds
                                                incoming_funds = self.bot.get_channel(
                                                    id=int(self.earnings))
                                                await custom_messages.cl_staff_incoming_funds_notification(
                                                    sys_channel=incoming_funds,
                                                    incoming_fees=f'{withdrawal_fee:,.7f} {token.upper()}')

                                                # Message to explorer
                                                if token == 'xlm':
                                                    in_dollar = convert_to_usd(amount=for_owner_macro,
                                                                               coin_name='stellar')
                                                else:
                                                    in_dollar = {"total": "$ 0.0"}

                                                # Load channels
                                                load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                                                                 self.backoffice.guild_profiles.get_all_explorer_applied_channels()]

                                                explorer_msg = f':outbox_tray: {for_owner_macro} {token.upper()} ' \
                                                               f'(${in_dollar["total"]}) on {ctx.message.guild}'
                                                await custom_messages.explorer_messages(applied_channels=load_channels,
                                                                                        message=explorer_msg)

                                        else:
                                            msg = f"It seems that there has been error while trying to withdraw. " \
                                                  f"Error: {result['error']}"
                                            await custom_messages.system_message(ctx=ctx, color_code=1,
                                                                                 message=msg,
                                                                                 destination=ctx.message.author,
                                                                                 sys_msg_title='Withdrawal error')
                                    else:
                                        msg = f"You have cancelled withdrawal request"
                                        await custom_messages.system_message(ctx=ctx, color_code=1,
                                                                             message=msg,
                                                                             destination=ctx.message.author,
                                                                             sys_msg_title='Withdrawal error')
                            else:
                                msg = f"You have not registered your wallet yet into the system or you have not" \
                                      f" deposit {token.upper()}. Withdrawal request has been canceled"
                                await custom_messages.system_message(ctx=ctx, color_code=1,
                                                                     message=msg,
                                                                     destination=ctx.message.author,
                                                                     sys_msg_title='Withdrawal error')
                        else:
                            msg = f"Minimum withdrawal amount has not been met. In order to be able to withdraw " \
                                  f"{asset_code.upper()}" \
                                  f" amount needs to be greater than {minimum_withdrawal / (10 ** 7)}"
                            await custom_messages.system_message(ctx=ctx, color_code=1,
                                                                 message=msg,
                                                                 destination=ctx.message.author,
                                                                 sys_msg_title='Withdrawal error')
                    else:
                        msg = f'{asset_code.upper()} is not supported yet on the Crypto Link system. Please ' \
                              f'try different asset. '
                        await custom_messages.system_message(ctx=ctx, color_code=1,
                                                             message=msg,
                                                             destination=ctx.message.author,
                                                             sys_msg_title='Withdrawal error')
                else:
                    msg = "Address you have specified either is not a valid public key address or it includes " \
                          "special characters. Please try again"
                    await custom_messages.system_message(ctx=ctx, color_code=1,
                                                         message=msg,
                                                         destination=ctx.message.author,
                                                         sys_msg_title='Withdrawal error')
            else:
                msg = "Withdrawing back to your account does not make any sense. Please choose different " \
                      "destination address."
                await custom_messages.system_message(ctx=ctx, color_code=1,
                                                     message=msg,
                                                     destination=ctx.message.author, sys_msg_title='Withdrawal error')
        except Exception as e:
            msg = (f'There has been an issue. Please contact support and provide them with the error {e}')
            await custom_messages.system_message(ctx=ctx, color_code=1,
                                                 message=msg,
                                                 destination=ctx.message.author, sys_msg_title='Withdrawal error')

    @withdraw.error
    async def withdrawal_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'First you need to register yourself wallet in Crypto Link system. You can do that ' \
                      f'though {self.command_string}register'
            title = f'**__Not registered__** :clipboard:'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(WithdrawalCommands(bot))
