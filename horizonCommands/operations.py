"""
COGS which handle explanation  on commands available to communicate with the Operations Horizon Endpoints from Discord
"""

from discord.ext import commands
from discord import Embed, Colour
from re import sub
from cogs.utils.systemMessaages import CustomMessages
from stellar_sdk.exceptions import BadRequestError
from horizonCommands.utils.tools import asset_code
from horizonCommands.utils.customMessages import horizon_error_msg, send_operations_basic_details

custom_messages = CustomMessages()


class HorizonOperations(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.command_string = bot.get_command_str()
        self.hor_operations = self.bot.backoffice.stellar_wallet.server.operations()

    @commands.group(aliases=['op'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def operations(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        title = ':wrench: __Horizon Operations Queries__ :wrench: '
        description = 'Representation of all available commands available to interact with' \
                      ' ***Operations*** Endpoint on Stellar Horizon Server.  Commands ' \
                      'can be used 1/30 seconds/ per user.\n' \
                      '`Aliases: op`'
        list_of_commands = [
            {"name": f' :map: Operation by Account :map: ',
             "value": f'```{self.command_string}operations account <Account public address>```\n'
                      f'`Aliases: acc, addr`'},

            {"name": f':tools: Single Operation :tools: ',
             "value": f'```{self.command_string}operations operation <operation id>```\n'
                      f'`Aliases: id`'},
            {"name": f' :hash: Operations for transaction hash :hash:',
             "value": f'```{self.command_string}operations transaction <transaction hash>```\n'
                      f'`Aliases: hash, tx`'},
            {"name": f' :ledger: Operation by Ledger :ledger: ',
             "value": f'```{self.command_string}operations ledger <ledger id>```'}
        ]
        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    async def send_operations_data(self, ctx, data):
        operations = data['_embedded']["records"]
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
                await ctx.author.send(content='There are more effects so please user Stellar'
                                              ' Laboratory for complete overview')

    @operations.command(aliases=["id"])
    async def operation(self, ctx, operation_id):
        try:
            data = self.hor_operations.operation(operation_id=operation_id).call()
            if data['_embedded']["records"]:
                await send_operations_basic_details(destination=ctx.message.author, key_query="Operation",
                                                    hrz_link=data['_links']['self']['href'])

                await self.send_operations_data(ctx=ctx, data=data)
            else:
                message = f'No operations found under operation ID`{operation_id}`.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title="No Operations for operation ID")

        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @operations.command(aliases=['acc', 'addr'])
    async def account(self, ctx, address: str):
        try:
            data = self.hor_operations.for_account(account_id=address).include_failed(False).order(desc=True).limit(
                200).call()
            if data['_embedded']["records"]:
                await send_operations_basic_details(destination=ctx.message.author, key_query="Account",
                                                    hrz_link=data['_links']['self']['href'])
                await self.send_operations_data(ctx=ctx, data=data)
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
            data = self.hor_operations.for_ledger(sequence=ledger_id).include_failed(False).order(desc=True).limit(
                200).call()
            if data['_embedded']["records"]:
                await send_operations_basic_details(destination=ctx.message.author, key_query="Ledger",
                                                    hrz_link=data['_links']['self']['href'])
                await self.send_operations_data(ctx=ctx, data=data)
            else:
                message = f'No operations for ledger id `{ledger_id}`.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title="No Operations for Ledger")
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @operations.command(aliases=["hash", "tx"])
    async def transaction(self, ctx, tx_hash: str):
        try:

            data = self.hor_operations.for_transaction(transaction_hash=tx_hash).include_failed(False).order(
                desc=True).limit(
                200).call()
            if data['_embedded']["records"]:
                await send_operations_basic_details(destination=ctx.message.author, key_query="Transaction",
                                                    hrz_link=data['_links']['self']['href'])
                await self.send_operations_data(ctx=ctx, data=data)
            else:
                message = f'No operations for transaction with hash `{tx_hash}`.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title="No Operations for Transaction Hash")
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])


def setup(bot):
    bot.add_cog(HorizonOperations(bot))
