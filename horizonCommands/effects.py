"""
COGS which handle explanation  on commands available to communicate with the Effects Horizon Endpoints from Discord
"""

from discord.ext import commands
from discord import Colour

from cogs.utils.systemMessaages import CustomMessages
from stellar_sdk.exceptions import BadRequestError
from horizonCommands.utils.customMessages import send_effects, send_effect_details, horizon_error_msg

custom_messages = CustomMessages()

CONST_ACCOUNT_ERROR = '__Account Not Registered__'


class HorizonEffects(commands.Cog):
    """
    Discord Commands to access Effects endpoints
    """

    def __init__(self, bot):
        self.bot = bot
        self.command_string = bot.get_command_str()
        self.hor_effects = self.bot.backoffice.stellar_wallet.server.effects()
        self.help_functions = bot.backoffice.helper

    @commands.group(aliases=["ef", 'effect'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def effects(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        title = ':fireworks:  __Horizon Effects Queries__ :fireworks: '
        description = 'Representation of all available commands available to interact with ***Effects*** Endpoint on ' \
                      'Stellar Horizon Server. Commands can be used 1/30 seconds/ per user.\n' \
                      '`Aliases: ef, effect`'
        list_of_commands = [
            {"name": f':map: Query effects for account :map:',
             "value": f'```{self.command_string}effects account <public account address>```\n'
                      f'`aliases: acc, addr, address`'},
            {"name": f' :ledger: Query effects for ledger :ledger: ',
             "value": f'```{self.command_string}effects ledger <ledger id>```'},
            {"name": f':wrench: Query effects for operations :wrench: ',
             "value": f'```{self.command_string}effects operations <operation id>```\n'
                      f'`aliases: op`'},
            {"name": f':hash: Query effects for transactions :hash: ',
             "value": f'```{self.command_string}effects transaction <transaction hash>```\n'
                      f'`aliases: tx, hash`'}
        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @effects.command(aliases=["acc", "addr", "address"])
    async def account(self, ctx, address: str):
        if self.help_functions.check_public_key(address=address):
            try:
                data = self.hor_effects.for_account(account_id=address).call()
                await send_effects(destination=ctx.message.author, data=data, usr_query=f'{address}',
                                   key_query='Account')

                effects = data['_embedded']["records"]
                counter = 0
                for effect in effects:
                    if counter <= 2:
                        await send_effect_details(destination=ctx.message.author, effect=effect)
                        counter += 1
                    else:
                        pass
            except BadRequestError as e:
                extras = e.extras
                await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

        else:
            message = f'Address you have provided is not a valid Stellar Lumen Address. Please try again'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)

    @effects.command()
    async def ledger(self, ctx, ledger_id: int):
        try:
            data = self.hor_effects.for_ledger(sequence=ledger_id).call()
            await send_effects(destination=ctx.message.author, data=data, usr_query=f'{ledger_id}',
                               key_query='Ledger')
            effects = data['_embedded']["records"]
            counter = 0
            for effect in effects:
                if counter <= 2:
                    await send_effect_details(destination=ctx.message.author, effect=effect)
                    counter += 1
                else:
                    pass
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @effects.command(aliases=['op'])
    async def operation(self, ctx, operation_id: int):
        try:
            data = self.hor_effects.for_operation(operation_id=operation_id).call()
            await send_effects(destination=ctx.message.author, data=data, usr_query=f'{operation_id}',
                               key_query='Operation')
            effects = data['_embedded']["records"]
            counter = 0
            for effect in effects:
                if counter <= 2:
                    await send_effect_details(destination=ctx.message.author, effect=effect)
                    counter += 1
                else:
                    pass
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @effects.command(aliases=["tx", "hash"])
    async def transaction(self, ctx, tx_hash: str):
        try:
            data = self.hor_effects.for_transaction(transaction_hash=tx_hash).call()
            await send_effects(destination=ctx.message.author, data=data, usr_query=f'{tx_hash}',
                               key_query='Transaction Hash')
            effects = data['_embedded']["records"]
            counter = 0
            for effect in effects:
                if counter <= 2:
                    await send_effect_details(destination=ctx.message.author, effect=effect)
                    counter += 1
                else:
                    pass
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])


def setup(bot):
    bot.add_cog(HorizonEffects(bot))
