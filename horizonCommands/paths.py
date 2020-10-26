"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers
from cogs.utils.securityChecks import check_stellar_address
from horizonCommands.horizonAccess.horizon import server
from stellar_sdk import Asset, PathPayment

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'


class HorizonPaths(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.command_string = bot.get_command_str()
        self.server = server

    async def send_record(self, ctx, data: dict):
        record_info = Embed(title=':record_button: Record Info :record_button: ',
                            colour=Colour.lighter_gray())
        record_info.add_field(name=f':gem: Source Asset :gem:',
                              value=f'`{data["source_asset_code"]}`',
                              inline=False)
        record_info.add_field(name=f':gem: Destination Asset :gem:',
                              value=f'`{data["destination_asset_code"]}`',
                              inline=False)
        record_info.add_field(name=f':money_with_wings:  Destination Amount :money_with_wings: ',
                              value=f'`{data["destination_amount"]} {data["destination_asset_code"]}`')

        counter = 0

        path_str = str()
        for p in data["path"]:
            if p["asset_type"] == 'native':
                path_str += f'***{counter}.*** `XLM`\n========\n'
            else:
                path_str += f'***{counter}.*** `{p["asset_code"]}`\n ```{p["asset_issuer"]}```========\n'
            counter += 1
        record_info.add_field(name=':railway_track: Paths :railway_track: ',
                              value=path_str,
                              inline=False)
        await ctx.author.send(embed=record_info)

    @commands.group()
    async def paths(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        title = ':railway_track:  __Horizon Paths Queries__ :railway_track:'
        description = 'Representation of all available commands available to interact with ***Paths*** Endpoint on ' \
                      'Stellar Horizon Server'
        list_of_commands = [
            {"name": f':service_dog: Find Strict Send Payment Paths',
             "value": f'`{self.command_string}paths send <to address> <amount> <asset> <issuer>`\n'
                      f'***__Note__***: Issuer can be None if asset is Native'},
            {"name": f':mag_right:  Find Strict Receive Payment Paths :mag:',
             "value": f'`{self.command_string}paths find <from address> <amount> <asset_codes> <asset isser>`\n'
                      f'***__Note__***: Issuer can be None if asset is Native'},
        ]
        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @paths.command()
    async def send(self, ctx, to_address: str, source_amount: float, source_asset: str, issuer: str = None):
        atomic_value = (int(source_amount * (10 ** 7)))
        normal = (atomic_value / (10 ** 7))

        # Validate stellar address structure
        if check_stellar_address(address=to_address) and check_stellar_address(issuer):
            if source_asset.upper() != 'XLM':
                source_asset = Asset(code=source_asset.upper(), issuer=issuer)
            else:
                source_asset = Asset(code='XLM').native()

            data = self.server.strict_send_paths(source_asset=source_asset, source_amount=normal,
                                                 destination=to_address).call()
            last_three_records = data["_embedded"]["records"][:3]

            query_info = Embed(title=f':mag_right: Strict Send Payment Search :mag:',
                               description='Bellow is information for 3 results returned from network',
                               colour=Colour.lighter_gray())
            query_info.add_field(name=f':map: To Address :map:',
                                 value=f'```{to_address}```',
                                 inline=False)
            query_info.add_field(name=f':moneybag: Source Asset :moneybag: ',
                                 value=f'`{normal} {source_asset}`',
                                 inline=False)

            if issuer:
                query_info.add_field(name=f':bank: Issuer :bank:',
                                     value=f'```{issuer}```',
                                     inline=False)
            await ctx.author.send(embed=query_info)

            for r in last_three_records:
                await self.send_record(ctx, data=r)

    @paths.command()
    async def receive(self, ctx, from_address: str, received_amount: float, asset_code: str, asset_issuer: str = None):

        atomic_value = (int(received_amount * (10 ** 7)))
        normal = (atomic_value / (10 ** 7))

        # Validate stellar address structure
        if check_stellar_address(address=from_address) and check_stellar_address(asset_issuer):
            if asset_code.upper() != 'XLM':
                destination_asset = Asset(code=asset_code.upper(), issuer=asset_issuer)
            else:
                destination_asset = Asset(code='XLM').native()

            data = self.server.strict_receive_paths(destination_asset=destination_asset,
                                                    destination_amount=normal).call()
            last_three_records = data["_embedded"]["records"][:3]

            query_info = Embed(title=f':mag_right: Strict Send Payment Search :mag:',
                               description='Bellow is information for 3 results returned from network',
                               colour=Colour.lighter_gray())
            query_info.add_field(name=f':map: From Address :map:',
                                 value=f'```{from_address}```',
                                 inline=False)
            query_info.add_field(name=f':moneybag: Source Asset :moneybag: ',
                                 value=f'`{normal} {asset_code}`',
                                 inline=False)

            if asset_issuer:
                query_info.add_field(name=f':bank: Issuer :bank:',
                                     value=f'```{asset_issuer}```',
                                     inline=False)
            await ctx.author.send(embed=query_info)

            for r in last_three_records:
                await self.send_record(ctx, data=r)


def setup(bot):
    bot.add_cog(HorizonPaths(bot))
