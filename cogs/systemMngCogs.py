"""
COGS: Management of the whole payment system
"""
import os
import sys
from datetime import datetime

from discord import Embed, Colour
from discord.ext import commands
from git import Repo, InvalidGitRepositoryError

from cogs.utils.customCogChecks import is_animus, is_one_of_gods
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

helper = Helpers()
customMessages = CustomMessages()
d = helper.read_json_file(file_name='botSetup.json')
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

# Extensions integrated into Crypto Link
extensions = ['cogs.generalCogs', 'cogs.transactionCogs', 'cogs.userAccountCogs',
              'cogs.systemMngCogs', 'cogs.hotWalletsCogs', 'cogs.clOfChainWalletCmd', 'cogs.withdrawalCogs',
              'cogs.merchantCogs', 'cogs.consumerMerchant', 'cogs.autoMessagesCogs',
              'cogs.merchantLicensingCogs',
              'cogs.feeManagementCogs']


class BotManagementCommands(commands.Cog):
    def __init__(self, bot):
        """
        Passing discord bot instance
        """
        self.bot = bot

    @commands.group()
    @commands.check(is_one_of_gods)
    async def mng(self, ctx):
        """
        Category of commands under team category
        :param ctx:
        :return:
        """

        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.invoked_subcommand is None:
            value = [{'name': 'Entry for commands to manage whole system',
                      'value': f"{d['command']}mng system*** "},
                     {'name': 'Entry for commands to manage COGS',
                      'value': f"{d['command']}god scripts*** "}
                     ]
            await customMessages.embed_builder(ctx, title='Welcome to the GOD mode',
                                               description=f"Showcase of all commands and sub-commands available "
                                                           f"for server owner, "
                                                           f" and bot creator. In order to get access to the categories "
                                                           f"***{d['command']}god*** needs to be typed in first "
                                                           f"followed by relevant sub-commands",
                                               data=value)

    @mng.group()
    @commands.check(is_animus)
    async def system(self, ctx):
        if ctx.invoked_subcommand is None:
            value = [{'name': '__Turning bot off__',
                      'value': f"***{d['command']}mng system off*** "},
                     {'name': '__Pulling update from Github__',
                      'value': f"***{d['command']}mng system update*** "},
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

    @mng.group()
    async def scripts(self, ctx):
        if ctx.invoked_subcommand is None:
            value = [{'name': '__List all cogs__',
                      'value': f"***{d['command']}mng scripts list_cogs*** "},
                     {'name': '__Loading specific cog__',
                      'value': f"***{d['command']}mng scripts load <cog name>*** "},
                     {'name': '__Unloading specific cog__',
                      'value': f"***{d['command']}mng scripts unload <cog name>*** "},
                     {'name': '__Reload all cogs__',
                      'value': f"***{d['command']}mng scripts reload*** "}
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


def setup(bot):
    bot.add_cog(BotManagementCommands(bot))
