from datetime import datetime

from discord.ext import commands
from discord import TextChannel, Embed, Colour
from utils.customCogChecks import is_owner, is_public, guild_has_stats, has_wallet
from cogs.utils.systemMessaages import CustomMessages

customMessages = CustomMessages()

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_SYS_ERROR = '__System error__'
CONST_SYS_MSG = '__System Message__'


class GuildOwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.merchant = self.backoffice.merchant_manager

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
    @commands.check(has_wallet)
    async def register(self, ctx):
        if not self.backoffice.guild_profiles.check_guild_registration_stats(guild_id=ctx.guild.id):
            new_guild = {
                "guildId": ctx.message.guild.id,
                "guildName": f'{ctx.guild}',
                "explorerSettings": {"channelId": int(0)},
                "txFees": {"xlmFeeValue": int(0)},
                "registeredUsers": 0,
                "xlm": {"volume": float(0.0),
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
                                                destination=ctx.message.author, sys_msg_title=CONST_SYS_MSG)
        else:
            await customMessages.system_message(ctx=ctx, color_code=1, message='Guild already registered',
                                                destination=ctx.message.channel, sys_msg_title=CONST_SYS_ERROR)

    @owner.command()
    @commands.check(guild_has_stats)
    async def stats(self, ctx):
        stats = await self.backoffice.guild_profiles.get_guild_stats(guild_id=ctx.guild.id)

        stats_info = Embed(title=":bank: __Guild Statistics__ :bank: ",
                           timestamp=datetime.utcnow(),
                           colour=Colour.dark_gold())
        stats_info.add_field(name='Wallets registered',
                             value=f'`{stats["registeredUsers"]}`',
                             inline=False)
        xlm_stats = stats["xlm"]
        stats_info.add_field(name=":incoming_envelope: Transactions sent :incoming_envelope:",
                             value=f'`{xlm_stats["txCount"]}`')
        stats_info.add_field(name=":money_with_wings: Volume :money_with_wings:",
                             value=f'`{xlm_stats["volume"]}`')
        stats_info.add_field(name=":cowboy: Public Transactions :cowboy: ",
                             value=f'`{xlm_stats["publicCount"]}`')
        stats_info.add_field(name=":detective: Private Transactions :detective:",
                             value=f'`{xlm_stats["privateCount"]}`')
        stats_info.add_field(name=":person_juggling: Roles Sold :person_juggling: ",
                             value=f'`{xlm_stats["roleTxCount"]}`')
        stats_info.add_field(name=":japanese_ogre: Emoji Transactions :japanese_ogre: ",
                             value=f'`{xlm_stats["emojiTxCount"]}`')
        stats_info.add_field(name=":family_man_woman_boy: Multi tx :family_man_woman_boy: ",
                             value=f'`{xlm_stats["multiTxCount"]}`')
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
                                                        f' Link Network Activity feed',
                                                destination=ctx.message.author, sys_msg_title=CONST_SYS_MSG)
        else:
            await customMessages.system_message(ctx=ctx, color_code=1, message='There has been an issue while trying'
                                                                               'to update data.',
                                                destination=ctx.message.channel, sys_msg_title=CONST_SYS_MSG)

    @uplink.command()
    async def remove(self, ctx):
        data_to_update = {
            "explorerSettings.channelId": int(0)
        }

        if await self.backoffice.guild_profiles.update_guild_profile(guild_id=ctx.guild.id,
                                                                     data_to_update=data_to_update):
            await customMessages.system_message(ctx=ctx, color_code=0,
                                                message=f'You have successfully turned OFF Crypto Link Network Feed',
                                                destination=ctx.message.author, sys_msg_title=CONST_SYS_MSG)
        else:
            await customMessages.system_message(ctx=ctx, color_code=1, message='There has been an issue and Crypto Link'
                                                                               ' Network Feed could not be turned OFF.'
                                                                               'Please try again later',
                                                destination=ctx.message.channel, sys_msg_title=CONST_SYS_ERROR)

    @owner.group(aliases=['merchant'])
    @commands.check(is_owner)
    @commands.check(has_wallet)
    @commands.check(is_public)
    async def merch(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':convenience_store: __Crypto Link Uplink manual__ :convenience_store: '
            description = "All available commands to operate with guild system"
            list_of_values = [
                {"name": ":pencil:  Open/Reigster for Merchant system :pencil:  ",
                 "value": f"```{self.command_string}owner merchant open ```"},
                {"name": ":joystick: Access commands for merchant :joystick: ",
                 "value": f"```{self.command_string}merchant```"}
            ]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                               destination=1, c=Colour.dark_gold())

    @merch.command()
    async def open(self, ctx):
        if not self.merchant.check_if_community_exist(community_id=ctx.message.guild.id):  # Check if not registered
            if self.merchant.register_community_wallet(community_id=ctx.message.guild.id,
                                                       community_owner_id=ctx.message.author.id,
                                                       community_name=f'{ctx.message.guild}'):  # register community wallet
                msg_title = ':rocket: __Community Wallet Registration Status___ :rocket:'
                message = f'You have successfully merchant system on ***{ctx.message.guild}***. You can proceed' \
                          f' with `{self.command_string}merchant` in order to familiarize yourself with all available' \
                          f' commands or have a look at ***merchant system manual on' \
                          f' `{self.command_string}merchant manual` '
                await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=0,
                                                    destination=1)
            else:
                msg_title = ':warning:  __Merchant Registration Status___ :warning: '
                message = f'There has been an issue while registering wallet into the system. Please try again later.' \
                          f' or contact one of the support staff. '
                await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=1,
                                                    destination=1)
        else:
            msg_title = ':warning:  __Community Wallet Registration Status___ :warning: '
            message = f'You have already registered {ctx.guild} for Merchant system on {self.bot.user.mention}. Proceed' \
                      f' with command ```{self.command_string}merchant``` or ```{self.command_string}```'
            await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=0,
                                                destination=1)

    @owner.error()
    async def owner_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to be able to access this category of commands you are required to be ' \
                      f' owner of the community {ctx.guild} and execute command on one of the ' \
                      f' public channels.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)

    @register.error()
    async def register_error(self,ctx,error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to be able to register community into Crypto Link system you re required to be ' \
                      f' have personal wallet registered in the system. You can do so through' \
                      f' `{self.command_string}register`'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)



def setup(bot):
    bot.add_cog(GuildOwnerCommands(bot))
