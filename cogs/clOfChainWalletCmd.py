"""SCRIPT: Dealing with the corporate balance """

import time
from datetime import datetime

from discord import Embed
import discord
from discord.ext import commands

from backOffice.botStatistics import BotStatsManager
from backOffice.botWallet import BotManager
from backOffice.corpHistory import CorporateHistoryManager
from backOffice.profileRegistrations import AccountManager
from backOffice.stellarActivityManager import StellarManager
from cogs.utils.customCogChecks import is_one_of_gods
from cogs.utils.monetaryConversions import get_decimal_point, get_normal
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
CONST_CORP_TRANSFER_ERROR_TITLE = '__Corporate Transfer Error__'


class BotWalletCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_transfer_notification(self, ctx, member, channel_id: int, normal_amount, emoji: str,
                                         chain_name: str):
        """
        Function send information to corporate channel on corp wallet activity
        :param ctx: Discord Context
        :param member: Member to where funds have been transferred
        :param channel_id: channel ID applied for notifications
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

    @commands.group()
    @commands.check(is_one_of_gods)
    async def cl(self, ctx):
        """
        Entry point for cl sub commands
        """
        print(f'CL : {ctx.author} -> {ctx.message.content}')
        if ctx.invoked_subcommand is None:
            title = '__Available Commands for Corp Wallet Transfers__'
            description = "All commands to operate with Crypto Link Corporate Wallet"
            list_of_values = [
                {"name": "Check Corporate Balance", "value": f"{d['command']}cl balance"},
                {"name": "Withdrawing XLM from Corp to personal",
                 "value": f"{d['command']}cl sweep"},
                {"name": "Statistics of crypto link system",
                 "value": f"{d['command']}cl stats"}
            ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                               destination=ctx.message.author)

    @cl.command()
    @commands.check(is_one_of_gods)
    async def balance(self, ctx):
        """
        Check the off-chain balance status of Crypto Link system
        """
        print(f'CL BALANCE : {ctx.author} -> {ctx.message.content}')
        data = bot_manager.get_bot_wallets_balance()
        values = discord.Embed(title="Balance of Crypto-Link Off chain balance",
                               description="Current state of Crypto Link Lumen wallet",
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

    @cl.command()
    @commands.check(is_one_of_gods)
    async def sweep(self, ctx):
        """
        Transfer funds from Crypto Link to develop wallet
        """
        print(f'CL SWEEP  : {ctx.author} -> {ctx.message.content}')
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

                    # Store into the history of corporate transfers
                    corporate_hist_mng.store_transfer_from_corp_wallet(time_utc=int(time.time()),
                                                                       author=f'{ctx.message.author}',
                                                                       destination=int(ctx.message.author.id),
                                                                       amount_atomic=balance, amount=normal_amount,
                                                                       currency='xlm')

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

                    message = f"Stellar funds could not be deducted from corporate account. Please try again later"
                    await customMessages.system_message(ctx, color_code=1, message=message, destination=0,
                                                        sys_msg_title=CONST_CORP_TRANSFER_ERROR_TITLE)
            else:
                message = f"Stellar funds could not be moved from corporate account to {ctx.message.author}." \
                          f"Please try again later "
                await customMessages.system_message(ctx, color_code=1, message=message, destination=0,
                                                    sys_msg_title=CONST_CORP_TRANSFER_ERROR_TITLE)
        else:
            message = f"You can not sweep the account as its balance is 0.0000000 {CONST_STELLAR_EMOJI}"
            await customMessages.system_message(ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=CONST_CORP_TRANSFER_ERROR_TITLE)

    @cl.command()
    @commands.check(is_one_of_gods)
    async def stats(self, ctx):
        """
        Statistical information on Crypto Link system
        """
        #TODO fix number conversions to string
        print(f'CL STATS  : {ctx.author} -> {ctx.message.content}')
        cl_data = bot_stats.get_all_stats()
        cl_off_chain = cl_data['xlm']['ofChain']
        cl_on_chain = cl_data['xlm']['onChain']

        off_stats = Embed(title='__Crypto Link Off chain__',
                          colour=discord.Colour.greyple())
        off_stats.add_field(name='Total XLM moved',
                            value=cl_off_chain["totalTx"] + ' ' + cl_off_chain["totalMoved"])
        off_stats.add_field(name='Public',
                            value=cl_off_chain["totalPublicCount"] + ' ' + cl_off_chain["totalPublicMoved"])
        off_stats.add_field(name='Private',
                            value=cl_off_chain["totalPrivateCount"] + ' ' + cl_off_chain["totalPrivateMoved"])
        off_stats.add_field(name='Role Statistics',
                            value=cl_off_chain["rolePurchaseTxCount"] + ' ' + cl_off_chain["roleMoved"])

        await ctx.author.send(embed=off_stats)

        on_stats = Embed(title='__Crypto Link On chain__',
                         colour=discord.Colour.greyple())
        on_stats.add_field(name='Deposit count',
                           value=cl_on_chain["depositCount"])
        on_stats.add_field(name='Deposit amount',
                           value=cl_on_chain["depositAmount"])
        on_stats.add_field(name='Withdrawal count',
                           value=cl_on_chain["withdrawalCount"])
        on_stats.add_field(name='Withdrawal amount',
                           value=cl_on_chain["withdrawnAmount"])

        await ctx.author.send(embed=on_stats)

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

    @cl.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f':warning: __Restricted area__ :warning: '
            message = f'You do not have rights to access this are of the bot'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)


def setup(bot):
    bot.add_cog(BotWalletCommands(bot))
