"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.customCogChecks import has_wallet
from cogs.utils.systemMessaages import CustomMessages
from cogs.utils.securityChecks import check_stellar_address
from horizonCommands.utils.horizon import server

custom_messages = CustomMessages()
CONST_ACCOUNT_ERROR = '__Account Not Registered__'


class HorizonPayments(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.server = server
        self.payment = self.server.payments()

    @staticmethod
    async def process_server_response(ctx, data, query_key: str, user_query: str):

        if query_key == 'address':
            desc = f'Detail for:\n' \
                   f':map:`{user_query}`'
            pass
        elif query_key == "ledger":
            desc = f'Detail for :ledger: {user_query}'
        elif query_key == 'transaction hash':
            desc = f'Detail for \n' \
                   f':hash: `{user_query}`'

        payment_details = Embed(title=f':mag_right: Payments for {query_key.capitalize()} :mag_right: ',
                                description=desc,
                                colour=Colour.lighter_gray())
        payment_details.add_field(name=f':file_folder: Complete List of Payments :file_folder: ',
                                  value=f'[Explorer Link]({data["_links"]["self"]["href"]})')
        payment_details.add_field(name=f'Last 3 Payment activities',
                                  value=f':arrow_double_down:',
                                  inline=False)
        await ctx.author.send(embed=payment_details)

        payments = data["_embedded"]["records"]
        counter = 0

        for p in payments:
            if counter <= 2:
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

                payment_info = Embed(title=f':money_with_wings: {p["type"].capitalize()} Details :money_with_wings: ',
                                     description=f':id: `{p["id"]}` ',
                                     colour=c)
                payment_info.add_field(name=f':calendar: Date and time :calendar: ',
                                       value=f'`{p["created_at"]}`')
                payment_info.add_field(name=f':page_facing_up: Paging Token :page_facing_up: ',
                                       value=f'`{p["paging_token"]}`',
                                       inline=True)
                payment_info.add_field(name=':incoming_envelope: From :incoming_envelope: ',
                                       value=f'```{p["from"]}```',
                                       inline=False)
                payment_info.add_field(name=':map: To :map: ',
                                       value=f'```{p["to"]}```',
                                       inline=False)
                if not p.get('asset_code'):
                    payment_info.add_field(name=':money_mouth: Amount :money_mouth: ',
                                           value=f'```{p["amount"]} XLM```',
                                           inline=False)

                else:
                    payment_info.add_field(name=':bank:  Asset Issuer :bank: ',
                                           value=f'```{p["asset_issuer"]}```',
                                           inline=False)
                    payment_info.add_field(name=':money_mouth: Amount :money_mouth: ',
                                           value=f'```{p["amount"]} {p["asset_code"]}```',
                                           inline=False)

                payment_info.add_field(name=f':hash: Transaction Hash :hash:',
                                       value=f'`{p["transaction_hash"]}`',
                                       inline=False)
                payment_info.add_field(name=f':sunrise: Horizon Link :sunrise: ',
                                       value=f'{p["_links"]["transaction"]["href"]}',
                                       inline=False)

                await ctx.author.send(embed=payment_info)
                counter += 1

    @commands.group()
    @commands.cooldown(1, 30, commands.BucketType.user)
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
             "value": f'`{self.command_string}payments address <address>`'},
            {"name": f':ledger:  Get payments based on ledger sequence :ledger:   ',
             "value": f'`{self.command_string}payments ledger <ledger sequence>`'},
            {"name": f':hash:  Get payments based on transaction hash :hash:',
             "value": f'`{self.command_string}payments transaction <hash of transaction>`'}
        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands, description=description,
                                                destination=1, c=Colour.lighter_gray())

    @payments.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def address(self, ctx, address: str):
        if check_stellar_address(address=address):
            data = self.payment.for_account(account_id=address).order(
                desc=True).limit(limit=200).call()
            await self.process_server_response(ctx, data=data, query_key='address', user_query=f'{address}')
        else:
            message = f'Address you have provided is not a valid Stellar Lumen Address. Please try again'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)

    @payments.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ledger(self, ctx, ledger_sequence: int):
        data = self.payment.for_ledger(sequence=ledger_sequence).order(
            desc=True).limit(limit=200).call()
        records = data['_embedded']['records']
        ledger_info = Embed(title=f':ledger: Ledger {ledger_sequence} Information :ledger:',
                            description='Bellow is represent information for requested ledger.',
                            colour=Colour.lighter_gray())
        ledger_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                              value=f'{data["_links"]["self"]["href"]}')
        await ctx.author.send(embed=ledger_info)
        for record in records:
            if record['type'] == 'create_account':
                action_name = 'Create Account'
            ledger_record = Embed(title=f':bookmark_tabs: {action_name} :bookmark_tabs: ',
                                  description=f'`{record["account"]}`',
                                  colour=Colour.dark_orange())
            ledger_record.add_field(name=f' Source account',
                                    value=f'`{record["source_account"]}`')
            ledger_record.add_field(name=f':calendar: Date and time :calendar: ',
                                    value=f'`{record["created_at"]}`',
                                    inline=False)
            ledger_record.add_field(name=':white_circle: Paging Token :white_circle: ',
                                    value=f'`{record["paging_token"]}`',
                                    inline=False)
            ledger_record.add_field(name=':map: Funder Address :map: ',
                                    value=f'`{record["funder"]}`',
                                    inline=False)
            ledger_record.add_field(name=':moneybag:  Starting Balance :moneybag: ',
                                    value=f'`{record["starting_balance"]} XLM`',
                                    inline=False)
            ledger_record.add_field(name=':hash: Transaction Hash :hash: ',
                                    value=f'`{record["transaction_hash"]}`',
                                    inline=False)
            ledger_record.add_field(name=f':person_running: Ledger Activity :person_running: ',
                                    value=f'[Self]({data["_links"]["self"]["href"]})\n'
                                          f'[Transactions]({record["_links"]["transaction"]["href"]})\n'
                                          f'[Effects]({record["_links"]["effects"]["href"]})\n'
                                          f'[Succeeds]({record["_links"]["succeeds"]["href"]})\n'
                                          f'[Precedes]({record["_links"]["precedes"]["href"]})')
            await ctx.author.send(embed=ledger_record)

    @payments.command(aliases=["tx"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def transaction(self, ctx, transaction_hash: str):
        data = self.payment.for_transaction(transaction_hash=transaction_hash).order(
            desc=True).limit(limit=20).call()
        await self.process_server_response(ctx, data=data, query_key='transaction hash',
                                           user_query=f'{transaction_hash}')

    @payments.error
    async def asset_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to user Stellar Expert Commands you need to have wallet registered in the system!. Use' \
                      f' `{self.command_string}register`'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)

    @ledger.error
    async def ledger_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            message = f'Ledger ID is constructed only with numbers.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)


def setup(bot):
    bot.add_cog(HorizonPayments(bot))
