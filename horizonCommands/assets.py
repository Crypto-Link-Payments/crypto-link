"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Colour
from cogs.utils.systemMessaages import CustomMessages
from discord.ext.commands.errors import CommandInvokeError
from horizonCommands.utils.horizon import server
from horizonCommands.utils.customMessages import send_asset_details, send_multi_asset_case
from stellar_sdk import Asset

custom_messages = CustomMessages()


class HorizonAssets(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.server = server
        self.asset = self.server.assets()

    @commands.group()
    async def assets(self, ctx):
        title = ':gem: __Horizon Assets Queries__ :gem:'
        description = 'Representation of all available commands available to interact with ***Assets*** Endpoint on ' \
                      'Stellar Horizon Server.'
        list_of_commands = [{"name": f':gem: Query by exact details :gem: ',
                             "value": f'`{self.command_string}assets get <asset code> <issuer address>`'},
                            {"name": f':regional_indicator_c: Query by code :regional_indicator_c: ',
                             "value": f'`{self.command_string}assets code <alphanumeric string>`'},
                            {"name": f':map: Query by Issuer Address :map:',
                             "value": f'`{self.command_string}assets issuer <Issuer address>`'}
                            ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @assets.command()
    async def get(self, ctx, asset_code: str, asset_issuer: str):

        data = self.asset.for_code(asset_code=asset_code.upper()).for_issuer(asset_issuer=asset_issuer.upper()).call()
        if data['_embedded']["records"]:
            await send_asset_details(destination=ctx.message.author, data=data, request='***asset***')
        else:
            message = f'Asset with details provided does not exist. Please query for asset either ' \
                      f'by `{self.command_string}assets code {asset_code}` or `{self.command_string}assets issuer` ' \
                      f'to verify details'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=':warning: Asset Code Error :warning: ')

    @assets.command()
    async def code(self, ctx, asset_code: str):
        data = self.asset.for_code(asset_code=asset_code.upper()).call()
        if data:
            records = data['_embedded']['records']
            if len(records) == 1:
                await send_asset_details(destination=ctx.message.author, data=records[0], request='asset code ')

            else:
                await send_multi_asset_case(destination=ctx.message.author, data=data, command_str=self.command_string)
        else:
            message = f'No Asset with code {asset_code} found. Please try again'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title='Asset Code Error')

    @assets.command()
    async def issuer(self, ctx, issuer_addr: str):
        data = self.asset.for_issuer(asset_issuer=issuer_addr).call()

        if data:
            await send_asset_details(destination=ctx.message.author, data=data, request='issuer')

        else:
            message = f' Issuer with address `{issuer_addr} does not exist. Please recheck address and try again'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title='Issuer Does Not Exist')

    @code.error
    async def code_error(self, ctx, error):
        if isinstance(error, CommandInvokeError):
            message = f'Wrong Code provided for asset'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title='Asset Could not be found')


def setup(bot):
    bot.add_cog(HorizonAssets(bot))
