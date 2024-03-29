"""
COGS which handle explanation  on commands available to communicate with the Orderbook Horizon Endpoints from Discord
"""

from nextcord.ext import commands
from nextcord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from stellar_sdk import Asset
from stellar_sdk.exceptions import BadRequestError
from horizonCommands.utils.customMessages import horizon_error_msg

custom_messages = CustomMessages()


class HorizonOrderBook(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.command_string = bot.get_command_str()
        self.server = self.bot.backoffice.stellar_wallet.server

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
        """
        Effects entry point to horizon endpoints
        """
        if ctx.invoked_subcommand is None:
            title = ':book:  __Horizon Order Book Queries__ :book: '
            description = 'Representation of all available commands available to interact with ***Order Book' \
                          '*** Endpoint on Stellar Horizon Server Commands can be used 1/30 seconds/ per user.'

            list_of_commands = [
                {"name": f':currency_exchange:  Query Order Book for pair :currency_exchange: ',
                 "value": f'```{self.command_string}book details <selling asset> <buying asset>```\n'
                          f'__Note__: Assets can be represented as a code or issuer address,'
                          f'`Aliases: get`'},
            ]

            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @book.command(aliases=['get'])
    async def details(self, ctx, selling: str, buying: str):
        selling_asset = self.check_asset(asset_query=selling.upper())

        if self.is_asset(asset_to_check=selling_asset):
            buying_asset = self.check_asset(asset_query=buying.upper())
            if self.is_asset(asset_to_check=buying_asset):
                try:
                    data = self.server.orderbook(selling=selling_asset, buying=buying_asset).call()
                    base_asset_details = data["base"]
                    counter_asset_details = data["counter"]

                    base_details = ''
                    if base_asset_details.get('asset_type') != 'native':
                        base_details += f'{base_asset_details["asset_code"]}\n' \
                                        f'```{base_asset_details["asset_issuer"]}```'
                    else:
                        base_details = 'XLM'

                    counter_details = ''
                    if counter_asset_details.get('asset_type') != 'native':
                        counter_details += f'{counter_asset_details["asset_code"]}\n' \
                                           f'```{counter_asset_details["asset_issuer"]}```'
                    else:
                        counter_details = 'XLM'

                    ask_side = data["asks"]

                    ask_str = str()
                    for a in ask_side[:3]:
                        ask_str += f'{a["amount"]} @ {a["price"]}\n'

                    bid_side = data["bids"]

                    bid_str = str()

                    for b in bid_side[:3]:
                        bid_str += f'{b["amount"]} @ {b["price"]}\n'

                    orderbook_spread = round(float(ask_side[0]['price']) - float(bid_side[0]["price"]), 7)

                    orderbook_embed = Embed(title=f' :book: Order book details :book:',
                                            colour=Colour.light_grey())
                    orderbook_embed.add_field(name=':gem: Base Asset Details :gem:',
                                              value=base_details,
                                              inline=False)
                    orderbook_embed.add_field(name=':gem: Counter Asset Details :gem:',
                                              value=counter_details,
                                              inline=False)
                    orderbook_embed.add_field(name=f':bar_chart: Order Book Spread :bar_chart: ',
                                              value=f'{orderbook_spread}',
                                              inline=False)
                    orderbook_embed.add_field(name=':green_circle: Buy Offers :green_circle: ',
                                              value=f'{bid_str}')
                    orderbook_embed.add_field(name=':red_circle: Sell Offers :red_circle: ',
                                              value=f'{ask_str}')
                    await ctx.author.send(embed=orderbook_embed)
                except BadRequestError as e:
                    extras = e.extras
                    await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])
            else:
                multi_details = Embed(title=f':exclamation:  Multiple Entries Found :exclamation: ',
                                      description='You have received this message because multiple entries have been found'
                                                  f' for Buying asset parameter `{buying}`. Check the list bellow and'
                                                  f' repeat the call however provide issuer address for Selling Asset',
                                      colour=Colour.red())
                await ctx.author.send(embed=multi_details)
                for asset in buying_asset:
                    multi_details.add_field(name=f':bank: Asset Issuer for {asset["asset_code"]} :bank:',
                                            value=f'```{asset["asset_issuer"]}```',
                                            inline=False)
                await ctx.author.send(embed=multi_details)

        else:
            multi_details = Embed(title=f':exclamation:  Multiple Entries Found :exclamation: ',
                                  description='You have received this message because multiple entries have been found'
                                              f' for Selling asset parameter `{selling}`. Check the list bellow and'
                                              f' repeat the call however provide issuer address for Selling Asset',
                                  colour=Colour.red())
            for asset in selling_asset:
                multi_details.add_field(name=f':bank: Asset Issuer for {asset["asset_code"]} :bank:',
                                        value=f'```{asset["asset_issuer"]}```',
                                        inline=False)
            await ctx.author.send(embed=multi_details)


def setup(bot):
    bot.add_cog(HorizonOrderBook(bot))
