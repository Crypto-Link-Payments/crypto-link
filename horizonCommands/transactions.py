"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.customCogChecks import has_wallet
from backOffice.stellarOnChainHandler import StellarWallet
from cogs.utils.systemMessaages import CustomMessages

from cogs.utils.securityChecks import check_stellar_address
from utils.tools import Helpers

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'
stellar_chain = StellarWallet()


class HorizonTransactions(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()

    @commands.group()
    async def transactions(self, ctx):
        title = ':office_worker: __Horizon Accounts Operations__ :office_worker:'
        description = 'Representation of all available commands available to interact with ***Account*** Endpoint on ' \
                      'Stellar Horizon Server'
        list_of_commands = [
            {"name": f':new: Create New Account :new: ',
             "value": f'`{self.command_string}accounts create`'},
            {"name": f':new: Query Account Details :new: ',
             "value": f'`{self.command_string}accounts get <Valid Stellar Address>`'}
        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @transactions.command()
    async def single(self, ctx, transaction_hash: str):
        data = stellar_chain.get_transactions_hash(tx_hash=transaction_hash)

    @transactions.command()
    async def account(self, ctx, account_address: str):
        data = stellar_chain.get_transactions_account(address=account_address)

    @transactions.command()
    async def ledger(self, ctx, ledger_id: int):
        data = stellar_chain.get_transactions_ledger(ledger_id=ledger_id)


def setup(bot):
    bot.add_cog(HorizonTransactions(bot))
