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


class HorizonPayments(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()

    @staticmethod
    async def process_server_response(ctx, data):
        payment_details = Embed(title=':mag_right: Payments for Stellar Account :mag_right: ',
                                colour=Colour.lighter_gray())
        payment_details.add_field(name=':map: Account Address :map: ',
                                  value=f'```{data["account_id"]}```',
                                  inline=False)
        payment_details.add_field(name=f'Complete List of Payments',
                                  value=f'{data["_links"]["self"]}')
        await ctx.author.send(embed=payment_details)

        payments = data["_embedded"]["records"]

        for p in payments:
            # Check if transaction type is payment
            if p["type"] == 'payment':
                # Check if transaction was incoming or outgoing
                if p['to'] == p["source_account"]:
                    c = Colour.green()
                else:
                    c = Colour.red()
            else:
                # Some other account action has been done
                c = Colour.purple()

            payment_info = Embed(title=f'Operation Details',
                                 colour=c)
            payment_info.set_author(name=f':id: {p["id"]}')
            payment_info.add_field(name=f'Operation Type',
                                   value=f'`{p["type"]}`')
            payment_info.add_field(name=f'Date and time',
                                   value=f'`{p["created_at"]}`')
            payment_info.add_field(name=f'Paging Token',
                                   value=f'{p["paging_token"]}',
                                   inline=False)
            payment_info.add_field(name='From',
                                   value=f'```{p["from"]}```',
                                   inline=False)
            payment_info.add_field(name='To',
                                   value=f'```{p["to"]}```',
                                   inline=False)
            payment_info.add_field(name=f'Transaction Hash',
                                   value=f'`{p["transaction_hash"]}`')
            payment_info.add_field(name=f'Explorer Link',
                                   value=f'{p["_links"]["transaction"]["href"]}')

            if not p.get('asset_code'):
                payment_info.add_field(name='Amount',
                                       value=f'```{p["amount"]} XLM```',
                                       inline=False)

            else:
                payment_info.add_field(name='Asset Issuer',
                                       value=f'```{p["asset_issuer"]}```',
                                       inline=False)
                payment_info.add_field(name='Amount',
                                       value=f'```{p["amount"]} {p["asset_code"]}```',
                                       inline=False)

            await ctx.author.send(embed=payment_info)

    @commands.group()
    @commands.check(has_wallet)
    async def payments(self, ctx):
        """
        End points for payments
        """
        title = ':money_with_wings:  __Horizon Payments Operations__ :money_with_wings: '
        description = 'Representation of all available commands available to interact with ***Payments*** Endpoint on ' \
                      'Stellar Horizon Server. All commands return last 3 transactions done on account, and explorer' \
                      ' link to access older transactions. All transactions are returned in descending order.'
        list_of_commands = [
            {"name": f':map: Get payments by public address :map: ',
             "value": f'`{self.command_string}horizon account payments address <address>`'},
            {"name": f':ledger:  Get payments based on ledger sequence :ledger:   ',
             "value": f'`{self.command_string}horizon account payments ledger <ledger sequence>``'},
            {"name": f':hash:  Get payments based on transaction hash :hash:',
             "value": f'`{self.command_string}horizon account payments transaction <hash of transaction>``'}
        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands, description=description,
                                                destination=1, c=Colour.lighter_gray())

    @payments.command()
    async def address(self, ctx, address: str):
        if check_stellar_address(address=address):
            data = self.backoffice.stellar_wallet.get_payments_for_account(address=address)
            await self.process_server_response(ctx, data=data)
        else:
            message = f'Address you have provided is not a valid Stellar Lumen Address. Please try again'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)

    @payments.command()
    async def ledger(self, ctx, ledger: int):
        data = self.backoffice.stellar_wallet.get_payments_for_ledger(ledger_sequence=ledger)
        await self.process_server_response(ctx, data=data)

    @payments.command(aliases=["tx"])
    async def transaction(self, ctx, transaction_hash: str):
        data = self.backoffice.stellar_wallet.get_payments_for_tx(transaction_hash=transaction_hash)
        await self.process_server_response(ctx, data=data)

    @payments.error
    async def asset_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to user Stellar Expert Commands you need to have wallet registered in the system!. Use' \
                      f' `{self.command_string}register`'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)

    @ledger.error
    async def ledger_error(self, ctx, error):
        if isinstance(error,commands.BadArgument):
            message = f'Ledger ID is constructed only with numbers.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)


def setup(bot):
    bot.add_cog(HorizonPayments(bot))
