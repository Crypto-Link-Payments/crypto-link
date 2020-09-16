"""SCRIPT: Dealing with the corporate balance """

import time

import discord
from colorama import Fore
from discord.ext import commands
from datetime import datetime

from backOffice.botWallet import BotManager
from backOffice.corpHistory import CorporateHistoryManager
from backOffice.profileRegistrations import AccountManager
from backOffice.stellarActivityManager import StellarManager
from cogs.utils.monetaryConversions import get_decimal_point, get_normal
from backOffice.botStatistics import BotStatsManager
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

bot_stats = BotStatsManager()
helper = Helpers()
bot_manager = BotManager()
account_mng = AccountManager()
stellar = StellarManager()
corporate_hist_mng = CorporateHistoryManager()
customMessages = CustomMessages()
d = helper.read_json_file(file_name='botSetup.json')
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'


def is_one_of_gods(ctx):
    list_of_gods = [d['ownerId'], d['creator']]
    return [god for god in list_of_gods if god == ctx.message.author.id]


class BotWalletCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_transfer_notification(self, ctx, member, channel_id: int, normal_amount, emoji: str,
                                         chain_name: str):
        """
        Function send information to corporate channel on corp wallet activity
        :param ctx: Discord Context
        :param member: Member to where funds have been transfered
        :param channel_id: channel ID applied for notifcations
        :param normal_amount: converted amount from atomic
        :param emoji: emoji identification for the currency
        :param chain_name: name of the chain used in transactions
        :return: discord.Embed
        """
        stellar_notify_channel = self.bot.get_channel(id=int(channel_id))
        corp_channel = discord.Embed(
            title=f'__{emoji} Corporate account transfer activity__ {emoji}',
            description=f'Notification on corporate funds transfer activity on {chain_name}',
            colour=discord.Colour.greyple())
        corp_channel.add_field(name='Author',
                               value=f'{ctx.message.author}',
                               inline=False)
        corp_channel.add_field(name='Destination',
                               value=f'{member}')
        corp_channel.add_field(name='Amount',
                               value=f'{normal_amount} {emoji}')
        await stellar_notify_channel.send(embed=corp_channel)

    @commands.command()
    @commands.check(is_one_of_gods)
    async def check_corp_balance(self, ctx):
        data = bot_manager.get_bot_wallets_balance()
        values = discord.Embed(title="Balance of Launch Pad Investment Corporate Wallet",
                               description="Current state of all bot wallets",
                               color=discord.Colour.blurple())
        for bal in data:
            ticker = bal['ticker']
            decimal = get_decimal_point(ticker)
            conversion = int(bal["balance"])
            conversion = get_normal(str(conversion), decimal_point=decimal)
            values.add_field(name=ticker.upper(),
                             value=f'{conversion}',
                             inline=False)
        await ctx.channel.send(embed=values, delete_after=100)

    @commands.group()
    @commands.check(is_one_of_gods)
    async def transfer(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.invoked_subcommand is None:
            title = '__Available Commands for Corp Wallet Transfers__'
            description = "All commands to operate with Launch Pad Corporate wallet"
            list_of_values = [
                {"name": "Check Corporate Balance", "value": f"{d['command']}check_corp_balance"},
                {"name": "Transfer total Stellar balance from Corp to god member",
                 "value": f"{d['command']}transfer sweep_xlm <discord.Member>"}]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values)

    @transfer.command()
    @commands.check(is_one_of_gods)
    async def sweep_xlm(self, ctx):
        author = ctx.message.author.id

        balance = int(bot_manager.get_bot_wallet_balance_by_ticker(ticker='xlm'))
        if balance > 0:  # Check if balance greater than -
            # Checks if recipient exists
            if not account_mng.check_user_existence(user_id=ctx.message.author.id):
                account_mng.register_user(discord_id=ctx.message.author.id, discord_username=f'{ctx.message.author}')

            if stellar.update_stellar_balance_by_discord_id(discord_id=ctx.message.author.id,
                                                            stroops=int(balance), direction=1):
                # Deduct the balance from the community balance
                if bot_manager.update_lpi_wallet_balance(amount=balance, wallet="xlm", direction=2):
                    # Store in history and send notifications to owner and to channel
                    dec_point = get_decimal_point(symbol='xlm')
                    normal_amount = get_normal(str(balance), decimal_point=dec_point)

                    # Store transaction details into corp history
                    if corporate_hist_mng.store_transfer_from_corp_wallet(time_utc=int(time.time()), author=author,
                                                                          destination=int(ctx.message.author.id),
                                                                          amount_atomic=balance, amount=normal_amount,
                                                                          currency='xlm'):
                        pass
                    else:
                        print(Fore.RED + "could not store in history")
                        pass

                    # notification to corp account discord channel
                    stellar_channel_id = auto_channels['stellar']
                    await self.send_transfer_notification(ctx=ctx, member=ctx.message.author,
                                                          channel_id=stellar_channel_id,
                                                          normal_amount=normal_amount, emoji=CONST_STELLAR_EMOJI,
                                                          chain_name='Stellar Chain')

                else:
                    # Revert the user balance if community balance can not be updated
                    stellar.update_stellar_balance_by_discord_id(discord_id=ctx.message.author.id,
                                                                 stroops=int(balance), direction=2)

                    title = '__Corporate Transfer Error__'
                    message = f"Stellar funds could not be deducted from corporate account. Please try again later"
                    await customMessages.system_message(ctx, color_code=1, message=message, destination=0,
                                                        sys_msg_title=title)
            else:
                title = '__Corporate Transfer Error__'
                message = f"Stellar funds could not be moved from corporate account to {ctx.message.author}." \
                          f"Please try again later "
                await customMessages.system_message(ctx, color_code=1, message=message, destination=0,
                                                    sys_msg_title=title)
        else:
            title = '__Corporate Transfer Error__'
            message = f"You can not transfer XLM from corporate account to {ctx.message.author} " \
                      f"because the corporate wallet balance" \
                      f"is 0 {CONST_STELLAR_EMOJI}"
            await customMessages.system_message(ctx, color_code=1, message=message, destination=0, sys_msg_title=title)

    @commands.command()
    @commands.check(is_one_of_gods)
    async def stats(self, ctx):
        data = bot_stats.get_all_stats()
        stats_embed = discord.Embed(title='__Global Crypto Link Stats__',
                                    colour=discord.Color.green(),
                                    timestamp=datetime.utcnow())
        stats_embed.add_field(name='On-Chain Stellar Stats',
                              value=f"Deposits:{data['xlm']['onChain']['depositCount']}\n"
                                    f"Total dep. amount: {int(data['xlm']['onChain']['depositAmount']) / 10000000} <:stelaremoji:684676687425961994>\n"
                                    f"=========================\n"
                                    f"Withdrawals: {data['xlm']['onChain']['withdrawalCount']}\n"
                                    f"Total with. amount: {int(data['xlm']['onChain']['withdrawalAmount']) / 10000000} <:stelaremoji:684676687425961994>",
                              inline=False)
        stats_embed.add_field(name='Off-Chain Stellar Stats',
                              value=f"P2P Tx Count:{data['xlm']['ofChain']['transactionCount']}\n"
                                    f"Total P2P Transfered: {int(data['xlm']['ofChain']['offChainMoved']) / 10000000} <:stelaremoji:684676687425961994>",
                              inline=False)


        await ctx.author.send(embed=stats_embed)
        guilds = await self.bot.fetch_guilds(limit=150).flatten()
        reach = len(self.bot.users)
        world = discord.Embed(title='__Crypto Link Reach__',
                              colour=discord.Colour.magenta(),
                              timestamp=datetime.utcnow())
        world.add_field(name='Guild reach',
                        value=f'{len(guilds)}',
                        inline=False)
        world.add_field(name='Member reach',
                        value=f'{reach}',
                        inline=False)
        await ctx.author.send(embed=world)


def setup(bot):
    bot.add_cog(BotWalletCommands(bot))
