"""
File includes custom security checks for the Discord GUI part
"""

from nextcord import ChannelType, Interaction
from nextcord.ext import application_checks

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


def has_wallet_inter_check():
    def predicate(interaction: Interaction):
        return (
            interaction.client.backoffice.account_mng.check_user_existence(user_id=interaction.user.id)
        )

    return application_checks.check(predicate)


def is_owner(ctx):
    """
    Function checks if the user is owner of the community or not
    """
    return int(ctx.message.author.id) == int(ctx.message.guild.owner_id)


def merchant_com_reg_stats(ctx):
    """
    Checks if community is registered in the merchant system
    """
    try:
        return ctx.bot.backoffice.merchant_manager.check_if_community_exist(community_id=int(ctx.message.guild.id))
    except AttributeError:
        return False


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


def guild_has_merchant(ctx):
    """
    Check if community has activate merchant system
    """
    return ctx.bot.backoffice.merchant_manager.check_if_community_exist(int(ctx.message.guild.id))


def guild_has_stats(ctx):
    """
    Guild registration status check for stats
    """
    return ctx.bot.backoffice.guild_profiles.check_guild_registration_stats(guild_id=ctx.guild.id)


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


def check(author):
    def inner_check(message):
        """
        Check for answering the verification message on withdrawal. Author origin
        """
        if message.author.id == author.id:
            return True
        else:
            return False

    return inner_check


def has_ballot_access(ctx):
    voting_role_id = ctx.bot.backoffice.voting_manager.get_ballot_rights_role(guild_id=ctx.guild.id)
    return voting_role_id in [role.id for role in ctx.author.roles]

