from datetime import datetime
from bson.decimal128 import Decimal128
from re import sub
from nextcord.ext import commands, application_checks
from nextcord import Embed, Colour, slash_command, SlashOption, Interaction, Role, TextChannel
import cooldowns
from utils.customCogChecks import guild_has_stats, has_wallet_inter_check, is_guild_owner
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

    @slash_command(name='owner', description="Guild Owner manual group", dm_permission=False)
    @application_checks.check(is_guild_owner())
    @cooldowns.cooldown(1, 5, cooldowns.SlashBucket.guild)
    async def owner(self, interaction: Interaction):
        pass 

    @owner.subcommand(name="help", description="Show the guild owner's manual")
    @application_checks.check(is_guild_owner())
    @cooldowns.cooldown(1, 5, cooldowns.SlashBucket.guild)
    async def owner_help(self, interaction: Interaction):
        self.guild_string = self.bot.get_prefix_help(interaction.guild.id)
        title = ':joystick: __Guild Owner Manual__ :joystick: '
        description = "Available commands to operate the guild system."
        list_of_values = [
            {"name": ":bar_chart: Guild Crypto Link Stats :bar_chart: ",
            "value": f"`/owner stats`"},
            {"name": ":service_dog: Guild Applied Services :service_dog: ",
            "value": f"`/owner services`"},
            # {"name": ":satellite_orbital: Crypto Uplink (transaciton feeds) :satellite_orbital: ",
            # "value": f"`/owner uplink`"},
            {"name": ":convenience_store: Activate Role Monetization :convenience_store:  ",
            "value": f"`/owner merchant open`"}
        ]

        await customMessages.embed_builder(interaction=interaction, title=title,
                                        description=description, data=list_of_values,
                                        c=Colour.dark_gold())


    @owner.subcommand(name="register", description="Register Guild into the System")
    @application_checks.check(is_guild_owner())  
    @application_checks.check(has_wallet_inter_check())  
    @commands.cooldown(1, 20, commands.BucketType.user) 
    async def register(self, interaction: Interaction):
        guild_id = interaction.guild.id

        # Check if guild already exists
        if self.backoffice.guild_profiles.check_guild_registration_stats(guild_id=guild_id):
            await customMessages.system_message(
                interaction=interaction,
                color_code=1,
                message='Guild is already registered.',
                sys_msg_title=CONST_SYS_ERROR
            )
            return

        # Define the default structure per token
        default_token_structure = {
            "volume": 0.0,
            "txCount": 0,
            "privateCount": 0,
            "publicCount": 0,
            "roleTxCount": 0,
            "emojiTxCount": 0,
            "multiTxCount": 0
        }

        # Initialize new guild profile
        new_guild = {
            "guildId": guild_id,
            "guildName": str(interaction.guild),
            "explorerSettings": {"channelId": 0},
            "txFees": {"xlmFeeValue": 0},
            "registeredUsers": 0,
            "xlm": default_token_structure.copy()
        }

        # Add other integrated tokens
        try:
            all_tokens = self.bot.backoffice.token_manager.get_registered_tokens()
            for token in all_tokens:
                asset_code = token.get("assetCode")
                if asset_code and asset_code.lower() != "xlm":
                    new_guild[asset_code] = default_token_structure.copy()
        except Exception as e:
            print(f"[ERROR] Token fetch failed during guild registration: {e}")

        # Set default guild prefix
        self.bot.backoffice.guild_profiles.set_guild_prefix(guild_id=guild_id, prefix="!")

        # Register the guild
        await self.backoffice.guild_profiles.register_guild(guild_data=new_guild)

        # Confirm success
        await customMessages.system_message(
            interaction=interaction,
            color_code=0,
            message='✅ You have successfully registered the guild into the system. now you are able to use other slash commands under the /owner',
            sys_msg_title=CONST_SYS_MSG
        )

    @owner.subcommand(name="stats", description="Check Guild Stats")
    @application_checks.check(is_guild_owner())
    @application_checks.check(guild_has_stats())
    async def stats(self,
                    interaction: Interaction,
                    token: str = SlashOption(description="Token to display stats for", required=False, default='xlm')
                    ):

        token = token.lower()
        guild_id = interaction.guild.id

        stats = await self.backoffice.guild_profiles.get_guild_stats(guild_id=guild_id)
        registered_tokens = [
            x["assetCode"] for x in self.bot.backoffice.token_manager.get_registered_tokens()
        ]

        available_stats = ', '.join(t for t in registered_tokens if t.lower() != "xlm").upper()

        if token == 'xlm':
            xlm_stats = stats["xlm"]
            volume = xlm_stats["volume"]
            if isinstance(volume, Decimal128):
                volume = volume.to_decimal()

            embed = Embed(
                title=":bank: __Guild Statistics__ :bank:",
                timestamp=datetime.utcnow(),
                colour=Colour.dark_gold()
            )
            embed.set_thumbnail(url=interaction.guild.icon.url)
            embed.add_field(name="Wallets registered", value=f'`{stats["registeredUsers"]}`', inline=False)
            embed.add_field(name=":incoming_envelope: XLM Payments executed", value=f'`{xlm_stats["txCount"]}`')
            embed.add_field(name=":money_with_wings: Total Volume", value=f'`{round(volume, 7)} XLM`')
            embed.add_field(name=":cowboy: Public Transactions", value=f'`{xlm_stats["publicCount"]}`')
            embed.add_field(name=":detective: Private Transactions", value=f'`{xlm_stats["privateCount"]}`')
            embed.add_field(name=":person_juggling: Perks Sold", value=f'`{xlm_stats["roleTxCount"]}`')

            embed.add_field(
                name=':warning: Other token statistics',
                value=(
                    f'To view token-specific stats, use this command with one of the following tokens: '
                    f'`{available_stats}`'
                ),
                inline=False
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif token in [t.lower() for t in registered_tokens if t.lower() != 'xlm']:
            token_stats = stats.get(token)
            if not token_stats:
                await interaction.response.send_message(
                    f"No stats available for token `{token.upper()}`.",
                    ephemeral=True
                )
                return

            embed = Embed(
                title=f":coin: Token Statistics: {token.upper()}",
                timestamp=datetime.utcnow(),
                colour=Colour.teal()
            )
            embed.set_thumbnail(url=interaction.guild.icon.url)

            for k, v in token_stats.items():
                display_key = ' '.join(sub(r"([A-Z])", r" \1", k).split()).capitalize()
                value_str = f'{v:,.7f} {token.upper()}' if k == 'volume' else str(v)
                embed.add_field(name=display_key, value=f'```{value_str}```')

            await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            await interaction.response.send_message(
                content=(
                    f"❌ Unsupported token `{token.upper()}`.\n"
                    f"Available tokens: `{available_stats}`"
                ),
                ephemeral=True
            )


    @owner.subcommand(name="services", description="Guild Service Status")
    @application_checks.check(guild_has_stats())
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

    @owner.subcommand(name="uplink", description="Crypto Link Uplink Manual")
    async def uplink(self,
                     interaction: Interaction
                     ):
        title = ':satellite_orbital: __Crypto Link Uplink manual__ :satellite_orbital:'
        description = "All available commands to operate with guild system"
        list_of_values = [
            {"name": "Apply Channel for CL feed",
             "value": f"`/owner uplink apply <#discord.Channel>`"},
            {"name": "Remove Channel for CL feed",
             "value": f"`/owner uplink remove`"}
        ]

        await customMessages.embed_builder(interaction=interaction, title=title, description=description,
                                           data=list_of_values,
                                           c=Colour.dark_gold())

    @uplink.subcommand(name="apply", description="Crypto Link Activity Feed")
    async def apply(self,
                    interaction: Interaction,
                    chn: TextChannel
                    ):
        data_to_update = {
            "explorerSettings.channelId": int(chn.id)
        }

        # Check if owner registered
        if self.backoffice.guild_profiles.check_guild_registration_stats(guild_id=interaction.guild.id):
            if await self.backoffice.guild_profiles.update_guild_profile(guild_id=interaction.guild.id,
                                                                         data_to_update=data_to_update):
                await customMessages.system_message(interaction=interaction, color_code=0,
                                                    message=f'You have successfully set channel {chn} to receive Crypto'
                                                            f' Link Network Activity feed', sys_msg_title=CONST_SYS_MSG)
            else:
                await customMessages.system_message(interaction=interaction, color_code=1,
                                                    message='There has been an issue while trying'
                                                            'to update data.', sys_msg_title=CONST_SYS_MSG)
        else:
            await customMessages.system_message(interaction=interaction, color_code=1,
                                                message=f'Please register the {interaction.guild} to the system with '
                                                        f'/owner register', sys_msg_title=CONST_SYS_MSG)

    @uplink.subcommand(name="remove", description="Switch Off Uplink")
    async def remove(self,
                     interaction: Interaction):
        data_to_update = {
            "explorerSettings.channelId": int(0)
        }

        if await self.backoffice.guild_profiles.update_guild_profile(guild_id=interaction.guild.id,
                                                                     data_to_update=data_to_update):
            await customMessages.system_message(interaction=interaction, color_code=0,
                                                message=f'You have successfully turned OFF Crypto Link Network Feed',
                                                sys_msg_title=CONST_SYS_MSG)
        else:
            await customMessages.system_message(interaction=interaction, color_code=1,
                                                message='There has been an issue and Crypto Link Network Feed could '
                                                        'not be turned OFF. Please try again later',
                                                sys_msg_title=CONST_SYS_ERROR)

    @owner.subcommand(name="merchant", description="Guild Merchant Service")
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
                                                        message=message, color_code=0)
                else:
                    msg_title = ':warning:  __Merchant Registration Status___ :warning: '
                    message = f'There has been an issue while registering wallet into the system. ' \
                              f'Please try again later.' \
                              f' or contact one of the support staff. '
                    await customMessages.system_message(interaction=interaction, sys_msg_title=msg_title,
                                                        message=message, color_code=1)
            else:
                msg_title = ':warning:  __Community Wallet Registration Status___ :warning: '
                message = f'You have already registered Merchant system on {interaction.guild} server. Proceed' \
                          f'with command {self.command_string}merchant'
                await customMessages.system_message(interaction=interaction, sys_msg_title=msg_title,
                                                    message=message, color_code=0)
        else:
            msg_title = ':warning:  __Community Registration Status___ :warning: '
            message = f'You have not yet registered {interaction.guild} server into Crypto Link system. Please ' \
                      f'do that first through `{self.guild_string}owner register`.'
            await customMessages.system_message(interaction=interaction, sys_msg_title=msg_title,
                                                message=message, color_code=0)

    @owner.error
    async def owner_error(self, interaction, error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to be able to access this category of commands you are required to be ' \
                      f' owner of the community {interaction.guild} and execute command on one of the ' \
                      f' public channels.'
            await customMessages.system_message(interaction=interaction, color_code=1, message=message)

    @register.error
    async def register_error(self, interaction, error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to be able to register community into Crypto Link system you re required to ' \
                      f' have personal wallet registered in the system. You can do so through:\n' \
                      f' /register'
            await customMessages.system_message(interaction=interaction, color_code=1, message=message)

    # ----------------Voting pools registration-------------#
    @owner.subcommand(name="ballot", description="Crypto Link Ballot System")
    @is_guild_owner()
    @application_checks.check(has_wallet_inter_check())
    async def ballot(self,
                     interaction: Interaction):
        if self.backoffice.guild_profiles.check_guild_registration_stats(guild_id=interaction.guild.id):
            title = ':ballot_box: __Crypto Link Ballot System__ :ballot_box: '
            description = "Commands to activate voting feature over Crypto Link and Discord"
            list_of_values = [
                {"name": ":pencil: Activate ballot vote pools functionality :pencil:  ",
                 "value": f"```/owner ballot activate```"},
                {"name": ":joystick: Access commands to operate with ballot vote pools :joystick: ",
                 "value": f"```/pool```"}
            ]
            await customMessages.embed_builder(interaction=interaction, title=title, description=description,
                                               data=list_of_values,
                                               c=Colour.dark_gold())
        else:
            msg_title = ':warning:  __Community Registration Status___ :warning: '
            message = f'You have not yet registered {interaction.guild} server into Crypto Link system. Please ' \
                      f'do that first through `/owner register`.'
            await customMessages.system_message(interaction=interaction, sys_msg_title=msg_title, message=message,
                                                color_code=0)

    @ballot.subcommand(name="activate", description="Activation of voting pools")
    @is_guild_owner()
    async def activate(self,
                       interaction: Interaction,
                       r: Role):
        """
        Activation of voting pools
        """
        if not self.bot.backoffice.voting_manager.check_server_voting_reg_status(guild_id=interaction.guild.id):
            data = {
                "guildId": interaction.guild.id,
                "ownerId": interaction.user.id,
                "mngRoleId": int(r.id),
                "mngRoleName": f'{r}'
            }

            if self.backoffice.voting_manager.register_server_for_voting_service(data=data):
                await customMessages.system_message(interaction=interaction, color_code=0,
                                                    message=f'You have successfully activated ballot voting '
                                                            f'pools functionality for your'
                                                            f' server. Proceed with `{self.command_string}ballot` over '
                                                            f'public channel where Crypto Link has access to.',
                                                    sys_msg_title=CONST_SYS_MSG)
            else:
                msg_title = ':ballot_box: __Ballot Voting System Error__ :ballot_box: '
                message = f'System could not activate Ballot Voting pools due to backend issue. Please contact' \
                          f' crypto link team.'
                await customMessages.system_message(interaction=interaction, sys_msg_title=msg_title, message=message,
                                                    color_code=0)
        else:
            msg_title = ':ballot_box: __Ballot Voting System Already Active__ :ballot_box: '
            message = f'You have already activated {interaction.guild} server for voting functionality.'
            await customMessages.system_message(interaction=interaction, sys_msg_title=msg_title, message=message,
                                                color_code=0)

    @activate.error
    async def activate_error(self, interaction, error):
        if isinstance(error, commands.CheckFailure):
            message = f"You are required to specify active role on the server which will have access to the " \
                      f"Ballot voting system management. `/owner ballot activate @discord.Role'"
            await customMessages.system_message(interaction=interaction, color_code=1, message=message,
                                                sys_msg_title="Ballot voting access error!")
        elif isinstance(error, commands.MissingRequiredArgument):
            message = f"You forgot to provide @discord.Role which will have access to ballot functions."
            await customMessages.system_message(interaction=interaction, color_code=1, message=message,
                                                sys_msg_title="Ballot voting access error!")


def setup(bot):
    bot.add_cog(GuildOwnerCommands(bot))
