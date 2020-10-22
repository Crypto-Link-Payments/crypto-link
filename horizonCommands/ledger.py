"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
import requests
from discord import Embed, Colour
from cogs.utils.customCogChecks import has_wallet
from cogs.utils.systemMessaages import CustomMessages
from horizonCommands.horizonAccess.horizon import server

from cogs.utils.securityChecks import check_stellar_address
from utils.tools import Helpers

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'


class HorizonLedger(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.server = server
        self.ledg = self.server.ledgers()

    @commands.command()
    async def ledger(self, ctx, ledger_number: int):
        data = self.ledg.ledger(sequence=ledger_number)
        if data:
            operations_count = len(
                requests.get(f'https://horizon-testnet.stellar.org/ledgers/{ledger_number}/operations').json()[
                    '_embedded'][
                    "records"])
            effects_count = len(
                requests.get(f'https://horizon-testnet.stellar.org/ledgers/{ledger_number}/effects').json()[
                    '_embedded'][
                    "records"])
            payments_count = len(
                requests.get(f'https://horizon-testnet.stellar.org/ledgers/{ledger_number}/payments').json()[
                    '_embedded'][
                    "records"])
            transactions_count = len(
                requests.get(f'https://horizon-testnet.stellar.org/ledgers/{ledger_number}/transactions').json()[
                    '_embedded'][
                    "records"])

            ledger_info = Embed(title=f':ledger: Ledger :id: {ledger_number} Information :ledger:',
                                description='Bellow is represent information for requested ledger.',
                                colour=Colour.lighter_gray())
            ledger_info.add_field(name=':white_circle: Paging Token :white_circle: ',
                                  value=f'`{data["paging_token"]}`',
                                  inline=False)
            ledger_info.add_field(name=':timer: Closing Time :timer: ',
                                  value=f'{data["closed_at"]}')
            ledger_info.add_field(name=':hash: Ledger Hash :hash:',
                                  value=f'`{data["hash"]}`',
                                  inline=False)
            ledger_info.add_field(name=':abacus: Transaction Count :abacus: ',
                                  value=f'`{data["successful_transaction_count"]}`',
                                  inline=False)
            ledger_info.add_field(name=':wrench: Operations Count :wrench: ',
                                  value=f'`{data["operation_count"]}`',
                                  inline=False)
            ledger_info.add_field(name=':x: Failed Transactions :x: ',
                                  value=f'`{data["failed_transaction_count"]}`',
                                  inline=False)
            ledger_info.add_field(name=':moneybag: Total Existing XLM :moneybag: ',
                                  value=f'`{data["total_coins"]} XLM`',
                                  inline=False)
            ledger_info.add_field(name=':money_mouth: Base Fee :money_mouth: ',
                                  value=f'`{format(round(data["base_fee_in_stroops"] / 10000000, 7), ".7f")} XLM`',
                                  inline=False)
            ledger_info.add_field(name=':bath: Fee Pool :bath: ',
                                  value=f'`{data["fee_pool"]} XLM`',
                                  inline=False)
            ledger_info.add_field(name=':arrow_forward: Protocol Version :arrow_forward: ',
                                  value=f'`{data["protocol_version"]}`',
                                  inline=False)
            ledger_info.add_field(name=f':person_running: Ledger Activity :person_running: ',
                                  value=f'Operations: [{operations_count}]({data["_links"]["operations"]["href"]}) \n'
                                        f'Effects: [{effects_count}]({data["_links"]["effects"]["href"]})\n'
                                        f'Payments: [{payments_count}]({data["_links"]["payments"]["href"]}) \n'
                                        f'Transactions: [{transactions_count}]({data["_links"]["transactions"]["href"]})')
            ledger_info.set_footer(text='Click on number to expand details')
            await ctx.author.send(embed=ledger_info)

    @ledger.error
    async def ledger_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            message = f'Ledger ID is constructed only with numbers.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)


def setup(bot):
    bot.add_cog(HorizonLedger(bot))
