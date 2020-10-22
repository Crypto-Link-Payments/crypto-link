"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from backOffice.stellarOnChainHandler import StellarWallet
from cogs.utils.systemMessaages import CustomMessages
from discord.ext.commands.errors import CommandInvokeError
from utils.tools import Helpers

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'
stellar_chain = StellarWallet()


class HorizonEffects(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()

    @commands.group()
    async def effects(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        title = ':fireworks:  __Horizon Effects Queries__ :fireworks: '
        description = 'Representation of all available commands available to interact with ***Effects*** Endpoint on ' \
                      'Stellar Horizon Server'
        list_of_commands = [
            {"name": f':map: Query effects for account :map:',
             "value": f'`{self.command_string}effects account <public account address>`'},
            {"name": f' :ledger: Query effects for ledger :ledger: ',
             "value": f'`{self.command_string}effects ledger <ledger id>`'},
            {"name": f':wrench: Query effects for operations :wrench: ',
             "value": f'`{self.command_string}effects operations <operation id>`'},
            {"name": f':hash: Query effects for transactions :hash: ',
             "value": f'`{self.command_string}effects transaaction <transaction hash>`'}

        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @effects.command()
    async def account(self, address: str):
        pass

    @effects.command()
    async def ledger(self, ledger_id: int):
        pass

    @effects.command()
    async def operation(self, operation_id: int):
        pass

    @effects.command()
    async def transaction(self, tx_hash: str):
        pass


def setup(bot):
    bot.add_cog(HorizonEffects(bot))
