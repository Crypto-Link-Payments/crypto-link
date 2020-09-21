import time

import discord
from discord.ext import commands

from backOffice.botStatistics import BotStatsManager
from backOffice.botWallet import BotManager
from backOffice.profileRegistrations import AccountManager
from backOffice.stellarActivityManager import StellarManager
from backOffice.stellarOnChainHandler import StellarWallet
from cogs.utils.customCogChecks import user_has_wallet, is_public
from cogs.utils.monetaryConversions import convert_to_currency
from cogs.utils.securityChecks import check_stellar_address
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
account_mng = AccountManager()
stellar_wallet = StellarWallet()
customMessages = CustomMessages()
bot_manager = BotManager()
bot_stats = BotStatsManager()
stellar = StellarManager()
d = helper.read_json_file(file_name='botSetup.json')
notf_channels = helper.read_json_file(file_name='autoMessagingChannels.json')
hot_wallets = helper.read_json_file(file_name='hotWallets.json')

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_STELLAR_WITHDRAWAL_FEE = 0.001


def check(author):
    def inner_check(message):
        if message.author.id == author.id:
            return True
        else:
            return False

    return inner_check


class WithdrawalCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(user_has_wallet)
    async def withdraw(self, ctx):
        print(f'WITHDRAW: {ctx.author} -> {ctx.message.content}')

        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.invoked_subcommand is None:
            title = '__Available withdrawal commands__'
            description = "All commands available to withdraw funds from Discord Wallet"
            list_of_values = [
                {
                    "name": f"{CONST_STELLAR_EMOJI} Withdraw Stellar (XLM) from Discord wallet {CONST_STELLAR_EMOJI}",
                    "value": f"{d['command']}withdraw xlm <amount> <destination address>\n"
                             f"\nexample:\n"
                             f"```!withdraw xlm 100 GBAGTMSNZLAJJWTBAJM2EVN5BQO7YTQLYCMQWRZT2JLKKXP3OMQ36IK7```"}]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                               destination=1)

    @withdraw.command()
    @commands.check(is_public)
    @commands.check(user_has_wallet)
    async def xlm(self, ctx, amount: float, address: str):
        """
        Initiates withdrawal on Stellar chain
        :param ctx: Discord Context
        :param amount: Amount in Stellar
        :param address: Destination address of withdrawal
        :return:
        """
        try:
            await ctx.message.delete()
        except Exception:
            pass

        print(f'WITHDRAW XLM  : {ctx.author} -> {ctx.message.content}')

        # TODO check fees and so on
        stellar_fee = bot_manager.get_fees_by_category(key='xlm')['fee']
        fee_in_xlm = convert_to_currency(amount=stellar_fee, coin_name='stellar')
        fee_in_stroops = int(fee_in_xlm['total'] * (10 ** 7))
        channel_id = notf_channels["stellar"]
        channel = self.bot.get_channel(
            id=int(channel_id))  # Get the channel wer notification onw ithdrawal will be sent

        if check_stellar_address(address=address):
            stroops = (int(amount * (10 ** 7)))
            if stroops >= 300000000:
                final_stroop = stroops + fee_in_stroops
                # Check user balance
                wallet_details = stellar.get_stellar_wallet_data_by_discord_id(discord_id=ctx.message.author.id)
                if wallet_details['balance'] >= final_stroop:
                    xlm_with_amount = stroops / 10000000

                    # Get withdrawal fee
                    convert_fee = convert_to_currency(fee_in_stroops, coin_name='stellar')

                    # Confirmation message
                    message_content = f"{ctx.message.author.mention} Current withdrawal fee which will be appended to your withdrawal amout is " \
                                      f"{round(fee_in_xlm['total'], 7)} {CONST_STELLAR_EMOJI} (${stellar_fee}, Rate:{round(fee_in_xlm['usd'], 4)})." \
                                      f"Are you still willing to withdraw? answer with ***yes*** or ***no***"

                    verification = await ctx.channel.send(content=message_content)
                    msg_usr = await self.bot.wait_for('message', check=check(ctx.message.author))

                    if isinstance(ctx.message.channel, discord.TextChannel):
                        await ctx.channel.delete_messages([verification, msg_usr])
                    else:
                        pass

                    if str(msg_usr.content.lower()) == 'yes':
                        processing_msg = f'Processing withdrawal request, please wait few moments....'
                        processing_msg = await ctx.channel.send(content=processing_msg)

                        # Update stellar balance discord id
                        if stellar.update_stellar_balance_by_discord_id(discord_id=ctx.message.author.id,
                                                                        stroops=final_stroop,
                                                                        direction=2):
                            # Initiate on chain withdrawal
                            data = stellar_wallet.withdraw(address=address,
                                                           xlm_amount=str(xlm_with_amount))
                            # data = await stellar_wallet.as_withdraw(address=address,
                            #                                         xlm_amount=str(xlm_with_amount))

                            if data:
                                data_new = {
                                    "time": time.time(),
                                    "destination": address,
                                    "userId": int(ctx.message.author.id),
                                    "amount": f'{xlm_with_amount:.7f}',
                                    "fee": fee_in_stroops,
                                    "stroops": stroops,
                                    "serverId": int(ctx.message.guild.id),
                                    "serverName": f'{ctx.message.guild}',
                                    "paymentId": wallet_details['depositId'],
                                    "explorer": data['explorer'],
                                    "hash": data["hash"]
                                }

                                if stellar.stellar_withdrawal_history(type=1, data=data_new):
                                    await customMessages.coin_withdrawal_notification(coin='XLM',
                                                                                      recipient=ctx.message.author,
                                                                                      hash=data['hash'],
                                                                                      amount=data_new["amount"],
                                                                                      fee=f"${stellar_fee}, Rate:{round(fee_in_xlm['usd'], 4)}",
                                                                                      destination=data['destination'],
                                                                                      ledger=data['ledger'],
                                                                                      link=data['explorer'],
                                                                                      thumbnail=self.bot.user.avatar_url)
                                    try:
                                        # create withdrawal notifcaiton for channel
                                        notify = discord.Embed(title='Stellar Withdrawal Notification',
                                                               description='Withdrawal has been processed',
                                                               colour=discord.Colour.gold())
                                        notify.add_field(name='Guild',
                                                         value=f'{ctx.message.guild} ID; {ctx.message.guild.id}',
                                                         inline=False)
                                        notify.add_field(name='User details',
                                                         value=f'{ctx.message.author} \nID; {ctx.message.author.id}',
                                                         inline=False)
                                        notify.add_field(name='Withdrawal details',
                                                         value=f'Time: {data_new["time"]}\n'
                                                               f'Destination: {data_new["destination"]}\n'
                                                               f'Amount: {data_new["amount"]} {CONST_STELLAR_EMOJI}',
                                                         inline=False)
                                        await channel.send(embed=notify)

                                    except Exception as e:
                                        print('sending to channel error')
                                        print(e)
                                        return

                                    if bot_stats.update_chain_activity_stats(type_of='withdrawal', ticker='stellar',
                                                                             amount=stroops):
                                        pass
                                    else:
                                        print('Could not update stellar withdrawal stats ')

                                else:
                                    print('Could not store withdrawal to history')

                                # UPDATE BOT WALLET

                                if bot_manager.update_lpi_wallet_balance(amount=fee_in_stroops, wallet='xlm',
                                                                         direction=1):
                                    notify = discord.Embed(title='Bot Stellar Wallet Activity',
                                                           description='Bot Wallet has been credited because user '
                                                                       'has initiated on-chainw withdrawal',
                                                           color=discord.Colour.blurple())
                                    notify.add_field(name='Value',
                                                     value=f'{fee_in_stroops / 10000000}{CONST_STELLAR_EMOJI}')
                                    await channel.send(embed=notify)

                            else:
                                title = '__Withdrawal error___'
                                message = f'Funds could not be withdrawn at this point. Please try again later.'
                                await customMessages.system_message(ctx=ctx, color_code=1, message=message,
                                                                    destination=0,
                                                                    sys_msg_title=title)
                                stellar.update_stellar_balance_by_discord_id(discord_id=ctx.message.author.id,
                                                                             stroops=final_stroop,
                                                                             direction=1)
                        else:
                            title = '__Withdrawal error___'
                            message = f'Funds could not be withdrawn at this point. Please try again later.'
                            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                                sys_msg_title=title)
                        await ctx.channel.delete_messages([processing_msg])
                    else:
                        title = '__Withdrawal request canceled___'
                        message = f'You have cancelled withdrawal request of {round(xlm_with_amount, 7)}'
                        await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                            sys_msg_title=title)

                else:
                    title = '__Insufficient balance___'
                    message = f'Amount you are willing to withdraw is greater than your current wallet balance.\n' \
                              f'Wallet balance: {wallet_details["balance"] / 10000000} Stellar Balance {CONST_STELLAR_EMOJI}'
                    await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                        sys_msg_title=title)

            else:
                title = '__Amount error___'
                message = f'Wrong amount for withdrawal provided. Amount needs to be greater than 30 XLM'
                await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                    sys_msg_title=title)
        else:
            title = 'Withdrawal address error'
            message = f'{address} is not valis for Stellar. Please reached the address and try again. ' \
                      f'If issue persists\n please contact dev team.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)

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
            message = f'You are either not registered in the system or you have tried to use command over DM with the ' \
                      f'system itself. Head to one of the channels on community where system is accessible.'
            title = f'**__Not registered__** :clipboard:'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)
        elif isinstance(error, commands.MissingRequiredArgument):
            message = f'**You have not provided one of the required arguments for the command to work. Command structure' \
                      f' to initiate withdrawal is {d["command"]}withdraw stellar <amount> <address>'
            title = f'**__Missing required argument__** :clipboard:'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)
        elif isinstance(error, commands.BadArgument):
            message = f'**The arguments you have provided do not fit the command style. Be sure to specify appropriate' \
                      f' amount and address format.'
            title = f'**__Bad arguments provided__** :clipboard:'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)
        return


def setup(bot):
    bot.add_cog(WithdrawalCommands(bot))
