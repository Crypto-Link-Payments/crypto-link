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
    @application_checks.check(is_guild_owner()) 
    @application_checks.check(guild_has_stats())
    async def services(self, interaction: Interaction):
        service_status = await self.backoffice.guild_profiles.get_service_statuses(
            guild_id=interaction.guild.id
        )

        explorer_channel_id = int(service_status["explorerSettings"].get("channelId", 0))
        explorer_channel = self.bot.get_channel(explorer_channel_id)

        service_info = Embed(
            title=":service_dog: __Guild Service Status__ :service_dog:",
            timestamp=datetime.utcnow(),
            description='Currently active services and their assigned channels in Crypto Link.',
            colour=Colour.dark_gold()
        )
        service_info.set_thumbnail(url=self.bot.user.avatar.url)

        if explorer_channel:
            service_info.add_field(
                name=':satellite_orbital: Crypto Link Uplink :satellite_orbital:',
                value=f'```{explorer_channel.name} ({explorer_channel.id})```',
                inline=False
            )
        else:
            service_info.add_field(
                name=':satellite_orbital: Crypto Link Uplink :satellite_orbital:',
                value=':red_circle: Not assigned',
                inline=False
            )

        # TODO add status for merchant
        await interaction.response.send_message(embed=service_info)
        

    # @owner.subcommand(name="uplink", description="Crypto Link Uplink Manual")
    # @application_checks.check(is_guild_owner())  
    # async def uplink(self, interaction: Interaction):
    #     title = ':satellite_orbital: __Crypto Link Uplink Manual__ :satellite_orbital:'
    #     description = "Use the following commands to manage Crypto Link network feed channels."

    #     list_of_values = [
    #         {
    #             "name": "Apply Channel for CL Feed",
    #             "value": "`/owner uplink apply <#channel>`"
    #         },
    #         {
    #             "name": "Remove Channel for CL Feed",
    #             "value": "`/owner uplink remove`"
    #         }
    #     ]

    #     await customMessages.embed_builder(
    #         interaction=interaction,
    #         title=title,
    #         description=description,
    #         data=list_of_values,
    #         c=Colour.dark_gold()
    #     )

    # #     interaction: Interaction,
    # #     chn: GuildChannel = SlashOption(
    # #         description="Select the channel to receive network feed",
    # #         channel_types=[ChannelType.text]
    # #     )
    # # ):
    # #     data_to_update = {
    # #         "explorerSettings.channelId": int(chn.id)
    # #     }

    # #     # Check if owner registered
    # #     if self.backoffice.guild_profiles.check_guild_registration_stats(guild_id=interaction.guild.id):
    # #         if await self.backoffice.guild_profiles.update_guild_profile(
    # #             guild_id=interaction.guild.id,
    # #             data_to_update=data_to_update
    # #         ):
    # #             await customMessages.system_message(
    # #                 interaction=interaction,
    # #                 color_code=0,
    # #                 message=f'✅ Channel {chn.mention} will now receive Crypto Link Network Activity feed.',
    # #                 sys_msg_title=CONST_SYS_MSG
    # #             )
    # #         else:
    # #             await customMessages.system_message(
    # #                 interaction=interaction,
    # #                 color_code=1,
    # #                 message='❌ Failed to update your settings.',
    # #                 sys_msg_title=CONST_SYS_MSG
    # #             )
    # #     else:
    # #         await customMessages.system_message(
    # #             interaction=interaction,
    # #             color_code=1,
    # #             message=f'Please register the server {interaction.guild.name} using `/owner register` first.',
    # #             sys_msg_title=CONST_SYS_MSG
    # #         )
    
    # @uplink.subcommand(name="apply", description="Set the channel for Crypto Link activity feed")
    # @application_checks.check(is_guild_owner())  # ✅ Only server owner allowed
    # async def apply(
    #     self,
    #     interaction: Interaction,
    #     chn: GuildChannel = SlashOption(
    #         description="Select the channel to receive network feed",
    #         channel_types=[ChannelType.text]
    #     )
    # ):
    #     guild_id = interaction.guild.id

    #     data_to_update = {
    #         "explorerSettings.channelId": chn.id
    #     }

    #     if self.backoffice.guild_profiles.check_guild_registration_stats(guild_id=guild_id):
    #         success = await self.backoffice.guild_profiles.update_guild_profile(
    #             guild_id=guild_id,
    #             data_to_update=data_to_update
    #         )

    #         if success:
    #             await customMessages.system_message(
    #                 interaction=interaction,
    #                 color_code=0,
    #                 message=f'✅ Channel {chn.mention} will now receive Crypto Link Network Activity feed.',
    #                 sys_msg_title=CONST_SYS_MSG
    #             )
    #         else:
    #             await customMessages.system_message(
    #                 interaction=interaction,
    #                 color_code=1,
    #                 message='❌ Failed to update your settings.',
    #                 sys_msg_title=CONST_SYS_MSG
    #             )
    #     else:
    #         await customMessages.system_message(
    #             interaction=interaction,
    #             color_code=1,
    #             message=f'Please register the server `{interaction.guild.name}` using `/owner register` first.',
    #             sys_msg_title=CONST_SYS_MSG
    #         )
        
    # @uplink.subcommand(name="remove", description="Switch off the Crypto Link Network Feed")
    # @application_checks.check(is_guild_owner())  # ✅ Restrict to guild owner
    # async def remove(self, interaction: Interaction):
    #     guild_id = interaction.guild.id

    #     data_to_update = {
    #         "explorerSettings.channelId": 0
    #     }

    #     success = await self.backoffice.guild_profiles.update_guild_profile(
    #         guild_id=guild_id,
    #         data_to_update=data_to_update
    #     )

    #     if success:
    #         await customMessages.system_message(
    #             interaction=interaction,
    #             color_code=0,
    #             message="📡 You have successfully turned **OFF** the Crypto Link Network Feed.",
    #             sys_msg_title=CONST_SYS_MSG
    #         )
    #     else:
    #         await customMessages.system_message(
    #             interaction=interaction,
    #             color_code=1,
    #             message=(
    #                 "❌ There was an issue turning **OFF** the network feed. "
    #                 "Please try again later or contact support."
    #             ),
    #             sys_msg_title=CONST_SYS_ERROR
    #         )


    @owner.subcommand(name="merchant", description="Guild Merchant Service")
    @application_checks.check(is_guild_owner())  # ✅ Restrict to guild owner only
    @application_checks.check(has_wallet_inter_check())
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def merchant(self, interaction: Interaction):
        # title = ':convenience_store: __Crypto Link Merchant Manual__ :convenience_store:'
        # description = "Here are the available commands to activate and manage the guild's merchant service."

        # list_of_values = [
        #     {
        #         "name": ":pencil: Open/Register for Merchant System",
        #         "value": "```/owner merchant open```"
        #     },
        #     {
        #         "name": ":joystick: Access Merchant Commands",
        #         "value": "```/merchant```"
        #     }
        # ]

        # await customMessages.embed_builder(
        #     interaction=interaction,
        #     title=title,
        #     description=description,
        #     data=list_of_values,
        #     c=Colour.dark_gold()
        # )
        return

    @merchant.subcommand(name="open", description="Register a community wallet for merchant system")
    @application_checks.check(is_guild_owner())  # ✅ Restrict to owner
    async def open(self, interaction: Interaction):
        guild_id = interaction.guild.id
        guild_name = str(interaction.guild)
        user_id = interaction.user.id

        if not self.backoffice.guild_profiles.check_guild_registration_stats(guild_id=guild_id):
            msg_title = ':warning: __Community Registration Status__ :warning:'
            message = (
                f'The server ***{guild_name}*** is not registered in the Crypto Link system yet.\n\n'
                f'Please register it first using `{self.guild_string}owner register`.'
            )
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=msg_title,
                message=message,
                color_code=1
            )
            return

        if self.merchant.check_if_community_exist(community_id=guild_id):
            msg_title = ':warning: __Merchant Registration Status__ :warning:'
            message = (
                f'The merchant system is already active for ***{guild_name}***.\n\n'
                f'Use `/merchant` to access merchant features on public channel of the server where Crypto Link has access to.'
            )
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=msg_title,
                message=message,
                color_code=0
            )
            return

        # Attempt to register the merchant wallet
        success = self.merchant.register_community_wallet(
            community_id=guild_id,
            community_owner_id=user_id,
            community_name=guild_name
        )

        if success:
            msg_title = ':rocket: __Community Wallet Registration Status__ :rocket:'
            message = (
                f'You have successfully activated the merchant system for ***{guild_name}***.\n\n'
                f'You can now use `{self.command_string}merchant` to view commands, or access the manual via '
                f'`/merchant manual`.'
            )
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=msg_title,
                message=message,
                color_code=0
            )
        else:
            msg_title = ':warning: __Merchant Registration Status__ :warning:'
            message = (
                f'An error occurred while registering the merchant wallet.\n\n'
                f'Please try again later or contact support.'
            )
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=msg_title,
                message=message,
                color_code=1
            )

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



def setup(bot):
    bot.add_cog(GuildOwnerCommands(bot))
