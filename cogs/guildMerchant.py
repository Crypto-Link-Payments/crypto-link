import re
from datetime import datetime

import nextcord
from nextcord import Role, Embed, Color, utils
from nextcord.ext import commands
from utils.customCogChecks import is_public, merchant_com_reg_stats_check
from cogs.utils.monetaryConversions import convert_to_currency
from cogs.utils.monetaryConversions import get_normal
from cogs.utils.systemMessaages import CustomMessages
from nextcord import Embed, Colour, slash_command, SlashOption, Interaction, Role, TextChannel, ChannelType
from utils.customCogChecks import has_wallet_inter_check, is_guild_owner_or_has_clmng, has_clmng_role, is_public_channel
from nextcord.ext import commands
import cooldowns
from nextcord import Embed, Colour, slash_command, SlashOption, Interaction, Role, TextChannel, ChannelType
from utils.customCogChecks import has_wallet_inter_check, is_guild_owner_or_has_clmng, has_clmng_role, is_public_channel
from nextcord.ext import commands
import cooldowns

customMessages = CustomMessages()
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_ROLE_CREATION_ERROR = "__Role creation error___"
CONST_ROLE_STATUS_CHANGE_ERROR = "__Role status change error__"
CONST_SYSTEM_ERROR = '__Merchant System Error__'
CONST_ROLE_STATUS_CHANGE = '__Role status change error__'
CONST_BAD_ARGUMENT_ROLE = "You have provided bad argument for Role parameter. Use @ in-front of " \
                          "the role name and tag it"


class MerchantCommunityOwner(commands.Cog):
    """
    Discord COGS handling commands for merchant system from community owner perspective
    """

    def __init__(self, bot):
        self.bot = bot
        self.merchant_channel_info = bot.backoffice.auto_messaging_channels["merchant"]
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.merchant = self.backoffice.merchant_manager

    async def create_monetized_role(self, interaction, role, in_penny: int, weeks_count: int, days_count: int, hours_count: int, minutes_count: int):
        # Prepare role data for DB
        new_role = {
            "roleId": int(role.id),
            "roleName": f'{role}',
            "communityId": int(interaction.guild.id),
            "pennyValues": int(in_penny),
            "weeks": int(weeks_count),
            "days": int(days_count),
            "hours": int(hours_count),
            "minutes": int(minutes_count),
            "status": "active"
        }

        if self.merchant.register_role(new_role):
            # Message 1: Success details
            msg_title = ':convenience_store: __Merchant System Information__ :convenience_store:'
            sys_title = f":man_juggling: ***Role successfully created*** :man_juggling:"
            message = (
                f'Role Name: {role}\n'
                f'Role ID: {role.id}\n'
                f'Value: {in_penny / 100:.2f} $\n'
                f'Duration:\n'
                f'{weeks_count} week(s), {days_count} day(s), {hours_count} hour(s), {minutes_count} minute(s)'
            )
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=sys_title,
                message=message,
                color_code=0,
                destination=1,
                embed_title=msg_title
            )

            # Message 2: Inform members
            message_title = ':convenience_store: __Merchant System Information__ :convenience_store:'
            sys_title = ":mega: Time to inform your members on available role to be purchased. :mega:"
            message = (
                f'Users can now apply for the role by executing:\n'
                f'{self.command_string}membership subscribe <@{role.name}>'
            )
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=sys_title,
                message=message,
                color_code=0,
                destination=1,
                embed_title=message_title
            )
        else:
            # Message: Failure
            message = (
                'Role could not be stored in the system at this time.\n'
                'Please try again later. We apologize for the inconvenience.'
            )
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=CONST_ROLE_CREATION_ERROR,
                message=message,
                color_code=1,
                destination=1
            )

    @slash_command(name="merchant", description="Merchant system command hub", dm_permission=False)
    @is_public_channel()
    @is_guild_owner_or_has_clmng()
    @merchant_com_reg_stats_check()
    @has_wallet_inter_check()
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def merchant(self, interaction: Interaction):
        # Optional: You can leave this blank if you only use subcommands
        await interaction.response.send_message(
            content="Use `/merchant help` to view available merchant commands.",
            ephemeral=True
        )

    @merchant.subcommand(name="help", description="Show merchant system manual and available commands")
    @is_public_channel()
    @is_guild_owner_or_has_clmng()
    @merchant_com_reg_stats_check()
    @has_wallet_inter_check()
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def merchant_help(self, interaction: Interaction):
        title = "💱 __Merchant System Message Setup__ 💱"
        description = "All available commands under the ***merchant*** category."
        list_of_commands = [
            {"name": ":information_source: How to Monetize Roles :information_source:",
            "value": "```/merchant manual```"},
            {"name": ":information_source: Access Role Management :information_source:",
            "value": "```/merchant role```"},
            {"name": ":moneybag: Access Merchant Wallet sub-commands :moneybag:",
            "value": "```/merchant wallet```"},
            {"name": ":moneybag: List Active Roles on Community :moneybag:",
            "value": "```/merchant active```"},
        ]

        await customMessages.embed_builder(
            interaction=interaction,
            title=title,
            description=description,
            data=list_of_commands,
            c=Colour.purple()
        )

    @merchant.subcommand(name="manual", description="Show how to create and use monetized roles")
    @is_public_channel()
    @is_guild_owner_or_has_clmng()
    @merchant_com_reg_stats_check()
    @has_wallet_inter_check()
    @cooldowns.cooldown(1, 20, cooldowns.SlashBucket.guild)
    async def merchant_manual(self, interaction: Interaction):

        manual = Embed(
            title=':convenience_store: __Merchant System Manual__ :convenience_store:',
            colour=Colour.purple(),
            description=":warning: if you have not open merchant yet through `/owner merchant open` you can also use /merchant initiate to create merchant wallet:warning:"
        )

        manual.add_field(
            name=':one: Create Monetized Roles :one:',
            value=(
                f'```/merchant role create <role name> <role value in $> '
                f'<weeks> <days> <hours> <minutes>```\n\n'
                f':warning: __Required Parameters__ :warning:\n'
                f'> ✅ No spaces in role name (max length: 20 characters)\n'
                f'> ✅ At least one of the time parameters must be greater than 0\n'
                f'> ✅ Role price must be greater than $0.00'
            ),
            inline=False
        )

        manual.add_field(
            name=':two: Additional Setup :two:',
            value='> Allow role to be mentioned by everyone\n> Assign permissions to created role',
            inline=False
        )

        manual.add_field(
            name=':three: Inform Members :three:',
            value=(
                'Once the role is successfully created, members can purchase it using:\n'
                f'```/membership subscribe @discord.Role```'
            ),
            inline=False
        )

        await interaction.response.send_message(embed=manual, ephemeral=True)

    ################################# MERCHANT WLALLET RELATED COMMANDS
    @merchant.subcommand(name="wallet", description="Merchant wallet operations")
    @is_public_channel()
    @is_guild_owner_or_has_clmng()
    async def wallet_group(self, interaction: Interaction):
        title = "💱 __Merchant Wallet Commands__ 💱"
        description = "All available commands to operate the merchant wallet of the community."
        list_of_commands = [
            {
                "name": ":moneybag: Get Balance Status :moneybag:",
                "value": "```/merchant wallet balance```\nAliases: `bal`"
            },
            {
                "name": ":broom: Withdraw funds to your personal account :broom:",
                "value": "```/merchant wallet sweep```\nAliases: `withdraw`"
            },
        ]
        await customMessages.embed_builder(
            interaction=interaction,
            title=title,
            description=description,
            data=list_of_commands,
            c=Color.purple()
        )

    @wallet_group.subcommand(name="balance", description="Check merchant wallet balance")
    @is_public_channel()
    @is_guild_owner_or_has_clmng()
    async def wallet_balance(self, interaction: Interaction):
        """
        Returns the current value of the community wallet in Stellar
        """
        community_id = interaction.guild.id
        data = self.merchant.get_wallet_balance(community_id=community_id)

        if data:
            wallet_details = Embed(
                title=':bank: __Merchant Wallet Balance__ :bank:',
                description=f"Current balance of the ***{interaction.guild.name}*** wallet",
                colour=Color.gold()
            )
            wallet_details.add_field(
                name=':moneybag:  Stellar Lumen :moneybag:',
                value=f"```{(data['xlm']) / (10 ** 7)} XLM```",
                inline=False
            )
            wallet_details.add_field(
                name=':warning: Withdrawal from merchant wallet :warning:',
                value=(
                    f"Use command ```/merchant wallet sweep``` to withdraw all available funds "
                    f"to your personal wallet.\n\nWithdrawing is allowed **only** for the owner of {interaction.guild.name}."
                ),
                inline=False
            )

            # Send privately (ephemeral)
            await interaction.response.send_message(embed=wallet_details, ephemeral=True)

        else:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title='__Balance Check Error__',
                message='There was a problem fetching the community balance. Please try again later or contact support.',
                color_code=1
            )


    @wallet_group.subcommand(name="sweep", description="Withdraw all funds to owner's personal wallet")
    @is_public_channel()
    @has_wallet_inter_check()
    @is_guild_owner_or_has_clmng()
    async def wallet_sweep(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        community_id = interaction.guild.id
        user_id = interaction.user.id
        guild_name = interaction.guild.name
        ticker = "xlm"
        current_time = datetime.utcnow()

        # Fee check
        withdrawal_min = self.backoffice.bot_manager.get_fees_by_category(key='merchant_min')
        withdrawal_min_dollar = withdrawal_min['fee']
        min_in_xlm = convert_to_currency(withdrawal_min_dollar, coin_name='stellar')


        if min_in_xlm.get("error"):
            return await interaction.followup.send(
                "Could not fetch live XLM conversion rates. Please try again later.",
                ephemeral=True
            )

        withdrawal_limit = min_in_xlm["total"]
        com_balance_stroops = self.merchant.get_balance_based_on_ticker(community_id=community_id, ticker=ticker)

        if com_balance_stroops < withdrawal_limit:
            return await interaction.followup.send(
                f"❌ Minimum withdrawal is `{withdrawal_limit / 1e7:.2f} XLM`, "
                f"but current balance is `{com_balance_stroops / 1e7:.2f} XLM`.",
                ephemeral=True
            )

        fee_perc = self.backoffice.bot_manager.get_fees_by_category(key='wallet_transfer')['fee']
        fee_amount = int(com_balance_stroops * (fee_perc / 100))
        net_amount = com_balance_stroops - fee_amount

        if not self.merchant.modify_funds_in_community_merchant_wallet(direction=1, community_id=community_id, wallet_tick=ticker, amount=com_balance_stroops):
            return await interaction.followup.send(
                "An error occurred while attempting to withdraw the funds. Please try again later.",
                ephemeral=True
            )

        # Transfer fee to corp account
        if not self.backoffice.bot_manager.update_cl_wallet_balance(to_update={"balance": fee_amount}, ticker=ticker):
            return await interaction.followup.send(
                "Error applying merchant fee to corporate wallet. Withdrawal aborted.",
                ephemeral=True
            )

        # Add net funds to owner's personal wallet
        if not self.backoffice.account_mng.update_user_wallet_balance(discord_id=user_id, ticker=ticker, direction=0, amount=net_amount):
            return await interaction.followup.send(
                "Funds withdrawal failed. Please contact the staff.",
                ephemeral=True
            )

        # Send embed summary to user
        embed = Embed(
            title=":money_with_wings: Withdrawal Successful",
            description=f"Withdrawal from **{guild_name}** to your personal wallet completed.",
            colour=Color.purple()
        )
        embed.add_field(name="🕒 Time", value=f"`{current_time} UTC`", inline=False)
        embed.add_field(name="💰 Amounts", value=f"```Total: {com_balance_stroops / 1e7:.2f} XLM\n"
                                                f"Fee: {fee_amount / 1e7:.2f} XLM\n"
                                                f"Net: {net_amount / 1e7:.2f} XLM```", inline=False)
        await interaction.user.send(embed=embed)

        # Notify system channel
        sys_embed = Embed(
            title=":bank: Corp Wallet Updated",
            description=f"Fee from `{guild_name}` merchant sweep added to corp.",
            colour=Color.green()
        )
        sys_embed.add_field(name="Guild", value=f"`{guild_name}`", inline=False)
        sys_embed.add_field(name="Guild Owner", value=f"`{interaction.user}`", inline=False)
        sys_embed.add_field(name="Fee Collected", value=f"`{fee_amount / 1e7:.2f} XLM`", inline=False)
        notification_channel = self.bot.get_channel(int(self.merchant_channel_info))
        await notification_channel.send(embed=sys_embed)

        await self.backoffice.stats_manager.update_cl_earnings(
            amount=fee_amount, system="merchant", token="xlm", time=current_time,
            user=str(interaction.user), user_id=user_id
        )

        await interaction.followup.send("✅ Funds withdrawn successfully!", ephemeral=True)

    ################################# ROLE RELATED COMMANDS
    @merchant.subcommand(name="role", description="Role monetization")
    @is_public_channel()
    @is_guild_owner_or_has_clmng()
    async def role_group(self, interaction: Interaction):
        await interaction.response.send_message(
            content="Use `/merchant role comms` to view available role commands.",
            ephemeral=True
        )


    @role_group.subcommand(name="comms_role", description="View commands to monetized roles")
    @is_public_channel()
    @is_guild_owner_or_has_clmng()
    async def commands_example(self, interaction: Interaction):
        title = ":man_juggling: __Merchant Role Management__ :man_juggling:"
        description = "All available commands to manage monetized roles"
        list_of_commands = [
            {
                "name": ":information_source: Create new monetized role",
                "value": f"```/merchant role create <role name> <value in $> <weeks> <days> <hours> <minutes>```"
            },
                        {
                "name": ":play_pause: Stop Active Role",
                "value": f"```/merchant role stop <@Role>```"
            },
            {
                "name": ":rocket: Activate already active role",
                "value": f"```/merchant role reactivate <@Role>```"
            },
            {
                "name": ":wastebasket: Remove role from the system and server",
                "value": f"```/merchant role delete <@Role>```"
            },
            {
                "name": ":play_pause: View Monetized Roles",
                "value": f"```/merchant role active```"
            }
        ]

        await customMessages.embed_builder(
            interaction=interaction,
            title=title,
            description=description,
            data=list_of_commands,
            c=Color.purple()
        )


    @role_group.subcommand(name="create", description="Create a new monetized role")
    @is_public_channel()
    @is_guild_owner_or_has_clmng()
    @commands.bot_has_permissions(manage_roles=True)
    async def create_role_sub(
        self,
        interaction: Interaction,
        role_name: str = SlashOption(description="Role name"),
        dollar_value: float = SlashOption(description="Dollar value"),
        weeks_count: int = SlashOption(description="Weeks", default=0),
        days_count: int = SlashOption(description="Days", default=0),
        hours_count: int = SlashOption(description="Hours", default=0),
        minutes_count: int = SlashOption(description="Minutes", default=0)
    ):
        in_penny = int(dollar_value * 100)
        total_duration = weeks_count + days_count + hours_count + minutes_count

        if any(x < 0 for x in [weeks_count, days_count, hours_count, minutes_count]) or total_duration <= 0:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=":warning: Invalid Role Duration",
                message=(
                    "The role expiration time is invalid.\n"
                    "At least one of the values for weeks, days, hours, or minutes must be greater than 0.\n"
                    "Negative values or role without specific length are not allowed."
                ),
                color_code=1
            )
            return

        if re.search(r"[~!#$%^&*()_+{}:;\'\"]", role_name):
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=":warning: Invalid Role Name",
                message=f'Role name {role_name} contains forbidden special characters.',
                color_code=1
            )
            return

        if len(role_name) > 20:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=":warning: Role Name Too Long",
                message=f'Role name {role_name} is too long. Max allowed length is 20 characters.',
                color_code=1
            )
            return

        existing_role = utils.get(interaction.guild.roles, name=role_name)
        if existing_role:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=CONST_ROLE_CREATION_ERROR,
                message=f'Role {role_name} already exists in the community.',
                color_code=1
            )
            return

        if in_penny <= 0:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=":warning: Invalid Dollar Value",
                message="The dollar value must be greater than 0.00$",
                color_code=1
            )
            return

        try:
            new_role = await interaction.guild.create_role(name=role_name)

            await self.create_monetized_role(
                interaction=interaction,
                role=new_role,
                in_penny=in_penny,
                weeks_count=weeks_count,
                days_count=days_count,
                hours_count=hours_count,
                minutes_count=minutes_count
            )
        except nextcord.Forbidden:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=CONST_ROLE_CREATION_ERROR,
                message="Error in the backend. Please contact Crypto Link owner.",
                color_code=1
            )

    @role_group.subcommand(name="reactivate", description="Reactivate an existing monetized role")
    @is_public_channel()
    @is_guild_owner_or_has_clmng()
    @commands.bot_has_permissions(manage_roles=True)
    async def reactivate_role_sub(
        self,
        interaction: Interaction,
        role: Role = SlashOption(description="Select an existing monetized role to reactivate")
    ):
        # Fetch existing role data
        role_data = self.merchant.find_role_details(role_id=role.id)
        from pprint import pprint
        pprint(role_data)
        if not role_data:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=":warning: Role Not Found",
                message=f"The role {role.name} is not registered in the Merchant system yet or is not part of the Merchant system on Crypto Link.",
                color_code=1,
            )
            return

        # Check if already active
        if role_data.get("status") == "active":
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=":information_source: Already Active",
                message=f"The role {role.name} is already active.",
                color_code=0,
            )
            return

        # Reactivate the role in the database
        role_data["status"] = "active"
        updated = self.bot.backoffice.merchant_manager.change_role_details(role_data=role_data)

        if updated:
            value_dollars = role_data.get("pennyValues", 0) / 100
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title="✅ Role Reactivated",
                message=(
                    f"Role {role.name} has been successfully reactivated.\n\n"
                    f"💰 Value: ${value_dollars:.2f}\n"
                    f"⏳ Duration: {role_data.get('weeks', 0)}w {role_data.get('days', 0)}d "
                    f"{role_data.get('hours', 0)}h {role_data.get('minutes', 0)}m"
                ),
                color_code=0,
            )
        else:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title="❌ Reactivation Failed",
                message="An error occurred while updating the role in the system. Please try again later.",
                color_code=1,
            )


    @role_group.subcommand(name="stop", description="Deactivate a monetized role")
    @is_public_channel()
    @is_guild_owner_or_has_clmng()
    @commands.bot_has_permissions(manage_roles=True)
    async def stop_role_sub(
        self,
        interaction: Interaction,
        role: Role = SlashOption(description="Select the monetized role to deactivate")
    ):
        # Fetch role details
        role_details = self.bot.backoffice.merchant_manager.find_role_details(role_id=role.id)

        if not role_details:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=":warning: Role Not Found",
                message=(
                    f"The role {role.name} is not registered in the system.\n\n"
                    f"Use `/merchant role list` to view all monetized roles."
                ),
                color_code=1,
            )
            return

        if role_details.get("status") != "active":
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=":information_source: Already Inactive",
                message=f"The role {role.name} is already inactive.",
                color_code=0,
            )
            return

        # Update role status
        role_details["status"] = "inactive"
        updated = self.bot.backoffice.merchant_manager.change_role_details(role_data=role_details)

        if updated:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title="✅ Role Deactivated",
                message=(
                    f"The role {role.name} has been deactivated.\n\n"
                    f"To reactivate it, use:\n`/merchant role reactivate @discord.Role`"
                ),
                color_code=0,
            )
        else:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title="❌ Deactivation Failed",
                message=(
                    "Role could not be deactivated due to a system issue. "
                    "Please try again later or contact an administrator if the problem persists."
                ),
                color_code=1,
            )


    @role_group.subcommand(name="delete", description="Permanently delete a monetized role from the system and the server")
    @is_public_channel()
    @is_guild_owner_or_has_clmng()
    @commands.bot_has_permissions(manage_roles=True)
    async def delete_role_sub(
        self,
        interaction: Interaction,
        role: Role = SlashOption(description="Select the monetized role to delete")
    ):
        guild = interaction.guild

        # Check if the role is monetized
        if not self.bot.backoffice.merchant_manager.find_role_details(role_id=role.id):
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=":warning: Role Not Found",
                message="This role is not registered in the merchant system and cannot be deleted.",
                color_code=1,
            )
            return

        # Attempt to remove role from merchant system
        removed = self.bot.backoffice.merchant_manager.remove_monetized_role_from_system(
            role_id=role.id,
            community_id=guild.id
        )

        if not removed:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title="❌ Deletion Failed",
                message="The role could not be removed from the merchant system. Please contact the support team.",
                color_code=1,
            )
            return

        try:
            await role.delete(reason="Deleted via /merchant role delete command")
        except Exception as e:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title="⚠️ Role Deletion Error",
                message=f"Failed to delete the role from the server: `{str(e)}`",
                color_code=1,
            )
            return

        await customMessages.system_message(
            interaction=interaction,
            sys_msg_title="✅ Role Deleted",
            message=(
                f"The monetized role {role.name} has been successfully removed from:\n"
                f"• the Crypto Link Merchant System\n"
                f"• the server (**{guild.name}**)\n"
            ),
            color_code=0,
        )


    @role_group.subcommand(name="active", description="View all monetized roles in your community")
    @is_public_channel()
    @is_guild_owner_or_has_clmng()
    @commands.check(is_public)
    async def active_roles_sub(self, interaction: Interaction):
        guild = interaction.guild
        roles = self.bot.backoffice.merchant_manager.get_all_roles_community(community_id=guild.id)

        if not roles:
            await customMessages.system_message(
                interaction=interaction,
                sys_msg_title=":circus_tent: No Monetized Roles",
                message="There are currently no monetized roles registered in your community.",
                color_code=1,
            )
            return

        title = f":circus_tent: __Available Roles in {guild.name}__ :circus_tent:"
        description = "List of all roles registered in the Crypto Link Merchant system."

        for role in roles:
            dollar_value = float(role["pennyValues"] / 100)
            values = [
                {
                    "name": ":person_juggling: Role Name",
                    "value": f"```{role['roleName']} (ID: {role['roleId']})```"
                },
                {
                    "name": ":vertical_traffic_light: Status",
                    "value": f"```{role['status']}```"
                },
                {
                    "name": ":dollar: Price",
                    "value": f"```{dollar_value:.2f} USD```"
                },
                {
                    "name": ":timer: Role Duration",
                    "value": f"```{role['weeks']}w {role['days']}d {role['hours']}h {role['minutes']}m```"
                }
            ]

            await customMessages.embed_builder(
                interaction=interaction,
                title=title,
                description=description,
                data=values,
                thumbnail=self.bot.user.avatar.url,
                c=Color.blue()
            )


def setup(bot):
    bot.add_cog(MerchantCommunityOwner(bot))
