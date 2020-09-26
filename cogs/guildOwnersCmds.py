"""
COGS: Help commands for the payment services
"""
import discord
from discord.ext import commands
from discord import TextChannel
from backOffice.guildServicesManager import GuildProfileManagement

from cogs.utils.customCogChecks import is_owner, is_public
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
guild_manager = GuildProfileManagement()
customMessages = CustomMessages()
d = helper.read_json_file(file_name='botSetup.json')

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'


class GuildOwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(is_owner)
    @commands.check(is_public)
    async def owner(self):
        pass

    @commands.group()
    @commands.check(is_owner)
    async def register(self, ctx):
        if not guild_manager.check_guild_registration_stats(guild_id=ctx.guild.id):
            new_guild = {
                "guildId": ctx.guild.id,
                "guildName": f'{ctx.guild}',
                "explorerSettings": {"channelId": int(0)},
                "txFees": {"xlmFeeValue": int(0)},
                "communityStats": {"xlmVolume": float(0.0),
                                   "clTokenVolume": float(0.0),
                                   "txCount": int(0),
                                   "privateCount": int(0),
                                   "publicCount": int(0),
                                   "roleTxCount": int(0),
                                   "emojiTxCount": int(0),
                                   "multiTxCount": int(0)}
            }
            await guild_manager.register_guild(guild_data=new_guild)

            await customMessages.system_message(ctx=ctx, color_code=0,
                                                message='You have successfully registered guild into the system',
                                                destination=ctx.message.author, sys_msg_title='__System Message__')
        else:
            await customMessages.system_message(ctx=ctx, color_code=1, message='Guild already registered',
                                                destination=ctx.message.channel, sys_msg_title='__System error__')

    @owner.command()
    async def stats(self):
        pass

    @owner.commmand()
    async def services(self):
        """
        Pull status of services
        """
        pass

    @owner.group()
    async def explorer(self):
        pass

    @explorer.command()
    async def apply(self, ctx, chn: TextChannel):
        pass

    @explorer.command()
    async def remove(self, ctx, chn: TextChannel):
        pass

    @owner.group()
    async def fees(self, ctx):
        pass

    @fees.command()
    async def set(self, ctx, xlm: float):
        pass


def setup(bot):
    bot.add_cog(GuildOwnerCommands(bot))
