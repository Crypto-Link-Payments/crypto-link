"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from backOffice.stellarOnChainHandler import StellarWallet
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers
from horizonCommands.horizonAccess.horizon import server

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'
stellar_chain = StellarWallet()


class HorizonOffers(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.server = server
        self.offer = self.server.offers()

    @commands.group()
    async def offers(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        title = ':fireworks:  __Horizon Effects Queries__ :fireworks: '
        description = 'Representation of all available commands available to interact with ***Effects*** Endpoint on ' \
                      'Stellar Horizon Server'
        list_of_commands = [
            {"name": f':map: Single Offer Query :map:',
             "value": f'`{self.command_string}offers single <offer id>`'},
            {"name": f' :ledger: Offers by Account:ledger: ',
             "value": f'`{self.command_string}offers account <Account public address>`'}
        ]
        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    async def send_offer_info(self, ctx, offer: dict):

        offer_details = Embed(title=f':id: {offer["id"]} :id:',
                              colour=Colour.lighter_gray())
        offer_details.add_field(name=f':sunrise: Horizon Links :sunrise:',
                                value=f'[Offer]({offer["_links"]["self"]["href"]})\n'
                                      f'[Maker]({offer["_links"]["offer_maker"]["href"]})',
                                inline=False)
        offer_details.add_field(name=f':calendar: Last Modified :calendar: ',
                                value=f'{offer["last_modified_time"]}',
                                inline=False)
        offer_details.add_field(name=f':white_circle: Paging Token :white_circle:',
                                value=f'{offer["paging_token"]}',
                                inline=False)
        offer_details.add_field(name=f':map: Seller Details :map:',
                                value=f'```{offer["seller"]}```',
                                inline=False)

        selling_string = ''

        if offer["selling"]["asset_type"] != 'native':
            selling_string += f'{offer["amount"]} {offer["selling"]["asset_code"]} @ '
        else:
            selling_string += f'{offer["amount"]} XLM @ '

        if offer['buying']['asset_type'] != 'native':
            selling_string += f' {offer["price"]} {offer["buying"]["asset_code"]}/1'

        else:
            selling_string += f' {offer["price"]}/XLM @'

        offer_details.add_field(name=f':handshake: Offer Details :handshake: ',
                                value=f'`{selling_string}`',
                                inline=False)

        # Process issuing account
        asset_issuers = ''
        if offer['buying']['asset_type'] != 'native':
            asset_issuers += f':gem: {offer["buying"]["asset_code"]} :gem:\n' \
                             f'```{offer["buying"]["asset_issuer"]}```'
        else:
            asset_issuers += f':coin:  XLM :coin: \n' \
                             f'```Native Currency```'

        if offer['selling']['asset_type'] != 'native':
            asset_issuers += f'\n:gem: Selling {offer["selling"]["asset_code"]} :gem:\n' \
                             f'```{offer["selling"]["asset_issuer"]}```\n'
        else:
            asset_issuers += f':coin: XLM :coin: \n' \
                             f'```Native Currency```'

        offer_details.add_field(name=f':bank: Asset Issuers :bank:',
                                value=asset_issuers,
                                inline=False)

        await ctx.author.send(embed=offer_details)

    @offers.command()
    async def single(self, ctx, offer_id: int):
        data = self.offer.offer(offer_id=offer_id).call()
        await self.send_offer_info(ctx=ctx, offer=data)

    @offers.command()
    async def address(self, ctx, address: str):
        data = self.offer.account(account_id=address).limit(100).order(desc=True)


def setup(bot):
    bot.add_cog(HorizonOffers(bot))
