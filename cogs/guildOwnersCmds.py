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
            title = '__Guild Owner Manual__'
            description = "All available commands to operate with guild system"
            list_of_values = [
                {"name": "Register Guild", "value": f"{self.command_string}owner register"},
                {"name": "Guild Crypto Link Stats", "value": f"{self.command_string}owner stats"},
                {"name": "Guild Applied Services", "value": f"{self.command_string}owner services"},
                {"name": "Guild CL Explorer Settings", "value": f"{self.command_string}owner explorer"},
                {"name": "Guild CL Transaction Fee Settings", "value": f"{self.command_string}owner fees"},
            ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                               destination=1)

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

        stats_info = Embed(title="__Guild Statistics__",
                           timestamp=datetime.utcnow(),
                           colour=Colour.magenta())
        await ctx.author.send(embed=stats_info)
        for k, v in stats.items():
            stats_info = Embed(title=f"__{k.upper()} Stats__",
                               timestamp=datetime.utcnow(),
                               colour=Colour.magenta())
            stats_info.add_field(name="Transactions sent",
                                 value=f'{v["txCount"]}')
            stats_info.add_field(name="Volume",
                                 value=f'{v["volume"]}')
            stats_info.add_field(name="Public Tx",
                                 value=f'{v["publicCount"]}')
            stats_info.add_field(name="Private Tx",
                                 value=f'{v["privateCount"]}')
            stats_info.add_field(name="Role purchases",
                                 value=f'{v["roleTxCount"]}')
            stats_info.add_field(name="Emoji tx",
                                 value=f'{v["emojiTxCount"]}')
            stats_info.add_field(name="Multi tx",
                                 value=f'{v["multiTxCount"]}')
            await ctx.author.send(embed=stats_info)

    @owner.command()
    @commands.check(guild_has_stats)
    async def services(self, ctx):
        service_status = await self.backoffice.guild_profiles.get_service_statuses(guild_id=ctx.guild.id)
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
                 "value": f"{self.command_string}owner explorer apply <#discord.Channel>"},
                {"name": "Remove Channel for CL feed", "value": f"{self.command_string}owner explorer remove"}
            ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                               destination=1)

    @explorer.command()
    async def apply(self, ctx, chn: TextChannel):
        data_to_update = {
            "explorerSettings.channelId": int(chn.id)
        }

        if await self.backoffice.guild_profiles.update_guild_profile(guild_id=ctx.guild.id, data_to_update=data_to_update):
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

        if await self.backoffice.guild_profiles.update_guild_profile(guild_id=ctx.guild.id, data_to_update=data_to_update):
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
