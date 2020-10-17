from datetime import datetime

from discord.ext import commands
from discord import TextChannel, Embed, Colour

from cogs.utils.customCogChecks import is_owner, is_public, guild_has_stats
from cogs.utils.systemMessaages import CustomMessages

customMessages = CustomMessages()

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'


class GuildOwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()

    @commands.group()
    @commands.check(is_owner)
    @commands.check(is_public)
    async def owner(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':joystick: __Guild Owner Manual__ :joystick: '
            description = "All available commands to operate with guild system."
            list_of_values = [
                {"name": ":bellhop: Register Guild :bellhop: ", "value": f"`{self.command_string}owner register`"},
                {"name": ":bar_chart: Guild Crypto Link Stats :bar_chart: ",
                 "value": f"`{self.command_string}owner stats`"},
                {"name": ":service_dog: Guild Applied Services :service_dog: ",
                 "value": f"`{self.command_string}owner services`"},
                {"name": ":satellite_orbital: Crypto Link Commands :satellite_orbital: ",
                 "value": f"`{self.command_string}owner uplink`"}
            ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                               destination=1, c=Colour.dark_gold())

    @owner.command()
    @commands.check(is_owner)
    async def register(self, ctx):
        if not self.backoffice.guild_profiles.check_guild_registration_stats(guild_id=ctx.guild.id):
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
            await self.backoffice.guild_profiles.register_guild(guild_data=new_guild)

            await customMessages.system_message(ctx=ctx, color_code=0,
                                                message='You have successfully registered guild into the system',
                                                destination=ctx.message.author, sys_msg_title='__System Message__')
        else:
            await customMessages.system_message(ctx=ctx, color_code=1, message='Guild already registered',
                                                destination=ctx.message.channel, sys_msg_title='__System error__')

    @owner.command()
    @commands.check(guild_has_stats)
    async def stats(self, ctx):
        stats = await self.backoffice.guild_profiles.get_guild_stats(guild_id=ctx.guild.id)

        stats_info = Embed(title=":bank: __Guild Statistics__ :bank: ",
                           timestamp=datetime.utcnow(),
                           colour=Colour.dark_gold())
        await ctx.author.send(embed=stats_info)
        for k, v in stats.items():
            stats_info = Embed(title=f":bar_chart: __{k.upper()} Stats__ :bar_chart: ",
                               timestamp=datetime.utcnow(),
                               colour=Colour.dark_gold())
            stats_info.add_field(name=":incoming_envelope: Transactions sent :incoming_envelope:",
                                 value=f'{v["txCount"]}')
            stats_info.add_field(name=":money_with_wings: Volume :money_with_wings:",
                                 value=f'{v["volume"]}')
            stats_info.add_field(name=":cowboy: Public Transactions :cowboy: ",
                                 value=f'{v["publicCount"]}')
            stats_info.add_field(name=":detective: Private Transactions :detective:",
                                 value=f'{v["privateCount"]}')
            stats_info.add_field(name=":person_juggling: Roles Sold :person_juggling: ",
                                 value=f'{v["roleTxCount"]}')
            stats_info.add_field(name=":japanese_ogre: Emoji Transactions :japanese_ogre: ",
                                 value=f'{v["emojiTxCount"]}')
            stats_info.add_field(name=":family_man_woman_boy: Multi tx :family_man_woman_boy: ",
                                 value=f'{v["multiTxCount"]}')
            await ctx.author.send(embed=stats_info)

    @owner.command()
    @commands.check(guild_has_stats)
    async def services(self, ctx):
        service_status = await self.backoffice.guild_profiles.get_service_statuses(guild_id=ctx.guild.id)
        explorer_channel = self.bot.get_channel(id=int(service_status["explorerSettings"]["channelId"]))

        service_info = Embed(title=":service_dog: __Guild Service Status__ :service_dog: ",
                             timestamp=datetime.utcnow(),
                             colour=Colour.dark_gold())
        service_info.set_thumbnail(url=self.bot.user.avatar_url)

        if explorer_channel:
            service_info.add_field(name=':satellite_orbital: Crypto Link Uplink :satellite_orbital: ',
                                   value=f'{explorer_channel} ({explorer_channel.id})')
        else:
            service_info.add_field(name=':satellite_orbital: Crypto Link Uplink :satellite_orbital: ',
                                   value=f':red_circle:')

        await ctx.author.send(embed=service_info)

    @owner.group()
    async def uplink(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':satellite_orbital: __Crypto Link Uplink manual__ :satellite_orbital:'
            description = "All available commands to operate with guild system"
            list_of_values = [
                {"name": "Apply Channel for CL feed",
                 "value": f"`{self.command_string}owner uplink apply <#discord.Channel>`"},
                {"name": "Remove Channel for CL feed",
                 "value": f"`{self.command_string}owner uplink remove`"}
            ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                               destination=1, c=Colour.dark_gold())

    @uplink.command()
    async def apply(self, ctx, chn: TextChannel):
        data_to_update = {
            "explorerSettings.channelId": int(chn.id)
        }

        if await self.backoffice.guild_profiles.update_guild_profile(guild_id=ctx.guild.id,
                                                                     data_to_update=data_to_update):
            await customMessages.system_message(ctx=ctx, color_code=0,
                                                message=f'You have successfully set channel {chn} to receive Crypto'
                                                        f' Link Network Feed',
                                                destination=ctx.message.author, sys_msg_title='__System Message__')
        else:
            await customMessages.system_message(ctx=ctx, color_code=1, message='There has been an issue while trying'
                                                                               'to update data.',
                                                destination=ctx.message.channel, sys_msg_title='__System error__')

    @uplink.command()
    async def remove(self, ctx):
        data_to_update = {
            "explorerSettings.channelId": int(0)
        }

        if await self.backoffice.guild_profiles.update_guild_profile(guild_id=ctx.guild.id,
                                                                     data_to_update=data_to_update):
            await customMessages.system_message(ctx=ctx, color_code=0,
                                                message=f'You have successfully turned OFF Crypto Link Network Feed',
                                                destination=ctx.message.author, sys_msg_title='__System Message__')
        else:
            await customMessages.system_message(ctx=ctx, color_code=1, message='There has been an issue and Crypto Link'
                                                                               ' Network Feed could not be turned OFF.'
                                                                               'Please try again later',
                                                destination=ctx.message.channel, sys_msg_title='__System error__')


def setup(bot):
    bot.add_cog(GuildOwnerCommands(bot))
