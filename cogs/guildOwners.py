from datetime import datetime
import decimal
from bson.decimal128 import Decimal128
from re import sub
from nextcord.ext import commands, application_checks
from nextcord import Embed, Colour, Role, slash_command, SlashOption, Interaction
import cooldowns
from utils.customCogChecks import is_owner, is_public, guild_has_stats, has_wallet, has_wallet_inter_check
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
        self.guild_string = None

    @slash_command(description="Guild Owner manual", dm_permission=False)
    # TODO: Animus to change check functions for is_owner and is_public
    @application_checks.check(is_owner)
    @cooldowns.cooldown(1, 5, cooldowns.SlashBucket.guild)
    async def owner(self,
                    interaction: Interaction
                    ):
        self.guild_string = self.bot.get_prefix_help(interaction.guild.id)
        title = ':joystick: __Guild Owner Manual__ :joystick: '
        description = "Available commands to operate the guild system."
        list_of_values = [
            {"name": ":bellhop: Register Guild :bellhop: ",
             "value": f"`/owner register`"},
            {"name": ":bar_chart: Guild Crypto Link Stats :bar_chart: ",
             "value": f"`/owner stats`"},
            {"name": ":service_dog: Guild Applied Services :service_dog: ",
             "value": f"`/owner services`"},
            {"name": ":satellite_orbital: Crypto Link Commands :satellite_orbital: ",
             "value": f"`/owner uplink`"},
            {"name": ":convenience_store: Operate with merchant :convenience_store:  ",
             "value": f"`/owner merchant`"},
            {"name": ":ballot_box: Operate with voting pools :ballot_box:",
             "value": f"`/owner ballot`"}
        ]

        await customMessages.embed_builder(interaction=interaction, title=title,
                                           description=description, data=list_of_values,
                                           c=Colour.dark_gold())

    @owner.subcommand(name="register", description="Register Guild into the System")
    @application_checks.check(has_wallet_inter_check())
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def register(self,
                       interaction: Interaction
                       ):
        if not self.backoffice.guild_profiles.check_guild_registration_stats(guild_id=interaction.guild.id):
            new_guild = {
                "guildId": interaction.guild.id,
                "guildName": f'{interaction.guild}',
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

            all_integrated_tokens = self.bot.backoffice.token_manager.get_registered_tokens()

            for asset_code in all_integrated_tokens:
                new_guild[asset_code["assetCode"]] = {"volume": float(0.0),
                                                      "txCount": int(0),
                                                      "privateCount": int(0),
                                                      "publicCount": int(0),
                                                      "roleTxCount": int(0),
                                                      "emojiTxCount": int(0),
                                                      "multiTxCount": int(0)}

            self.bot.backoffice.guild_profiles.set_guild_prefix(guild_id=int(interaction.guild.id), prefix="!")

            await self.backoffice.guild_profiles.register_guild(guild_data=new_guild)
            await customMessages.system_message(interaction=interaction, color_code=0,
                                                message='You have successfully registered guild into the system.',
                                                destination=interaction.user, sys_msg_title=CONST_SYS_MSG)
        else:
            await customMessages.system_message(interaction=interaction, color_code=1,
                                                message='Guild already registered',
                                                destination=interaction.channel,
                                                sys_msg_title=CONST_SYS_ERROR)

    @owner.subcommand(name="stats", description="Check Guild Stats")
    # TODO: Animus to change check guild_has_stats
    @application_checks.check(guild_has_stats)
    async def stats(self,
                    interaction: Interaction,
                    token: str = SlashOption(description="Balance for token", required=False, default='xlm')
                    ):
        token = token.lower()
        stats = await self.backoffice.guild_profiles.get_guild_stats(guild_id=interaction.guild.id)
        # available tokens
        tokens = [x['assetCode'] for x in self.bot.backoffice.token_manager.get_registered_tokens() if
                  x['assetCode'] != 'xlm']
        available_stats = ' '.join([str(elem) for elem in tokens]).capitalize()

        if token == 'xlm':

            stats_info = Embed(title=":bank: __Guild Statistics__ :bank: ",
                               timestamp=datetime.utcnow(),
                               colour=Colour.dark_gold())
            stats_info.add_field(name='Wallets registered',
                                 value=f'`{stats["registeredUsers"]}`',
                                 inline=False)

            volume = stats["xlm"]["volume"]
            if isinstance(volume, Decimal128):
                volume = volume.to_decimal()

            xlm_stats = stats["xlm"]

            stats_info.set_thumbnail(url=interaction.guild.icon.url)
            stats_info.add_field(name=":incoming_envelope: XLM Payments executed ",
                                 value=f'`{xlm_stats["txCount"]}`')
            stats_info.add_field(name=":money_with_wings: Total Volume ",
                                 value=f'`{round(volume, 7)} XLM`')
            stats_info.add_field(name=":cowboy: XLM Public Transactions  ",
                                 value=f'`{xlm_stats["publicCount"]}`')
            stats_info.add_field(name=":detective: XLM Private Transactions ",
                                 value=f'`{xlm_stats["privateCount"]}`')
            stats_info.add_field(name=":person_juggling: Perks Sold  ",
                                 value=f'`{xlm_stats["roleTxCount"]}`')
            # stats_info.add_field(name=":japanese_ogre: Emoji Transactions :japanese_ogre: ",
            #                      value=f'`{xlm_stats["emojiTxCount"]}`')
            # stats_info.add_field(name=":family_man_woman_boy: Multi tx :family_man_woman_boy: ",
            #                      value=f'`{xlm_stats["multiTxCount"]}`')
            stats_info.add_field(name=':warning: Other token statistics',
                                 value=f'In order to get statistics of other tokens for you server please use '
                                       f'same command structure and add one asset code from available:'
                                       f' {available_stats.upper()}',
                                 inline=False)
            await interaction.response.send_message(embed=stats_info)
        else:
            tokens = [x["assetCode"] for x in self.backoffice.token_manager.get_registered_tokens() if
                      x["assetCode"] != 'xlm']

            if tokens:
                token_stats_info = Embed(title=f'Token statistics for server')

                for token in tokens:
                    token_stats = stats[f'{token.lower()}']
                    for k, v in token_stats.items():
                        itm = sub(r"([A-Z])", r" \1", k).split()
                        item = ' '.join([str(elem) for elem in itm]).capitalize()
                        if k != 'volume':
                            token_stats_info.add_field(name=f'{item}',
                                                       value=f'```{v}```')
                        else:
                            token_stats_info.add_field(name=f'{item}',
                                                       value=f'```{v:,.7f} {token.upper()}```')
                    await interaction.response.send_message(embed=token_stats_info)
            else:
                await interaction.response.send_message(content="No tokens registered")

    @owner.subcommand(name="services", description="Guild Service Status")
    # TODO: Animus to change check guild_has_stats
    @application_checks.check(guild_has_stats)
    async def services(self,
                       interaction: Interaction
                       ):
        service_status = await self.backoffice.guild_profiles.get_service_statuses(guild_id=interaction.guild.id)
        explorer_channel = self.bot.get_channel(int(service_status["explorerSettings"]["channelId"]))

        service_info = Embed(title=":service_dog: __Guild Service Status__ :service_dog: ",
                             timestamp=datetime.utcnow(),
                             description=f'All activated services on Crypto Link system and their relays',
                             colour=Colour.dark_gold())
        service_info.set_thumbnail(url=self.bot.user.avatar.url)

        if explorer_channel:
            service_info.add_field(name=':satellite_orbital: Crypto Link Uplink :satellite_orbital: ',
                                   value=f'```{explorer_channel} ({explorer_channel.id})```')
        else:
            service_info.add_field(name=':satellite_orbital: Crypto Link Uplink :satellite_orbital: ',
                                   value=f':red_circle:')

        await interaction.response.sent_message(embed=service_info)

    # @owner.group()
    # async def uplink(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         title = ':satellite_orbital: __Crypto Link Uplink manual__ :satellite_orbital:'
    #         description = "All available commands to operate with guild system"
    #         list_of_values = [
    #             {"name": "Apply Channel for CL feed",
    #              "value": f"`{self.command_string}owner uplink apply <#discord.Channel>`"},
    #             {"name": "Remove Channel for CL feed",
    #              "value": f"`{self.command_string}owner uplink remove`"}
    #         ]
    #
    #         await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
    #                                            c=Colour.dark_gold())

    # @uplink.command()
    # async def apply(self, ctx, chn: TextChannel):
    #     data_to_update = {
    #         "explorerSettings.channelId": int(chn.id)
    #     }
    #
    #     # Check if owner registered
    #     if self.backoffice.guild_profiles.check_guild_registration_stats(guild_id=ctx.guild.id):
    #         if await self.backoffice.guild_profiles.update_guild_profile(guild_id=ctx.guild.id,
    #                                                                      data_to_update=data_to_update):
    #             await customMessages.system_message(ctx=ctx, color_code=0,
    #                                                 message=f'You have successfully set channel {chn} to receive Crypto'
    #                                                         f' Link Network Activity feed',
    #                                                 destination=ctx.message.author, sys_msg_title=CONST_SYS_MSG)
    #         else:
    #             await customMessages.system_message(ctx=ctx, color_code=1,
    #                                                 message='There has been an issue while trying'
    #                                                         'to update data.',
    #                                                 destination=ctx.message.channel, sys_msg_title=CONST_SYS_MSG)
    #     else:
    #         await customMessages.system_message(ctx=ctx, color_code=1, message=f'Please register the {ctx.guild}'
    #                                                                            f' to the system with '
    #                                                                            f'`{self.guild_string}owner register',
    #                                             destination=ctx.message.channel, sys_msg_title=CONST_SYS_MSG)

    # @uplink.command()
    # async def remove(self, ctx):
    #     data_to_update = {
    #         "explorerSettings.channelId": int(0)
    #     }
    #
    #     if await self.backoffice.guild_profiles.update_guild_profile(guild_id=ctx.guild.id,
    #                                                                  data_to_update=data_to_update):
    #         await customMessages.system_message(ctx=ctx, color_code=0,
    #                                             message=f'You have successfully turned OFF Crypto Link Network Feed',
    #                                             destination=ctx.message.author, sys_msg_title=CONST_SYS_MSG)
    #     else:
    #         await customMessages.system_message(ctx=ctx, color_code=1, message='There has been an issue and Crypto Link'
    #                                                                            ' Network Feed could not be turned OFF.'
    #                                                                            'Please try again later',
    #                                             destination=ctx.message.channel, sys_msg_title=CONST_SYS_ERROR)

    @owner.subcommand(name="merchant", description="Guild Merchant Service")
    # TODO: Animus to change check is_owner and is_public
    @application_checks.check(is_owner)
    @application_checks.check(has_wallet_inter_check())
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def merchant(self,
                       interaction: Interaction
                       ):
        title = ':convenience_store: __Crypto Link Uplink manual__ :convenience_store: '
        description = "All available commands to activate and operate with merchant service."
        list_of_values = [
            {"name": ":pencil: Open/Register for Merchant system :pencil:  ",
             "value": f"```/owner merchant open ```"},
            {"name": ":joystick: Access commands for merchant :joystick: ",
             "value": f"```/merchant```"}
        ]

        await customMessages.embed_builder(interaction=interaction, title=title,
                                           description=description, data=list_of_values,
                                           c=Colour.dark_gold())

    @merchant.subcommand(name="open", description="Community Wallet Registration")
    async def open(self,
                   interaction: Interaction
                   ):
        if self.backoffice.guild_profiles.check_guild_registration_stats(guild_id=interaction.guild.id):
            if not self.merchant.check_if_community_exist(community_id=interaction.guild.id):  # Check if not registered
                if self.merchant.register_community_wallet(community_id=interaction.guild.id,
                                                           community_owner_id=interaction.user.id,
                                                           community_name=f'{interaction.guild}'):
                    msg_title = ':rocket: __Community Wallet Registration Status___ :rocket:'
                    message = f'You have successfully merchant system on ***{interaction.guild}***. You can proceed ' \
                              f' with `/merchant` in order to familiarize yourself with ' \
                              f'all available commands or have a look at ***merchant system' \
                              f' manual*** accessible through command ' \
                              f' `/merchant manual` '
                    await customMessages.system_message(interaction=interaction, sys_msg_title=msg_title,
                                                        message=message, color_code=0,
                                                        destination=1)
                else:
                    msg_title = ':warning:  __Merchant Registration Status___ :warning: '
                    message = f'There has been an issue while registering wallet into the system. ' \
                              f'Please try again later.' \
                              f' or contact one of the support staff. '
                    await customMessages.system_message(interaction=interaction, sys_msg_title=msg_title,
                                                        message=message, color_code=1,
                                                        destination=1)
            else:
                msg_title = ':warning:  __Community Wallet Registration Status___ :warning: '
                message = f'You have already registered Merchant system on {interaction.guild} server. Proceed' \
                          f'with command {self.command_string}merchant'
                await customMessages.system_message(interaction=interaction, sys_msg_title=msg_title,
                                                    message=message, color_code=0,
                                                    destination=1)
        else:
            msg_title = ':warning:  __Community Registration Status___ :warning: '
            message = f'You have not yet registered {interaction.guild} server into Crypto Link system. Please ' \
                      f'do that first through `{self.guild_string}owner register`.'
            await customMessages.system_message(interaction=interaction, sys_msg_title=msg_title,
                                                message=message, color_code=0,
                                                destination=1)

    @owner.error
    async def owner_error(self, interaction, error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to be able to access this category of commands you are required to be ' \
                      f' owner of the community {interaction.guild} and execute command on one of the ' \
                      f' public channels.'
            await customMessages.system_message(interaction=interaction, color_code=1, message=message, destination=0)

    @register.error
    async def register_error(self, interaction, error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to be able to register community into Crypto Link system you re required to ' \
                      f' have personal wallet registered in the system. You can do so through:\n' \
                      f' /register'
            await customMessages.system_message(interaction=interaction, color_code=1, message=message, destination=0)

    # # ----------------Voting pools registration-------------#
    # @owner.group()
    # @commands.check(is_owner)
    # @commands.check(has_wallet)
    # @commands.check(is_public)
    # async def ballot(self, ctx):
    #     if self.backoffice.guild_profiles.check_guild_registration_stats(guild_id=ctx.guild.id):
    #         if ctx.invoked_subcommand is None:
    #             title = ':ballot_box: __Crypto Link Ballot System__ :ballot_box: '
    #             description = "Commands to activate voting feature over Crypto Link and Discord"
    #             list_of_values = [
    #                 {"name": ":pencil: Activate ballot vote pools functionality :pencil:  ",
    #                  "value": f"```{self.command_string}owner ballot activate```"},
    #                 {"name": ":joystick: Access commands to operate with ballot vote pools :joystick: ",
    #                  "value": f"```{self.command_string}pool```"}
    #             ]
    #             await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
    #                                                c=Colour.dark_gold())
    #     else:
    #         msg_title = ':warning:  __Community Registration Status___ :warning: '
    #         message = f'You have not yet registered {ctx.guild} server into Crypto Link system. Please ' \
    #                   f'do that first through `{self.guild_string}owner register`.'
    #         await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=0,
    #                                             destination=1)
    #
    # @ballot.command()
    # async def activate(self, ctx, r: Role):
    #     """
    #     Activation of voting pools
    #     """
    #     if not self.bot.backoffice.voting_manager.check_server_voting_reg_status(guild_id=ctx.guild.id):
    #         data = {
    #             "guildId": ctx.guild.id,
    #             "ownerId": ctx.author.id,
    #             "mngRoleId": int(r.id),
    #             "mngRoleName": f'{r}'
    #         }
    #
    #         if self.backoffice.voting_manager.register_server_for_voting_service(data=data):
    #             await customMessages.system_message(ctx=ctx, color_code=0,
    #                                                 message=f'You have successfully activated ballot voting '
    #                                                         f'pools functionality for your'
    #                                                         f' server. Proceed with `{self.command_string}ballot` over '
    #                                                         f'public channel where Crypto Link has access to.',
    #                                                 destination=1, sys_msg_title=CONST_SYS_MSG)
    #         else:
    #             msg_title = ':ballot_box: __Ballot Voting System Error__ :ballot_box: '
    #             message = f'System could not activate Ballot Voting pools due to backend issue. Please contact' \
    #                       f' crypto link team.'
    #             await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=0,
    #                                                 destination=1)
    #     else:
    #         msg_title = ':ballot_box: __Ballot Voting System Already Active__ :ballot_box: '
    #         message = f'You have already activated {ctx.guild} server for voting functionality.'
    #         await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=0,
    #                                             destination=1)
    #
    # @activate.error
    # async def activate_error(self, ctx, error):
    #     if isinstance(error, commands.CheckFailure):
    #         message = f"You are required to specify active role on the server which will have access to the " \
    #                   f"Ballot voting system management. `{self.command_string}owner ballot activate @discord.Role'"
    #         await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
    #                                             sys_msg_title="Ballot voting access error!")
    #     elif isinstance(error, commands.MissingRequiredArgument):
    #         message = f"You forgot to provide @discord.Role which will have access to ballot functions."
    #         await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
    #                                             sys_msg_title="Ballot voting access error!")


def setup(bot):
    bot.add_cog(GuildOwnerCommands(bot))
