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


class HorizonTrades(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.command_string = bot.get_command_str()
        self.server = server
        self.trade = self.server.trades()

    @commands.group()
    async def trades(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        title = ':currency_exchange:  __Horizon Trades Queries__ :currency_exchange:   '
        description = 'Representation of all available commands available to interact with ***Trades*** Endpoint on ' \
                      'Stellar Horizon Server'
        list_of_commands = [
            {"name": f':map: Trades for Account :map:',
             "value": f'`{self.command_string}trades account <address>`'},
            {"name": f' :map: Offers by Account :map: ',
             "value": f'`{self.command_string}offers account <Account public address>`'}
        ]
        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @trades.command()
    async def account(self, ctx, address: str):
        data = self.trade.for_account(account_id=address).limit(100).order(desc=True).call()
        from pprint import pprint
        pprint(data)


    @trades.command()
    async def pair(self, ctx, base: str, counter: str):
        data = self.trade.for_asset_pair(base=base, counter=counter).limit(100).order(desc=True).call()
        from pprint import pprint
        pprint(data)

    @trades.command()
    async def offer(self, ctx, offer_id: int):
        data = self.trade.for_asset_pair().limit(100).order(desc=True).call()
        from pprint import pprint
        pprint(data)


def setup(bot):
    bot.add_cog(HorizonTrades(bot))
