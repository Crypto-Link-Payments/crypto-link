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
        title = ':incoming_envelope: __Horizon Accounts Operations__ :incoming_envelope:'
        description = 'Representation of all available commands available to interact with ***Account*** Endpoint on ' \
                      'Stellar Horizon Server'
        list_of_commands = [
            {"name": f':hash: Query by transaction Hash :hash: ',
             "value": f'`{self.command_string}transactions single <Transaction Hash>`'},
            {"name": f':map:  Query by account address :map:  ',
             "value": f'`{self.command_string}transactions account <Valid Stellar Address>`'},
            {"name": f':ledger:  Query by ledger :ledger:',
             "value": f'`{self.command_string}transactions ledger <Ledger Number>`'},

        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @staticmethod
    async def process_server_response(ctx, query: str, data, title: str):
        if title == 'ledger':
            emoji = ':ledger'
        elif title == 'Transaction Hash':
            emoji = ':hash:'
        elif title == "account":
            emoji = ':map:'

        payment_details = Embed(title=f':mag_right: {title} Transactions Details :mag_right: ',
                                colour=Colour.lighter_gray())
        payment_details.add_field(name=f'{emoji} {title} {emoji}',
                                  value=f'```{query}```',
                                  inline=False)
        payment_details.add_field(name=f'Full list of request',
                                  value=f'{data["_links"]["self"]}')
        await ctx.author.send(embed=payment_details)

        records = data["_embedded"]["records"]

        counter = 0
        for r in records:
            if counter <= 2:
                signers_data = ', '.join(
                    [f'`{sig}`' for sig in
                     records["signatures"]])

                tx_info = Embed(title=f'Transaction Details',
                                colour=Colour.lighter_gray())
                tx_info.set_author(name=f':id: `{r["id"]}`')
                tx_info.add_field(name=f'Height',
                                  value=f'`{r["paging_token"]}`')
                tx_info.add_field(name=f':ledger:ledger :ledger:',
                                  value=f'`{r["ledger"]}`')
                tx_info.add_field(name=f':hash: Transaction Hash :hash:',
                                  value=f'`{r["hash"]}`')
                tx_info.add_field(name=f'Memo Type',
                                  value=f'`{r["memo_type"]}`')
                tx_info.add_field(name=f':calendar: Date and time :calendar: ',
                                  value=f'`{r["created_at"]}`')
                tx_info.add_field(name=f'Paging Token',
                                  value=f'{r["paging_token"]}',
                                  inline=False)
                tx_info.add_field(name='Source account',
                                  value=f'```{r["source_account"]}```',
                                  inline=False)
                tx_info.add_field(name='Source account Sequence',
                                  value=f'```{r["source_account_sequence"]}```',
                                  inline=False)
                tx_info.add_field(name='Fee account',
                                  value=f'```{r["fee_account"]}```',
                                  inline=False)
                tx_info.add_field(name='Sum of operations',
                                  value=f'```{r["operation_count"]}```',
                                  inline=False)
                tx_info.add_field(name=f'Fees',
                                  value=f'Charged: {r["fee_charged"]}\n'
                                        f'Max: {r["max_fee"]} ')
                tx_info.add_field(name=f'Signers',
                                  value=f'{signers_data}')
                await ctx.author.send(embed=tx_info)
                counter += 1


    @transactions.command()
    async def single(self, ctx, transaction_hash: str):
        data = stellar_chain.get_transactions_hash(tx_hash=transaction_hash)
        await self.process_server_response(ctx=ctx, query=str(transaction_hash), data=data, title='Transaction Hash')

    @transactions.command()
    async def account(self, ctx, account_address: str):
        data = stellar_chain.get_transactions_account(address=account_address)
        await self.process_server_response(ctx=ctx, query=str(account_address), data=data, title='account')

    @transactions.command()
    async def ledger(self, ctx, ledger_id: int):
        data = stellar_chain.get_transactions_ledger(ledger_id=ledger_id)
        await self.process_server_response(ctx=ctx, query=str(ledger_id), data=data, title='Ledger')


def setup(bot):
    bot.add_cog(HorizonTransactions(bot))
