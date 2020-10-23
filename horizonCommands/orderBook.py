"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from backOffice.stellarOnChainHandler import StellarWallet
from cogs.utils.systemMessaages import CustomMessages
from stellar_sdk import Asset
from utils.tools import Helpers
from horizonCommands.horizonAccess.horizon import server

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'
stellar_chain = StellarWallet()


class HorizonOrderBook(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.command_string = bot.get_command_str()
        self.server = server

    def check_asset(self, asset_query):

        # Check if it is native
        if asset_query == 'XLM':
            asset = Asset(code='XLM').native()
            return asset

        # Check if asset is alphanumeric 4 or 12
        elif len(asset_query) <= 12:
            asset = self.server.assets().for_code(asset_code=asset_query).call()
            all_assets = asset["_embedded"]['records']

            # If only one asset with code exists
            if len(all_assets) == 1:
                asset = Asset(code=asset_query)
                return asset
            else:
                return all_assets

        # If not alphanumeric than issuer address check required
        else:
            data = self.server.assets().for_issuer(asset_issuer=asset_query).call()
            issuer_assets = data["_embedded"]['records']

            # If issuer only issued one asset
            if len(issuer_assets) == 1:
                asset = Asset(code=issuer_assets[0]['asset_code'], issuer=issuer_assets[0]['asset_issuer'])
                return asset
            else:
                return issuer_assets

    def is_asset(self, asset_to_check):
        if isinstance(asset_to_check, Asset):
            return True
        else:
            return False

    @commands.group()
    async def book(self, ctx):
        pass

    @book.command()
    async def asset(self, ctx, selling: str, buying: str):
        selling_asset = self.check_asset(asset_query=selling.upper())

        if self.is_asset(asset_to_check=selling_asset):
            buying_asset = self.check_asset(asset_query=buying.upper())
            if self.is_asset(asset_to_check=buying_asset):
                print('Initiate Book call')

            else:
                multi_details = Embed(title=f':robot: Multiple Entries Found :robot:',
                                      description='You have received this message because multiple entries have been found'
                                                  f' for Buying asset parameter `{buying}`. Check the list bellow and'
                                                  f' repeat the call however provide issuer address for Selling Asset',
                                      colour=Colour.red())
                for asset in selling_asset:
                    multi_details.add_field(name=f':bank: Asset Issuer for {asset["asset_code"]} :bank:',
                                            value=f'```{asset["asset_issuer"]}``')
                await ctx.author.send(embed=multi_details)



        else:
            multi_details = Embed(title=f':robot: Multiple Entries Found :robot:',
                                  description='You have received this message because multiple entries have been found'
                                              f' for Selling asset parameter `{selling}`. Check the list bellow and'
                                              f' repeat the call however provide issuer address for Selling Asset',
                                  colour=Colour.red())
            for asset in selling_asset:
                multi_details.add_field(name=f':bank: Asset Issuer for {asset["asset_code"]} :bank:',
                                        value=f'```{asset["asset_issuer"]}``')
            await ctx.author.send(embed=multi_details)


def setup(bot):
    bot.add_cog(HorizonOrderBook(bot))
