"""
File includes custom security checks for the Discord GUI part
"""

from nextcord import ChannelType, Interaction, TextChannel, Thread
from nextcord.ext import application_checks
from nextcord.errors import ApplicationCheckFailure  
from nextcord import Interaction
from nextcord.ext import application_checks
from nextcord.ext.commands.errors import CheckFailure


def is_animus(ctx):
    """
    Check if creator
    """
    return ctx.bot.is_animus(ctx.message.author.id)


def is_one_of_gods(ctx):
    return ctx.bot.is_one_of_gods(ctx.message.author.id)


def is_public(ctx):
    """
    Check if channel is public where command has been executed
    :param ctx: Discord Context
    :return: Boolean
    """
    print(ctx.channel.type)
    return ctx.message.channel.type != ChannelType.private


def is_dm(ctx):
    return not ctx.message.guild


def has_wallet(ctx):
    """
    Check if user has already registered personal wallet to the system
    :param ctx: Context
    :return: Boolean
    """
    return ctx.bot.backoffice.account_mng.check_user_existence(user_id=ctx.message.author.id)

def is_public_channel():
    async def predicate(interaction: Interaction):
        print("✅ Is public check running for guild:", interaction.guild_id)
        if interaction.guild is None:
            raise ApplicationCheckFailure("❌ This command cannot be used in Direct Messages.")

        if isinstance(interaction.channel, Thread):
            raise ApplicationCheckFailure("❌ This command cannot be used in thread channels.")

        if not isinstance(interaction.channel, TextChannel):
            raise ApplicationCheckFailure("❌ This command must be used in a public text channel.")

        return True

    return application_checks.check(predicate)


def has_wallet_inter_check():
    def predicate(interaction: Interaction):
        print("✅ Wallet check running for user:", interaction.user.id)

        user_id = interaction.user.id
        exists = interaction.client.backoffice.account_mng.check_user_existence(user_id=user_id)
        if not exists:
            raise ApplicationCheckFailure(
                "❌ You don’t have a wallet yet.\nUse `/register` to create one and get started."
            )
        return True

    return application_checks.check(predicate)

def is_owner(ctx):
    """
    Function checks if the user is owner of the community or not
    """
    return int(ctx.message.author.id) == int(ctx.message.guild.owner_id)

def has_clmng_role():
    async def predicate(interaction: Interaction):
        if interaction.guild is None:
            raise ApplicationCheckFailure("This command can only be used in a server.")

        if not hasattr(interaction.user, "roles"):
            raise ApplicationCheckFailure("This command requires role-based permissions.")

        has_role = any(role.name == "CLMng" for role in interaction.user.roles)
        if not has_role:
            raise ApplicationCheckFailure("❌ Access denied! You must have the 'CLMng' role to use this command.")
        return True

    return application_checks.check(predicate)

def is_guild_owner():
    async def predicate(interaction: Interaction):
        if interaction.guild is None:
            raise ApplicationCheckFailure("This command can only be used in a server.")

        if not hasattr(interaction.user, "id") or not hasattr(interaction.guild, "owner_id"):
            raise ApplicationCheckFailure("Unable to verify ownership due to missing user or guild data.")

        if interaction.user.id != interaction.guild.owner_id:
            raise ApplicationCheckFailure("❌ Access denied! Only the server owner can use this command.")
        return True

    return application_checks.check(predicate)


def is_guild_owner_or_has_clmng():
    async def predicate(interaction: Interaction):
        if interaction.guild is None:
            raise CheckFailure("❌ This command can only be used in a server.")

        user = interaction.user

        if user.id == interaction.guild.owner_id:
            return True

        if hasattr(user, "roles") and any(role.name == "CLMng" for role in user.roles):
            return True

        raise CheckFailure("❌ You must be the server owner or have the 'CLMng' role.")
    
    return application_checks.check(predicate)


def merchant_com_reg_stats(ctx):
    """
    Checks if community is registered in the merchant system
    """
    try:
        return ctx.bot.backoffice.merchant_manager.check_if_community_exist(community_id=int(ctx.message.guild.id))
    except AttributeError:
        return False

# def merchant_com_reg_stats_check():
#     def predicate(interaction: Interaction):
#         try:
#             return interaction.client.backoffice.merchant_manager.check_if_community_exist(
#                 community_id=interaction.guild.id
#             )
#         except AttributeError:
#             return False
#     return application_checks.check(predicate)

def merchant_com_reg_stats_check():
    def predicate(interaction: Interaction):
        if interaction.guild is None:
            raise ApplicationCheckFailure("This command can only be used in a server.")

        if not hasattr(interaction.client, "backoffice") or not hasattr(interaction.client.backoffice, "merchant_manager"):
            raise ApplicationCheckFailure("❌ Access denied! Merchant system is not available.")

        try:
            exists = interaction.client.backoffice.merchant_manager.check_if_community_exist(
                community_id=interaction.guild.id
            )
            if not exists:
                raise ApplicationCheckFailure("❌ This server is not registered as a merchant community. Please register it first")
            return True
        except Exception as e:
            raise ApplicationCheckFailure(f"❌ Error checking community registration: {str(e)}")

    return application_checks.check(predicate)

def guild_has_stats():
    """
    Check if the guild has registered stats in the system.
    Used to gate commands that require existing stats data.
    """
    def predicate(interaction: Interaction):
        if interaction.guild is None:
            raise ApplicationCheckFailure("❌ This command can only be used in a server.")

        try:
            exists = interaction.client.backoffice.guild_profiles.check_guild_registration_stats(
                guild_id=interaction.guild.id
            )
            if not exists:
                raise ApplicationCheckFailure("❌ This guild is not registered for stats.")
            return True

        except AttributeError:
            raise ApplicationCheckFailure("❌ Could not access guild profile system. Please try again later.")

    return application_checks.check(predicate)

def community_missing(ctx):
    """
    Check if community not registered in the system
    """
    return ctx.bot.backoffice.merchant_manager.check_if_community_exist(community_id=ctx.message.guild.id) is None


def user_has_wallet(ctx):
    """
    Check if user has wallet registered in the system
    """
    return ctx.bot.backoffice.account_mng.check_user_existence(user_id=ctx.message.author.id)



def guild_has_merchant():
    """
    Slash command check to ensure the community has the merchant system enabled.
    """
    async def predicate(interaction: Interaction):
        print("✅ Guild has merchant check running for guild:", interaction.guild_id)
        if interaction.guild is None:
            raise ApplicationCheckFailure("❌ This command can only be used in a server.")

        if not hasattr(interaction.client, "backoffice") or not hasattr(interaction.client.backoffice, "merchant_manager"):
            raise ApplicationCheckFailure("❌ Access denied! Merchant system is not available.")

        try:
            exists = interaction.client.backoffice.merchant_manager.check_if_community_exist(
                community_id=interaction.guild.id
            )
            if not exists:
                raise ApplicationCheckFailure("❌ This server is not registered as a merchant community. Please register it first.")
            return True
        except Exception as e:
            raise ApplicationCheckFailure(f"❌ Error checking merchant registration: {str(e)}")

    return application_checks.check(predicate)

def user_has_second_level(ctx):
    """
    Custom check for custodial wallet
    """
    return ctx.bot.backoffice.second_level_manager.second_level_user_reg_status(user_id=ctx.author.id)


def user_has_no_second(ctx):
    """
    Check if user has not registered for second wallet
    """
    return not ctx.bot.backoffice.second_level_manager.second_level_user_reg_status(user_id=ctx.author.id)


def user_has_third_level(ctx):
    """
    Check if user has registered for third level
    """
    return ctx.bot.backoffice.third_level_manager.third_level_user_reg_status(user_id=ctx.author.id)


def user_has_no_third_level(ctx):
    """
    Check if user has not registered for third level
    """
    return not ctx.bot.backoffice.third_level_manager.third_level_user_reg_status(user_id=ctx.author.id)


# def check(author):
#     def inner_check(message):
#         """
#         Check for answering the verification message on withdrawal. Author origin
#         """
#         if message.author.id == author.id:
#             return True
#         else:
#             return False

#     return inner_check


def has_ballot_access(ctx):
    voting_role_id = ctx.bot.backoffice.voting_manager.get_ballot_rights_role(guild_id=ctx.guild.id)
    return voting_role_id in [role.id for role in ctx.author.roles]
