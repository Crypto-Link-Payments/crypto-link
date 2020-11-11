"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from re import sub
from cogs.utils.systemMessaages import CustomMessages
from stellar_sdk.exceptions import BadRequestError
from horizonCommands.utils.horizon import server
from horizonCommands.utils.tools import asset_code
from horizonCommands.utils.customMessages import horizon_error_msg

custom_messages = CustomMessages()


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
             "value": f'`{self.command_string}operations transaction <transaction hash>`'}
        ]
        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    async def send_operations_data(self, ctx, data, key_query: str):
        operations = data['_embedded']["records"]
        horizon_query = data['_links']['self']['href']

        effects_info = Embed(title=f':wrench: {key_query} Operations :wrench:  ',
                             description=f'Bellow are last three Operations which happened for {key_query}',
                             colour=Colour.lighter_gray())
        effects_info.add_field(name=f':sunrise: Horizon Access :sunrise: ',
                               value=f'[{key_query} Operations]({horizon_query})')
        effects_info.add_field(name=f':three: Last Three Effects :three: ',
                               value=f':arrow_double_down: ',
                               inline=False)
        await ctx.author.send(embed=effects_info)

        counter = 0
        for op in operations:
            if counter <= 2:
                effect_type = sub('[^a-zA-Z0-9\n\.]', ' ', op["type"])
                eff_embed = Embed(title=f':wrench: {effect_type.capitalize()} :wrench: ',
                                  description=f':id: {op["id"]}',
                                  colour=Colour.lighter_gray())
                eff_embed.add_field(name=f':calendar:  Created :calendar: ',
                                    value=f'`{op["created_at"]}`',
                                    inline=False)
                eff_embed.add_field(name=f':white_circle: Paging Token :white_circle:',
                                    value=f'`{op["paging_token"]}`',
                                    inline=False)
                eff_embed.add_field(name=f':hash: Transaction Hash :hash:',
                                    value=f'`{op["transaction_hash"]}`',
                                    inline=False)
                eff_embed.add_field(name=f':sunrise: Horizon Link :sunrise: ',
                                    value=f'[Effect Link]({op["_links"]["transaction"]["href"]})',
                                    inline=False)

                if effect_type == 'create account':
                    eff_embed.add_field(name=f':map: Source Account :map: ',
                                        value=f'```{op["source_account"]}```',
                                        inline=False)
                    eff_embed.add_field(name=f':map: Account :map:',
                                        value=f'```{op["account"]}```',
                                        inline=False)
                    eff_embed.add_field(name=f':id: ID :id:',
                                        value=f'`{op["id"]}`',
                                        inline=False)

                elif effect_type == 'payment':
                    code = asset_code(op=op)
                    eff_embed.add_field(name=f':cowboy:  Sender :cowboy: ',
                                        value=f'`{op["from"]}`',
                                        inline=False)
                    eff_embed.add_field(name=f':map: Recipient :map:',
                                        value=f'`{op["to"]}`',
                                        inline=False)
                    eff_embed.add_field(name=f':money_with_wings:  Amount :money_with_wings: ',
                                        value=f'`{op["amount"]} {code}`',
                                        inline=False)

                elif effect_type in ['path payment strict send', 'path payment strict receive']:
                    code = asset_code(op=op)
                    eff_embed.add_field(name=f':cowboy: Sender :cowboy: ',
                                        value=f'`{op["from"]}`',
                                        inline=False)
                    eff_embed.add_field(name=f':map: Recipient :map:',
                                        value=f'`{op["to"]}`',
                                        inline=False)
                    eff_embed.add_field(name=f'":bank: Asset Issuer :bank:',
                                        value=f'{op["asset_issuer"]}')
                    eff_embed.add_field(name=f':money_with_wings:  Amount :money_with_wings: ',
                                        value=f'`{op["amount"]} {code}`',
                                        inline=False)
                    eff_embed.add_field(name=f'":bank: Source asset Issuer :bank:',
                                        value=f'{op["source_asset_issuer"]}')
                    eff_embed.add_field(name=f':money_with_wings:  Source Amount :money_with_wings: ',
                                        value=f'`{op["source_amount"]} {op["source_asset_code"]}`',
                                        inline=False)

                elif effect_type in ['manage sell offer', "manage buy offer"]:
                    eff_embed.add_field(name=f':id: Offer ID :id:',
                                        value=f'f{op["offer_id"]}')
                    eff_embed.add_field(name=f':gem: Buying Asset Details :gem:',
                                        value=f':bank:\n```{op["buying_asset_issuer"]}\n'
                                              f'Buying: {op["amount"]} {op["buying_asset_code"]} @ {op["price"]} {op["selling_asset_code"]}',
                                        inline=False)
                    eff_embed.add_field(name=f':bank: Selling Asset Details :bank:',
                                        value=f'```{op["selling_asset_issuer"]}```',
                                        inline=False)

                else:
                    eff_embed.add_field(name=':question: Unhandled Type',
                                        value=f'Type of operation has not been handled yet by the system. Please '
                                              f'inform the Crypto Link Staff to add support for it.\n'
                                              f'Type: {op["type"]}')

                await ctx.author.send(embed=eff_embed)

                counter += 1
            else:
                pass

    @operations.command()
    async def operation(self, ctx, operation_id):
        try:
            data = self.op.operation(operation_id=operation_id).call()
            if data['_embedded']["records"]:
                await self.send_operations_data(ctx=ctx, data=data, key_query='Operation')
            else:
                message = f'No operations found under operation ID`{operation_id}`.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title="No Operations for operation ID")

        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @operations.command()
    async def account(self, ctx, address: str):
        try:
            data = self.op.for_account(account_id=address).include_failed(False).order(desc=True).limit(200).call()
            if data['_embedded']["records"]:
                await self.send_operations_data(ctx=ctx, data=data, key_query='Account')
            else:
                message = f'Account `{address}` has not operations.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title="No Operations for Address")
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @operations.command()
    async def ledger(self, ctx, ledger_id: int):
        try:
            data = self.op.for_ledger(sequence=ledger_id).include_failed(False).order(desc=True).limit(200).call()
            if data['_embedded']["records"]:
                await self.send_operations_data(ctx=ctx, data=data, key_query='Ledger')
            else:
                message = f'No operations for ledger id `{ledger_id}`.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title="No Operations for Ledger")
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @operations.command()
    async def transaction(self, ctx, tx_hash: str):
        try:

            data = self.op.for_transaction(transaction_hash=tx_hash).include_failed(False).order(desc=True).limit(
                200).call()
            if data['_embedded']["records"]:
                await self.send_operations_data(ctx=ctx, data=data, key_query='Transaction')
            else:
                message = f'No operations for transaction with hash `{tx_hash}`.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title="No Operations for Transaction Hash")
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])


def setup(bot):
    bot.add_cog(HorizonOperations(bot))
