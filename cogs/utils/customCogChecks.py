"""
File includes custom security checks for the Discord GUI part
"""

from discord import ChannelType

from backOffice.merchatManager import MerchantManager
from backOffice.profileRegistrations import AccountManager
from utils.tools import Helpers
from backOffice.guildServicesManager import GuildProfileManagement

helper = Helpers()
d = helper.read_json_file(file_name='botSetup.json')
merchant_manager = MerchantManager()
account_mng = AccountManager()
guild_manager = GuildProfileManagement()


def is_animus(ctx):
    """
    Check if creator
    """
    return ctx.message.author.id == d['creator']


def is_one_of_gods(ctx):
    list_of_gods = [d['ownerId'], d['creator']]
    return [god for god in list_of_gods if god == ctx.message.author.id]


def is_public(ctx):
    """
    Check if channel is public where command has been executed
    :param ctx: Discord Context
    :return: Boolean
    """
    return ctx.message.channel.type != ChannelType.private


def has_wallet(ctx):
    """
    Check if user has already registered personal wallet to the system
    :param ctx: Context
    :return: Boolean
    """
    return account_mng.check_user_existence(user_id=ctx.message.author.id)


def is_owner(ctx):
    """
    Function checks if the user is owner of the community or not
    """
    return int(ctx.message.author.id) == int(ctx.message.guild.owner.id)


def merchant_com_reg_stats(ctx):
    """
    Checks if community is registered in the merchant system
    """
    try:
        return merchant_manager.check_if_community_exist(community_id=int(ctx.message.guild.id))
    except AttributeError:
        return False


def community_missing(ctx):
    """
    Check if community not registered in the system
    """
    return merchant_manager.check_if_community_does_not_exist(community_id=ctx.message.guild.id)


def user_has_wallet(ctx):
    """
    Check if user has wallet registered in the system
    """
    return account_mng.check_user_existence(user_id=ctx.message.author.id)


def guild_has_merchant(ctx):
    """
    Check if community has activate merchant system
    """
    return merchant_manager.check_if_community_exist(int(ctx.message.guild.id))


def guild_has_stats(ctx):
    """
    Guild registration status check for stats
    """
    return guild_manager.check_guild_registration_stats(guild_id=ctx.guild.id)
