"""
File includes custom security checks for the Discord GUI part
"""

from discord import ChannelType


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


def user_has_custodial(ctx):
    """
    Custom check for custodial wallet
    """
    return ctx.bot.backoffice.custodial_manager.second_level_user_reg_status(user_id=ctx.author.id)
