"""
COGS which handle explanation  on commands available to communicate with the Payments Horizon Endpoints from Discord
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from horizonCommands.utils.customMessages import horizon_error_msg, send_payments_details
from stellar_sdk.exceptions import BadRequestError

custom_messages = CustomMessages()
CONST_ACCOUNT_ERROR = '__Account Not Registered__'


class HorizonPayments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_string = bot.get_command_str()
        self.hor_payments = self.bot.backoffice.stellar_wallet.server.payments()
        self.help_functions = bot.backoffice.helper

    @staticmethod
    async def process_server_response(ctx, data, query_key: str, user_query: str):

        if query_key == 'address':
            desc = f'Detail for:\n' \
                   f':map:`{user_query}`'
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
        if ctx.invoked_subcommand is None:
            title = ':money_with_wings:  __Horizon Payments Operations__ :money_with_wings: '
            description = 'Representation of all available commands available to interact with ***Payments*** Endpoint on' \
                          ' Stellar Horizon Server. All commands return last 3 payments done based on query criteria,' \
                          ' and Horizon link is returned with the rest. All payments are returned in descending order.' \
                          ' Commands can be used 1/30 seconds/ per user.'
            list_of_commands = [
                {"name": f':map: Get payments by public address :map: ',
                 "value": f'```{self.command_string}payments address <address>```\n'
                          f'`Aliases: addr`'},
                {"name": f':ledger:  Get payments based on ledger sequence :ledger:   ',
                 "value": f'```{self.command_string}payments ledger <ledger sequence>```'},
                {"name": f':hash:  Get payments based on transaction hash :hash:',
                 "value": f'```{self.command_string}payments transaction <hash of transaction>```\n'
                          f'`Aliases: tx, hash'}
            ]

            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands, description=description,
                                                destination=1, c=Colour.lighter_gray())

    @payments.command(aliases=['addr'])
    async def address(self, ctx, address: str):
        try:
            if self.help_functions.check_public_key(address=address):
                data = self.hor_payments.for_account(account_id=address).order(
                    desc=True).limit(limit=200).call()
                if data['_embedded']['records']:
                    await self.process_server_response(ctx, data=data, query_key='address', user_query=f'{address}')
                else:
                    message = f'Address `{address}` does not have any payments yet.'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                         sys_msg_title="No Payments Found")
            else:
                message = f'Address you have provided is not a valid Stellar Lumen Address. Please try again'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=CONST_ACCOUNT_ERROR)
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @payments.command()
    async def ledger(self, ctx, ledger_sequence: int):
        try:
            data = self.hor_payments.for_ledger(sequence=ledger_sequence).order(
                desc=True).limit(limit=200).call()
            records = data['_embedded']['records']
            if records:
                ledger_info = Embed(title=f':ledger: Ledger {ledger_sequence} Information :ledger:',
                                    description='Bellow is represent information for requested ledger.',
                                    colour=Colour.lighter_gray())
                ledger_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                                      value=f'{data["_links"]["self"]["href"]}')
                await ctx.author.send(embed=ledger_info)

                for record in records:
                    if record['type'] == 'payment':
                        await send_payments_details(destination=ctx.message.author, record=record,
                                                    action_name='Payment')
            else:
                message = f'Ledger `{ledger_sequence}` does not have any payments yet.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=":ledger: No Payments Found :ledger:")
        except BadRequestError as e:
            await horizon_error_msg(destination=ctx.message.author, error=e.extras["reason"])

    @payments.command(aliases=["tx", "hash"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def transaction(self, ctx, transaction_hash: str):
        try:
            data = self.hor_payments.for_transaction(transaction_hash=transaction_hash).order(
                desc=True).limit(limit=20).call()
            if data['_embedded']['records']:
                await self.process_server_response(ctx, data=data, query_key='transaction hash',
                                                   user_query=f'{transaction_hash}')

            else:
                message = f'No Payments for Transaction with :hash:  `{transaction_hash}` found.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=":hash: No Payments Found :hash:")

        except BadRequestError as e:
            await horizon_error_msg(destination=ctx.message.author, error=e.extras["reason"])

    @ledger.error
    async def ledger_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            message = f'Ledger ID is constructed only with numbers.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)


def setup(bot):
    bot.add_cog(HorizonPayments(bot))
