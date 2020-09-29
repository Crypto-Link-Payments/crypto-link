"""
COGS: Management of the whole payment system
"""
import os
import sys
import time
from datetime import datetime

from discord import Embed, Colour
from discord.ext import commands
from git import Repo, InvalidGitRepositoryError
from backOffice.profileRegistrations import AccountManager
from backOffice.botWallet import BotManager
from backOffice.stellarActivityManager import StellarManager
from backOffice.corpHistory import CorporateHistoryManager
from backOffice.statsManager import StatsManager
from cogs.utils.monetaryConversions import get_decimal_point, get_normal
from cogs.utils.customCogChecks import is_animus, is_one_of_gods
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

helper = Helpers()
account_mng = AccountManager()
customMessages = CustomMessages()
stellar = StellarManager()
corporate_hist_mng = CorporateHistoryManager()
bot_manager = BotManager()
stats_manager = StatsManager()
d = helper.read_json_file(file_name='botSetup.json')
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_CORP_TRANSFER_ERROR_TITLE = '__Corporate Transfer Error__'

# Extensions integrated into Crypto Link
extensions = ['cogs.generalCogs', 'cogs.transactionCogs', 'cogs.userAccountCogs',
              'cogs.systemMngCogs', 'cogs.hotWalletsCogs', 'cogs.withdrawalCogs',
              'cogs.merchantCogs', 'cogs.consumerMerchant', 'cogs.autoMessagesCogs', 'cogs.merchantLicensingCogs',
              'cogs.feeManagementCogs', 'cogs.guildOwnersCmds']


class BotManagementCommands(commands.Cog):
    def __init__(self, bot):
        """
        Passing discord bot instance
        """
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
        corp_channel = Embed(
            title=f'__{emoji} Corporate account transfer activity__ {emoji}',
            description=f'Notification on corporate funds transfer activity on {chain_name}',
            colour=Colour.greyple())
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
            title = '__Crypto Link commands__'
            description = "All commands to operate with Crypto Link Corporate Wallet"
            list_of_values = [
                {"name": "Check Corporate Balance", "value": f"{d['command']}cl balance"},
                {"name": "Withdrawing XLM from Corp to personal",
                 "value": f"{d['command']}cl sweep"},
                {"name": "Statistics of crypto link system",
                 "value": f"{d['command']}cl stats"},
                {"name": "Other categories",
                 "value": f"{d['command']}system\n"
                          f"{d['command']}manage"}
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
        values = Embed(title="Balance of Crypto-Link Off chain balance",
                       description="Current state of Crypto Link Lumen wallet",
                       color=Colour.blurple())
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
    async def stats(self, ctx):
        """
        Statistical information on Crypto Link system
        """
        data = stats_manager.get_all_stats()
        cl_off_chain = data["xlm"]["offChain"]
        cl_on_chain = data['xlm']['onChain']

        guilds = await self.bot.fetch_guilds(limit=150).flatten()
        reach = len(self.bot.users)
        world = Embed(title='__Crypto Link__',
                      colour=Colour.magenta(),
                      timestamp=datetime.utcnow())
        world.add_field(name='Guild reach',
                        value=f'{len(guilds)}',
                        inline=False)
        world.add_field(name='Member reach',
                        value=f'{reach}',
                        inline=False)
        await ctx.author.send(embed=world)

        on_stats = Embed(title='__Crypto Link On Chain__',
                         colour=Colour.greyple())
        on_stats.add_field(name=f'Total Deposits',
                           value=f'{cl_on_chain["depositCount"]}')
        on_stats.add_field(name=f'Total Deposited',
                           value=f'{cl_on_chain["depositAmount"]} XLM')
        on_stats.add_field(name=f'Total Withdrawals',
                           value=f'{cl_on_chain["withdrawalCount"]}')
        on_stats.add_field(name=f'Total Withdrawn',
                           value=f'{cl_on_chain["withdrawnAmount"]} XLM')
        await ctx.author.send(embed=on_stats)

        off_chain = Embed(title=f'__Crypto Link off chain__',
                          colour=Colour.greyple())
        off_chain.add_field(name=f'Total Transactions done',
                            value=f'{cl_off_chain["totalTx"]}')
        off_chain.add_field(name=f'Total XLM moved',
                            value=f'{cl_off_chain["totalMoved"]}')
        off_chain.add_field(name=f'Total Public TX',
                            value=f'{cl_off_chain["totalPublicCount"]}')
        off_chain.add_field(name=f'Total Public Moved',
                            value=f'{cl_off_chain["totalPublicMoved"]}')
        off_chain.add_field(name=f'Total Private TX',
                            value=f'{cl_off_chain["totalPrivateCount"]}')
        off_chain.add_field(name=f'Total Private Moved',
                            value=f'{cl_off_chain["totalPrivateMoved"]}')
        off_chain.add_field(name=f'Total Emoji Tx',
                            value=f'{cl_off_chain["totalEmojiTx"]}')
        off_chain.add_field(name=f'Total Emoji Moved',
                            value=f'{cl_off_chain["totalEmojiMoved"]}')
        off_chain.add_field(name=f'Total Multi Tx',
                            value=f'{cl_off_chain["multiTxCount"]}')
        off_chain.add_field(name=f'Total Multi moved',
                            value=f'{cl_off_chain["multiTxMoved"]}')
        off_chain.add_field(name=f'Total Merchant Tx',
                            value=f'{cl_off_chain["merchantPurchases"]}')
        off_chain.add_field(name=f'Total Merchant moved',
                            value=f'{cl_off_chain["merchantMoved"]}')
        await ctx.author.send(embed=off_chain)

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

    @commands.group()
    @commands.check(is_one_of_gods)
    async def system(self, ctx):
        if ctx.invoked_subcommand is None:
            value = [{'name': '__Turning bot off__',
                      'value': f"***{d['command']}system off*** "},
                     {'name': '__Pulling update from Github__',
                      'value': f"***{d['command']}system update*** "},
                     ]

            await customMessages.embed_builder(ctx, title='Available sub commands for system',
                                               description='Available commands under category ***system***', data=value)

    @system.command()
    async def off(self, ctx):
        await ctx.channel.send(content='Going Offline!')
        await self.bot.close()
        sys.exit(0)

    @system.command()
    async def update(self):
        notification_str = ''
        channel_id = auto_channels['sys']
        channel = self.bot.get_channel(id=int(channel_id))
        current_time = datetime.utcnow()
        try:
            repo = Repo()  # Initiate repo
            git = repo.git
            git.pull()
            notification_str += 'GIT UPDATE STATUS\n' \
                                ' Latest commits pulled :green_circle: \n' \
                                '=============================================\n'
        except InvalidGitRepositoryError:
            notification_str += 'GIT UPDATE: There has been an error while pulling latest commits :red_circle:  \n' \
                                'Error: Git Repository could not be found\n' \
                                '=============================================\n'
            await channel.send(content=notification_str)

        notification_str += 'STATUS OF COGS AFTER RELOAD\n'
        for extension in extensions:
            print(f'Trying to load extension {extension}')
            try:
                self.bot.unload_extension(f'{extension}')
                self.bot.load_extension(f'{extension}')
                notification_str += f'{extension} :green_circle:  \n'
                print('success')
                print('=========')
            except Exception as e:
                notification_str += f'{extension} :red_circle:' \
                                    f'Error: {e} \n'
                print('failed')
                print('=========')
        notification_str += 'GIT UPDATE STATUS\n' \
                            ' Latest commits pulled :green_circle: \n' \
                            '=============================================\n'
        load_status = Embed(title='System update message',
                            description='Status after git update',
                            colour=Colour.green())
        load_status.add_field(name='Time of execution',
                              value=f'{current_time}',
                              inline=False)
        load_status.add_field(name='Status Message',
                              value=notification_str,
                              inline=False)
        await channel.send(embed=load_status)

    @commands.group()
    @commands.check(is_one_of_gods)
    async def manage(self, ctx):
        """
        Category of commands under team category
        :param ctx:
        :return:
        """

        if ctx.invoked_subcommand is None:
            value = [{'name': 'Entry for commands to manage COGS',
                      'value': f"{d['command']}manage scripts*** "}
                     ]
            await customMessages.embed_builder(ctx, title='Crypto Link Management commands',
                                               description=f"",
                                               data=value)

    @manage.group()
    async def scripts(self, ctx):
        if ctx.invoked_subcommand is None:
            value = [{'name': '__List all cogs__',
                      'value': f"***{d['command']}manage scripts list_cogs*** "},
                     {'name': '__Loading specific cog__',
                      'value': f"***{d['command']}manage scripts load <cog name>*** "},
                     {'name': '__Unloading specific cog__',
                      'value': f"***{d['command']}manage scripts unload <cog name>*** "},
                     {'name': '__Reload all cogs__',
                      'value': f"***{d['command']}manage scripts reload*** "}
                     ]

            await customMessages.embed_builder(ctx, title='Available sub commands for system',
                                               description='Available commands under category ***system***', data=value)

    @scripts.command()
    async def load(self, ctx, extension: str):
        """
        Load specific COG == Turn ON
        :param ctx: Context
        :param extension: Extension Name as str
        :return:
        """
        try:
            self.bot.load_extension(f'cogs.{extension}')
            embed_unload = Embed(name='Boom',
                                 title='Cogs management',
                                 colour=Colour.green())
            embed_unload.add_field(name='Extension',
                                   value=f'You have loaded ***{extension}*** COGS')

            await ctx.channel.send(embed=embed_unload)
        except Exception as error:
            await ctx.channel.send(content=error)

    @scripts.command()
    async def unload(self, ctx, extension: str):
        """
        Unloads COG == Turns OFF commands under certain COG
        :param ctx: Context
        :param extension: COG Name
        :return:
        """
        try:
            self.bot.unload_extension(f'cogs.{extension}')
            embed_unload = Embed(name='Boom',
                                 title='Cogs management',
                                 colour=Colour.red())
            embed_unload.add_field(name='Extension',
                                   value=f'You have unloaded ***{extension}*** COGS')

            await ctx.channel.send(embed=embed_unload)
        except Exception as error:
            await ctx.channel.send(content=error)

    @scripts.command()
    async def list_cogs(self, ctx):
        """
        List all cogs implemented in the system
        """
        cog_list_embed = Embed(title='All available COGS',
                               description='All available cogs and their description',
                               colour=Colour.green())
        for cg in extensions:
            cog_list_embed.add_field(name=cg,
                                     value='==============',
                                     inline=False)
        await ctx.channel.send(embed=cog_list_embed)

    @scripts.command()
    async def reload(self, ctx):
        """
         Reload all cogs
        """
        notification_str = ''
        ext_load_embed = Embed(title='System message',
                               description='Status of the cogs after reload',
                               colour=Colour.blue())
        for extension in extensions:
            try:
                self.bot.unload_extension(f'{extension}')
                self.bot.load_extension(f'{extension}')
                notification_str += f'{extension} :smile: \n'
            except Exception as e:
                notification_str += f'{extension} :angry: {e}\n'

        ext_load_embed.add_field(name='Status',
                                 value=notification_str)
        await ctx.channel.send(embed=ext_load_embed)

    @cl.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f':warning: __Restricted area__ :warning: '
            message = f'You do not have rights to access this are of the bot'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)


def setup(bot):
    bot.add_cog(BotManagementCommands(bot))
