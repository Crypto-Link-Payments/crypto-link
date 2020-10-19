from discord.ext import commands
from cogs.utils.systemMessaages import CustomMessages
from cogs.utils.customCogChecks import user_has_wallet

custom_messages = CustomMessages()

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_ACCOUNT_ERROR = "__Account Not Registered__"


class AssetCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()

    @commands.group()
    @commands.check(user_has_wallet)
    async def asset(self):
        """
        Command Entry Point for Stellar Expert Queries
        """
        pass

    @asset.command()
    async def supply(self):
        """
        Returns the asset_supply for asset
        """
        pass

    @asset.command()
    async def rating(self):
        """
        Returns the raiting on the asset
        """
        pass

    @asset.error
    async def asset_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to user Stellar Expert Commands you need to have wallet registered in the system!. Use' \
                      f' `{self.command_string}register`'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)


def setup(bot):
    bot.add_cog(AssetCommands(bot))
