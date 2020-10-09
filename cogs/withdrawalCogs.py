import time
import re
from discord.ext import commands
from discord import TextChannel

from cogs.utils.customCogChecks import user_has_wallet
from cogs.utils.monetaryConversions import convert_to_usd
from cogs.utils.securityChecks import check_stellar_address
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
custom_messages = CustomMessages()
hot_wallets = helper.read_json_file(file_name='hotWallets.json')
notify_channel = helper.read_json_file(file_name='autoMessagingChannels.json')
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_WITHDRAWAL_ERROR = "__Withdrawal error___"
integrated_coins = helper.read_json_file(file_name='integratedCoins.json')


def check(author):
    def inner_check(message):
        """
        Check for answering the verification message on withdrawal. Author origin
        """
        if message.author.id == author.id:
            return True
        else:
            return False

    return inner_check


class WithdrawalCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.list_of_coins = list(integrated_coins.keys())

    @commands.group()
    @commands.check(user_has_wallet)
    async def withdraw(self, ctx):
        print(f'WITHDRAW: {ctx.author} -> {ctx.message.content}')
        if ctx.invoked_subcommand is None:
            title = '__Available withdrawal commands__'
            description = "All commands available to withdraw funds from Discord Wallet"
            list_of_values = [
                {"name": f"{CONST_STELLAR_EMOJI} Withdraw Stellar (XLM) from Discord wallet {CONST_STELLAR_EMOJI}",
                 "value": f"{self.command_string}withdraw xlm <amount> <destination address>\n"
                          f"\nexample:\n"
                          f"```!withdraw xlm 100 GBAGTMSNZLAJJWTBAJM2EVN5BQO7YTQLYCMQWRZT2JLKKXP3OMQ36IK7```"},
                {"name": f" Withdraw Tokens",
                 "value": f"{self.command_string}withdraw <ticker> <amount> <destination address>\n"
                          f"\nexample:\n"
                          f"```!withdraw clt 100 GBAGTMSNZLAJJWTBAJM2EVN5BQO7YTQLYCMQWRZT2JLKKXP3OMQ36IK7```"}]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1)

    @withdraw.command()
    @commands.check(user_has_wallet)
    async def token(self, ctx, ticker: str, withdrawal_amount: float, address: str):
        token = ticker.lower()
        # check strings, stellar address and token integration status
        if not re.search("[~!#$%^&*()_+{}:;\']", token) and token in self.list_of_coins and check_stellar_address(
                address=address):

            # get and convert coin withdrawal fee from major to atomic
            all_coin_fees = self.backoffice.bot_manager.get_fees_by_category(all_fees=False, key='withdrawals')[
                'fee_list']

            # Stellar details
            stellar_details = integrated_coins['xlm']
            stellar_fee = all_coin_fees['xlm']

            # Token details
            token_emoji = integrated_coins[token]['emoji']
            token_name = integrated_coins[token]['name']
            token_decimal = integrated_coins[token]['decimal']
            token_minimum = integrated_coins[token]['minimumWithdrawal']

            token_withdrawal_amount_atomic = int(withdrawal_amount * (10 ** int(token_decimal)))
            token_fee = all_coin_fees[token]
            token_fee_atomic = (int(token_fee * (10 ** int(token_decimal))))
            token_major = (int(token_withdrawal_amount_atomic / (10 ** int(token_decimal))))

            # User balances
            user_balances = self.backoffice.wallet_manager.get_balances(user_id=ctx.message.author.id)
            user_stellar_balance = user_balances['xlm']
            stellar_balance_major = (int(user_stellar_balance / (10 ** int(token_decimal))))
            user_token_balance = user_balances[token]
            user_token_balance_major = (int(user_token_balance / (10 ** int(token_decimal))))

            # end values
            total_token_to_withdraw = token_fee_atomic + token_withdrawal_amount_atomic
            total_token_to_withdraw_major = (int(total_token_to_withdraw / (10 ** int(token_decimal))))
            total_stellar_to_withdraw = int(stellar_fee * (10 ** int(int(stellar_details["decimal"]))))
            total_stellar_to_withdraw_major = (int(total_stellar_to_withdraw / (10 ** int(token_decimal))))

            # Check if minimum is met
            if total_token_to_withdraw >= token_minimum:
                # Check if totals are met with fees compared to user wallet
                if user_stellar_balance >= total_stellar_to_withdraw and user_token_balance >= total_token_to_withdraw:

                    # Ask for verification
                    message_content = f"{ctx.message.author.mention} fees for withdrawal request are:\n" \
                                      f"***XLM***: {stellar_fee} {CONST_STELLAR_EMOJI}\n" \
                                      f"***{token.upper()}***: {token_fee}{token_emoji}\n" \
                                      f"Are you still willing to withdraw and pay the fess? answer with ***yes*** " \
                                      f"or ***no***"

                    verification = await ctx.channel.send(content=message_content)
                    msg_usr = await self.bot.wait_for('message', check=check(ctx.message.author))

                    # If public text channel than delete responses otherwise pass since bot cant delete on private
                    if isinstance(ctx.message.channel, TextChannel):
                        await ctx.channel.delete_messages([verification, msg_usr])

                    # Check verification
                    if str(msg_usr.content.lower()) == 'yes':
                        processing_msg = 'Processing withdrawal request, please wait few moments....'
                        await ctx.channel.send(processing_msg)

                        to_deduct = {
                            "xlm": int(total_stellar_to_withdraw) * (-1),
                            f"{token}": int(total_token_to_withdraw) * (-1)
                        }

                        # Withdraw balance from user wallet
                        if self.backoffice.wallet_manager.update_user_balance_off_chain(user_id=ctx.message.author.id,
                                                                                        coin_details=to_deduct):
                            bot_append = {
                                "xlm": {"balance": int(total_stellar_to_withdraw)},
                                f'{token}': {"balance": int(token_fee_atomic)}
                            }

                            # Give fees to the bot
                            if self.backoffice.bot_manager.update_lpi_wallet_balance_multi(fees_data=bot_append,
                                                                                           token=token):

                                # Initiate on chain withdrawal from hot wallet
                                result = self.backoffice.stellar_wallet.token_withdrawal(address=address,
                                                                                         token=ticker.upper(),
                                                                                         amount=f'{withdrawal_amount}')

                                # Check result of the on-chain withdrawal
                                if result.get("hash"):
                                    await custom_messages.withdrawal_notify(ctx, withdrawal_data=result,
                                                                            fee=f'{stellar_fee} XLM and {token_fee}'
                                                                                f' {ticker.upper()}')

                                    # Store withdrawal details to database
                                    result['userId'] = int(ctx.message.author.id)
                                    result["time"] = int(time.time())
                                    result['offChainData'] = {"xlmFee": stellar_fee,
                                                              f"tokenFee": token_fee}

                                    await self.backoffice.stellar_manager.insert_to_withdrawal_hist(tx_type=1,
                                                                                                    tx_data=result)

                                    # Update CL on chain stats
                                    await self.backoffice.stats_manager.update_cl_on_chain_stats(ticker=token,
                                                                                                 stat_details={
                                                                                                     "withdrawalCount": 1,
                                                                                                     "withdrawnAmount":
                                                                                                         token_major})
                                    # Update user profile stats
                                    withdrawal_data = {
                                        f"{token}.withdrawalsCount": 1,
                                        f"{token}.totalWithdrawn": token_major,
                                    }
                                    await self.backoffice.stats_manager.update_usr_tx_stats(
                                        user_id=ctx.message.author.id,
                                        tx_stats_data=withdrawal_data)

                                    # Message to explorer
                                    load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                                                     self.backoffice.guild_profiles.get_all_explorer_applied_channels()]
                                    explorer_msg = f':outbox_tray: {token_name} amount {token_major} {token_emoji}  ' \
                                                   f'withdrawn'
                                    await custom_messages.explorer_messages(applied_channels=load_channels,
                                                                            message=explorer_msg, tx_type='withdrawal',
                                                                            on_chain=True)

                                    # System channel notification on withdrawal
                                    channel_id = notify_channel["stellar"]
                                    channel_sys = self.bot.get_channel(
                                        id=int(
                                            channel_id))  # Get the channel wer notification on withdrawal will be sent

                                    # Send withdrawal notification to CL system
                                    await custom_messages.withdrawal_notification_channel(ctx=ctx,
                                                                                          channel=channel_sys,
                                                                                          withdrawal_data=result)

                                    # Sys notification of incoming funds to wallet
                                    await custom_messages.cl_staff_incoming_funds_notification(sys_channel=channel_sys,
                                                                                               incoming_fees=f'{stellar_fee} {CONST_STELLAR_EMOJI}\n'
                                                                                                             f'{token_fee} {token_emoji} ({token.upper()})')

                                elif result.get("error"):
                                    # revert user balance
                                    to_return = {
                                        "xlm": int(total_stellar_to_withdraw),
                                        f"{token}": int(total_token_to_withdraw)
                                    }

                                    self.backoffice.wallet_manager.update_user_balance_off_chain(
                                        user_id=ctx.message.author.id,
                                        coin_details=to_return)

                                    # Deduct appended fees from Bot wallet due to failed transaction
                                    bot_deduct = {
                                        "xlm": {"balance": int(total_stellar_to_withdraw) * (-1)},
                                        f'{token}': {"balance": int(token_fee_atomic) * (-1)}
                                    }

                                    self.backoffice.bot_manager.update_lpi_wallet_balance_multi(fees_data=bot_deduct,
                                                                                                token=token)

                                    await custom_messages.system_message(ctx, color_code=1, message=result['error'],
                                                                         destination=ctx.message.author,
                                                                         sys_msg_title=CONST_STELLAR_EMOJI)
                            else:
                                to_append = {
                                    "xlm": int(total_stellar_to_withdraw),
                                    f"{token}": int(total_token_to_withdraw)
                                }
                                self.backoffice.wallet_manager.update_user_balance_off_chain(
                                    user_id=ctx.message.author.id,
                                    coin_details=to_append)

                                message = f'There has been system issue, please try again later'
                                await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                     destination=0,
                                                                     sys_msg_title=CONST_WITHDRAWAL_ERROR)
                        else:
                            message = f'There has been system issue, please try again later'
                            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                                 sys_msg_title=CONST_WITHDRAWAL_ERROR)
                    else:
                        message = f'You have cancelled withdrawal request'
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                             sys_msg_title=CONST_WITHDRAWAL_ERROR)

                else:
                    message = f"You have insufficient balances:\n" \
                              f"***XLM***: Balance {stellar_balance_major}{CONST_STELLAR_EMOJI} required:" \
                              f" {total_stellar_to_withdraw_major}{CONST_STELLAR_EMOJI}\n" \
                              f"***{token.upper()}***: Balance {user_token_balance_major}{token_emoji} required:" \
                              f" {total_token_to_withdraw_major}{token_emoji}"
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                         sys_msg_title=CONST_WITHDRAWAL_ERROR)
            else:
                message = f'Minimum withdrawal requirements not met:\n' \
                          f'You requested to withdraw {token_major}{token_emoji} however minimum is set to' \
                          f' {token_minimum / (10 ** token_decimal)}{token_emoji}.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=CONST_WITHDRAWAL_ERROR)
        else:
            message = f'In order to be eligible to withdraw following conditions need to be met:\n' \
                      f'> :one: Token needs to be listed on Crypto Link\n' \
                      f'> :two: Destination address needs to be valid Stellar Public Key'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_WITHDRAWAL_ERROR)

    @withdraw.command()
    @commands.check(user_has_wallet)
    async def xlm(self, ctx, amount: float, address: str):
        """
        Initiates withdrawal on Stellar chain
        :param ctx: Discord Context
        :param amount: Amount in Stellar
        :param address: Destination address of withdrawal
        :return:
        """
        print(f'WITHDRAW XLM  : {ctx.author} -> {ctx.message.content}')
        stellar_fee = self.backoffice.bot_manager.get_fees_by_category(all_fees=False, key='withdrawals')['fee_list'][
            'xlm']
        fee_in_stroops = int(stellar_fee * (10 ** 7))

        # Get stellar details from json
        xlm_decimal = integrated_coins['xlm']['decimal']
        xlm_minimum = integrated_coins['xlm']['minimumWithdrawal']

        if check_stellar_address(address=address):
            stroops = (int(amount * (10 ** xlm_decimal)))
            if stroops >= xlm_minimum:
                final_stroop = stroops + fee_in_stroops
                # Check user balance

                wallet_details = self.backoffice.wallet_manager.get_ticker_balance(ticker='xlm',
                                                                                   user_id=ctx.message.author.id)

                if wallet_details >= final_stroop:
                    xlm_with_amount = stroops / 10000000

                    # Confirmation message
                    message_content = f"{ctx.message.author.mention} Current withdrawal fee which will be appended " \
                                      f"to your withdrawal amount is " \
                                      f"{stellar_fee} {CONST_STELLAR_EMOJI}\n" \
                                      f"Are you still willing to withdraw? answer with ***yes*** or ***no***"

                    verification = await ctx.channel.send(content=message_content)
                    msg_usr = await self.bot.wait_for('message', check=check(ctx.message.author))


                    if str(msg_usr.content.lower()) == 'yes':
                        processing_msg = 'Processing withdrawal request, please wait few moments....'
                        processing_msg = await ctx.channel.send(content=processing_msg)

                        to_deduct = {
                            "xlm": int(final_stroop) * (-1)
                        }

                        # Withdraw balance from user wallet
                        if self.backoffice.wallet_manager.update_user_balance_off_chain(user_id=ctx.message.author.id,
                                                                                        coin_details=to_deduct):

                            # Initiate on chain withdrawal
                            result = self.backoffice.stellar_wallet.token_withdrawal(address=address, token='xlm',
                                                                                     amount=str(xlm_with_amount))

                            if result.get("hash"):
                                # Store withdrawal details to database
                                result['userId'] = int(ctx.message.author.id)
                                result["time"] = int(time.time())
                                result['offChainData'] = {"xlmFee": stellar_fee}

                                # Insert in the history of withdrawals
                                await self.backoffice.stellar_manager.insert_to_withdrawal_hist(tx_type=1,
                                                                                                tx_data=result)

                                # Send message to user on withdrawal
                                await custom_messages.withdrawal_notify(ctx, withdrawal_data=result,
                                                                        fee=f'{stellar_fee} XLM and')

                                # System channel notification on withdrawal
                                channel_id = notify_channel["stellar"]
                                channel_sys = self.bot.get_channel(
                                    id=int(channel_id))  # Get the channel wer notification on withdrawal will be sent

                                # Send withdrawal notification to CL system
                                await custom_messages.withdrawal_notification_channel(ctx=ctx,
                                                                                      channel=channel_sys,
                                                                                      withdrawal_data=result)

                                if self.backoffice.bot_manager.update_lpi_wallet_balance(ticker='xlm',
                                                                                         to_update={'balance': int(
                                                                                             fee_in_stroops)}):
                                    await custom_messages.cl_staff_incoming_funds_notification(sys_channel=channel_sys,
                                                                                               incoming_fees=f'{stellar_fee} {CONST_STELLAR_EMOJI}')

                                    # Update user withdrawal stats
                                    withdrawal_data = {
                                        "xlm.withdrawalsCount": 1,
                                        "xlm.totalWithdrawn": round(stroops / 10000000, 7),
                                    }
                                    await self.backoffice.stats_manager.update_usr_tx_stats(
                                        user_id=ctx.message.author.id,
                                        tx_stats_data=withdrawal_data)

                                    # Update bot stats
                                    bot_stats_data = {
                                        "withdrawalCount": 1,
                                        "withdrawnAmount": round(stroops / 10000000, 7)
                                    }
                                    await self.backoffice.stats_manager.update_cl_on_chain_stats(ticker='xlm',
                                                                                                 stat_details=bot_stats_data)
                                    # Message to explorer
                                    in_dollar = convert_to_usd(amount=xlm_with_amount, coin_name='stellar')
                                    load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                                                     self.backoffice.guild_profiles.get_all_explorer_applied_channels()]
                                    explorer_msg = f':outbox_tray: {xlm_with_amount} {CONST_STELLAR_EMOJI} ' \
                                                   f'(${in_dollar["total"]}) on {ctx.message.guild}'
                                    await custom_messages.explorer_messages(applied_channels=load_channels,
                                                                            message=explorer_msg, tx_type='withdrawal',
                                                                            on_chain=True)

                            else:
                                message = 'Funds could not be withdrawn at this point. Please try again later.'
                                # return user funds to off-chain wallet
                                to_append = {
                                    "xlm": int(final_stroop)
                                }
                                self.backoffice.wallet_manager.update_user_balance_off_chain(
                                    user_id=ctx.message.author.id,
                                    coin_details=to_append)
                                await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                     destination=0,
                                                                     sys_msg_title=CONST_WITHDRAWAL_ERROR)
                        else:
                            message = 'Funds could not be withdrawn at this point. Please try again later.'
                            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                                 sys_msg_title=CONST_WITHDRAWAL_ERROR)

                        if isinstance(ctx.message.channel, TextChannel):
                            await ctx.channel.delete_messages([processing_msg])

                    else:
                        message = f'You have cancelled withdrawal request of {round(xlm_with_amount, 7)}'
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                             sys_msg_title=CONST_WITHDRAWAL_ERROR)

                    if isinstance(ctx.message.channel, TextChannel):
                        await ctx.channel.delete_messages([verification, msg_usr])


                else:
                    message = f'Amount you are willing to withdraw is greater than your current wallet balance.\n' \
                              f'Wallet balance: {wallet_details["balance"] / 10000000} {CONST_STELLAR_EMOJI}'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                         sys_msg_title=CONST_WITHDRAWAL_ERROR)

            else:
                message = f'Minimum amount to withdraw is set currently to {xlm_minimum} {CONST_STELLAR_EMOJI}'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=CONST_WITHDRAWAL_ERROR)
        else:
            message = f'{address} is not valid Stellar address. Please verify the address and try again. ' \
                      f'If issue persists\n please contact dev team.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_WITHDRAWAL_ERROR)

    @xlm.error
    async def stellar_withdrawal_error(self, ctx, error):
        """
        Custom error handlers for stellar withdrawal command
        :param ctx:
        :param error:
        :return:
        """
        print(f'ERR WITHDRAW XLM TRIGGERED  : {error}')

        if isinstance(error, commands.CheckFailure):
            message = f'You are either not registered in the system or you have tried to use command' \
                      f' over DM with the system itself. Head to one of the channels on community' \
                      f' where system is accessible.'
            title = f'**__Not registered__** :clipboard:'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)
        elif isinstance(error, commands.MissingRequiredArgument):
            message = f'**You have not provided one of the required arguments for the command ' \
                      f'to work. Command structure ' \
                      f'to initiate withdrawal is {self.command_string}withdraw stellar <amount> <address>'
            title = f'**__Missing required argument__** :clipboard:'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)
        elif isinstance(error, commands.BadArgument):
            message = f'**The arguments you have provided do not fit the command style.' \
                      f' Be sure to specify appropriate' \
                      f' amount and address format.'
            title = f'**__Bad arguments provided__** :clipboard:'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(WithdrawalCommands(bot))
