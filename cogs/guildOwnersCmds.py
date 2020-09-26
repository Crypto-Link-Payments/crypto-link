"""
COGS: Help commands for the payment services
"""
import discord
from discord.ext import commands

from cogs.utils.customCogChecks import is_owner
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
customMessages = CustomMessages()
d = helper.read_json_file(file_name='botSetup.json')

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'


class GuildOwnerCmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(is_owner)
    async def explorer(self):
        pass


def setup(bot):
    bot.add_cog(GuildOwnerCmds(bot))
