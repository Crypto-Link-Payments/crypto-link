from datetime import datetime

from discord.ext import commands
from discord import TextChannel, Embed, Colour
from backOffice.guildServicesManager import GuildProfileManager

from cogs.utils.customCogChecks import is_owner, is_public, guild_has_stats
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
guild_manager = GuildProfileManager()
customMessages = CustomMessages()
d = helper.read_json_file(file_name='botSetup.json')

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'


class GuildOwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(is_owner)
    @commands.check(is_public)
    async def owner(self, ctx):
        if ctx.invoked_subcommand is None:
            title = '__Guild Owner Manual__'
            description = "All available commands to operate with guild system"
            list_of_values = [
                {"name": "Register Guild", "value": f"{d['command']}owner register"},
                {"name": "Guild Crypto Link Stats", "value": f"{d['command']}owner stats"},
                {"name": "Guild Applied Services", "value": f"{d['command']}owner services"},
                {"name": "Guild CL Explorer Settings", "value": f"{d['command']}owner explorer"},
                {"name": "Guild CL Transaction Fee Settings", "value": f"{d['command']}owner fees"},
            ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                               destination=1)

    @owner.command()
    @commands.check(is_owner)
    async def register(self, ctx):
        if not guild_manager.check_guild_registration_stats(guild_id=ctx.guild.id):
            new_guild = {
                "guildId": ctx.message.guild.id,
                "guildName": f'{ctx.guild}',
                "explorerSettings": {"channelId": int(0)},
                "txFees": {"xlmFeeValue": int(0)},
                "xlm": {"volume": float(0.0),
                        "txCount": int(0),
                        "privateCount": int(0),
                        "publicCount": int(0),
                        "roleTxCount": int(0),
                        "emojiTxCount": int(0),
                        "multiTxCount": int(0)},
                "clt": {"volume": float(0.0),
                        "txCount": int(0),
                        "privateCount": int(0),
                        "publicCount": int(0),
                        "roleTxCount": int(0),
                        "emojiTxCount": int(0),
                        "multiTxCount": int(0)}
            }
            await guild_manager.register_guild(guild_data=new_guild)

            await customMessages.system_message(ctx=ctx, color_code=0,
                                                message='You have successfully registered guild into the system',
                                                destination=ctx.message.author, sys_msg_title='__System Message__')
        else:
            await customMessages.system_message(ctx=ctx, color_code=1, message='Guild already registered',
                                                destination=ctx.message.channel, sys_msg_title='__System error__')

    @owner.command()
    @commands.check(guild_has_stats)
    async def stats(self, ctx):
        stats = await guild_manager.get_guild_stats(guild_id=ctx.guild.id)
        from pprint import pprint
        pprint(stats)
        # stats_info = Embed(title="__Guild Statistics__",
        #                    timestamp=datetime.utcnow(),
        #                    colour=Colour.magenta())
        # stats_info.set_thumbnail(url=self.bot.user.avatar_url)
        # stats_info.add_field(name="Transactions sent",
        #                      value=f'{stats["txCount"]}')
        # stats_info.add_field(name="Xlm Volume",
        #                      value=f'{stats["xlmVolume"]}')
        # stats_info.add_field(name="Public Tx",
        #                      value=f'{stats["publicCount"]}')
        # stats_info.add_field(name="Private Tx",
        #                      value=f'{stats["xlmVolume"]}')
        # stats_info.add_field(name="Role purchases",
        #                      value=f'{stats["roleTxCount"]}')
        # stats_info.add_field(name="Emoji tx",
        #                      value=f'{stats["emojiTxCount"]}')
        # stats_info.add_field(name="Multi tx",
        #                      value=f'{stats["xlmVolume"]}')
        # await ctx.author.send(embed=stats_info)

    @owner.command()
    @commands.check(guild_has_stats)
    async def services(self, ctx):
        service_status = await guild_manager.get_service_statuses(guild_id=ctx.guild.id)
        explorer_channel = self.bot.get_channel(id=int(service_status["explorerSettings"]["channelId"]))

        service_info = Embed(title="__Guild Service Status__",
                             timestamp=datetime.utcnow(),
                             colour=Colour.magenta())
        service_info.set_thumbnail(url=self.bot.user.avatar_url)

        if explorer_channel:
            service_info.add_field(name='Crypto Link Feed Channel',
                                   value=f'{explorer_channel} ({explorer_channel.id})')
        else:
            service_info.add_field(name='Crypto Link Feed Channel',
                                   value=f':red_circle:')

        await ctx.author.send(embed=service_info)

    @owner.group()
    async def explorer(self, ctx):
        if ctx.invoked_subcommand is None:
            title = '__Crypto Link Explorer Manual__'
            description = "All available commands to operate with guild system"
            list_of_values = [
                {"name": "Apply Channel for CL feed",
                 "value": f"{d['command']}owner explorer apply <#discord.Channel>"},
                {"name": "Remove Channel for CL feed", "value": f"{d['command']}owner explorer remove"}
            ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                               destination=1)

    @explorer.command()
    async def apply(self, ctx, chn: TextChannel):
        data_to_update = {
            "explorerSettings.channelId": int(chn.id)
        }

        if await guild_manager.update_guild_profile(guild_id=ctx.guild.id, data_to_update=data_to_update):
            await customMessages.system_message(ctx=ctx, color_code=0,
                                                message=f'You have successfully set channel {chn} to receive Crypto'
                                                        f' Link Network Feed',
                                                destination=ctx.message.author, sys_msg_title='__System Message__')
        else:
            await customMessages.system_message(ctx=ctx, color_code=1, message='There has been an issue while trying'
                                                                               'to update data.',
                                                destination=ctx.message.channel, sys_msg_title='__System error__')

    @explorer.command()
    async def remove(self, ctx):
        data_to_update = {
            "explorerSettings.channelId": int(0)
        }

        if await guild_manager.update_guild_profile(guild_id=ctx.guild.id, data_to_update=data_to_update):
            await customMessages.system_message(ctx=ctx, color_code=0,
                                                message=f'You have successfully turned OFF Crypto Link Network Feed',
                                                destination=ctx.message.author, sys_msg_title='__System Message__')
        else:
            await customMessages.system_message(ctx=ctx, color_code=1, message='There has been an issue and Crypto Link'
                                                                               ' Network Feed could not be turned OFF.'
                                                                               'Please try again later',
                                                destination=ctx.message.channel, sys_msg_title='__System error__')
    #
    # @owner.group()
    # async def fees(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         title = '__Crypto Link Custom Fees Manual__'
    #         description = "All available commands to operate with guild system"
    #         list_of_values = [
    #             {"name": "Set XLM off chain Tx fee",
    #              "value": f"{d['command']}owner fee set <xlm amount as float>"}
    #         ]
    #
    #         await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
    #                                            destination=1)
    #
    # @fees.command()
    # async def set(self, ctx, xlm: float):
    #     pass


def setup(bot):
    bot.add_cog(GuildOwnerCommands(bot))
