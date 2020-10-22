"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from re import sub
from backOffice.stellarOnChainHandler import StellarWallet
from cogs.utils.systemMessaages import CustomMessages
from discord.ext.commands.errors import CommandInvokeError
from cogs.utils.securityChecks import check_stellar_address
from stellar_sdk.asset import Asset
from utils.tools import Helpers

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

    @offers.command()
    async def id(self, offer_id: int):
        pass

    @offers.command()
    async def account(self, side: str, address: str):
        if side == 'seller':
            data = stellar_chain.get_offers_account_seller(address=address)
            print(data)
        elif side == 'buyer':
            pass
        else:
            print('wrong param chosen')

    @offers.command()
    async def asset(self, issuer_id: str):
        pass


def setup(bot):
    bot.add_cog(HorizonOffers(bot))
