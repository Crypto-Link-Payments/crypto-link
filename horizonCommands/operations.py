"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers
from horizonCommands.horizonAccess.horizon import server

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'


class HorizonOperations(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.server = server
        self.op = self.server.operations()

    @commands.group()
    async def operations(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        title = ':wrench: __Horizon Operations Queries__ :wrench: '
        description = 'Representation of all available commands available to interact with' \
                      ' ***Operations*** Endpoint on Stellar Horizon Server'
        list_of_commands = [
            {"name": f':tools: Single Operation :tools: ',
             "value": f'`{self.command_string}operations operation <operation id>`'},
            {"name": f' :ledger: Operation by Ledger :ledger: ',
             "value": f'`{self.command_string}operations ledger <ledger id>`'},
            {"name": f' :map: Operation by Account :map: ',
             "value": f'`{self.command_string}operations account <Account public address>`'},
            {"name": f' :hash: Operations for transaction :hash:',
             "value": f'`{self.command_string}operations transaction <Atransaction hash>`'}

        ]
        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @operations.command()
    async def operation(self, operation_id):
        data = self.op.operation(operation_id=operation_id).cal()
        pass

    @operations.command()
    async def account(self, ctx, address: str):
        data = self.op.for_account(account_id=address).call()

    @operations.command()
    async def ledger(self, ledger_id: int):
        data = self.op.for_ledger(sequence=ledger_id).call()

    @operations.command()
    async def transaction(self, ctx, tx_hash: str):
        data = self.op.for_transaction(transaction_hash=tx_hash).call()


def setup(bot):
    bot.add_cog(HorizonOperations(bot))
