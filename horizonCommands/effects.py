"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from re import sub
from cogs.utils.systemMessaages import CustomMessages
from cogs.utils.securityChecks import check_stellar_address
from utils.tools import Helpers
from horizonCommands.utils.horizon import server

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'


class HorizonEffects(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.server = server
        self.effect = self.server.effects()

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

    @staticmethod
    async def send_effects_to_user(ctx, data: dict, usr_query: str, key_query: str):
        effects = data['_embedded']["records"]
        horizon_query = data['_links']['self']['href']

        effects_info = Embed(title=f':fireworks: {key_query} Effects :fireworks:  ',
                             description=f'Bellow are last three effects which happened for {usr_query}',
                             colour=Colour.lighter_gray())
        effects_info.add_field(name=f':sunrise: Horizon Access :sunrise: ',
                               value=f'[{key_query} Effects]({horizon_query})')
        effects_info.add_field(name=f':three: Last Three Effects :three: ',
                               value=f':arrow_double_down: ',
                               inline=False)
        await ctx.author.send(embed=effects_info)

        counter = 0
        for effect in effects:
            if counter <= 2:
                effect_type = sub('[^a-zA-Z0-9\n\.]', ' ', effect["type"])
                eff_embed = Embed(title=f':fireworks: {effect_type.capitalize()} :fireworks: ',
                                  colour=Colour.lighter_gray())
                eff_embed.add_field(name=f':calendar:  Created :calendar: ',
                                    value=f'`{effect["created_at"]}`',
                                    inline=False)
                eff_embed.add_field(name=f':white_circle: Paging Token :white_circle:',
                                    value=f'`{effect["paging_token"]}`')
                eff_embed.add_field(name=f':map: Account :map:',
                                    value=f'```{effect["account"]}```',
                                    inline=False)
                eff_embed.add_field(name=f':id: ID :id:',
                                    value=f'`{effect["id"]}`',
                                    inline=False)
                eff_embed.add_field(name=f':sunrise: Horizon Link :sunrise: ',
                                    value=f'[Effect Link]({effect["_links"]["operation"]["href"]})',
                                    inline=False)
                await ctx.author.send(embed=eff_embed)
                counter += 1
            else:
                pass

    @effects.command()
    async def account(self, ctx, address: str):
        if check_stellar_address(address=address):
            data = self.effect.for_account(account_id=address).call()
            await self.send_effects_to_user(ctx=ctx, data=data, usr_query=f'{address}', key_query='Account')

        else:
            message = f'Address you have provided is not a valid Stellar Lumen Address. Please try again'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)

    @effects.command()
    async def ledger(self, ctx, ledger_id: int):
        data = self.effect.for_ledger(sequence=ledger_id).call()
        await self.send_effects_to_user(ctx=ctx, data=data, usr_query=f'{ledger_id}', key_query='Ledger')

    @effects.command()
    async def operation(self, ctx, operation_id: int):
        data = self.effect.for_operation(operation_id=operation_id).call()
        await self.send_effects_to_user(ctx=ctx, data=data, usr_query=f'{operation_id}', key_query='Operation')

    @effects.command()
    async def transaction(self, ctx, tx_hash: str):
        data = self.effect.for_transaction(transaction_hash=tx_hash).call()
        await self.send_effects_to_user(ctx=ctx, data=data, usr_query=f'{tx_hash}', key_query='Transaction Hash')


def setup(bot):
    bot.add_cog(HorizonEffects(bot))
