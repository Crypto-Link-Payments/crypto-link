"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
import requests
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


class HorizonLedger(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()

    @commands.command()
    async def ledger(self, ctx, ledger_number: int):
        data = self.backoffice.stellar_wallet.get_ledger_information(ledger_id=ledger_number)
        if data:
            operations_count = len(requests.get(data['_links']["operations"]['href']).json()['_embedded'][
                                       "records"])
            effects_count = len(requests.get(data['_links']["effects"]['href']).json()['_embedded'][
                                    "records"])
            payments_count = len(requests.get(data['_links']["payments"]['href']).json()['_embedded'][
                                     "records"])
            transactions_count = len(requests.get(data['_links']["transactions"]['href']).json()['_embedded'][
                                         "records"])

            ledger_info = Embed(title=':ledger: Ledger Information :ledger:',
                                description='Bellow is represent information for requested ledger.',
                                colour=Colour.lighter_gray())
            ledger_info.set_author(name=f':id: {ledger_number}')
            ledger_info.add_field(name='Paging Token',
                                  value=f'`{data["paging_token"]}`',
                                  inline=False)
            ledger_info.add_field(name='Closing time',
                                  value=f'{data["closed_at"]}')
            ledger_info.add_field(name=':hash: Ledger Hash :hash:',
                                  value=f'`{data["hash"]}`',
                                  inline=False)
            ledger_info.add_field(name='Transaction Count',
                                  value=f'`{data["successful_transaction_count"]}`',
                                  inline=False)
            ledger_info.add_field(name='Operations Count',
                                  value=f'`{data["operation_count"]}`',
                                  inline=False)
            ledger_info.add_field(name='Failed Transactions',
                                  value=f'`{data["failed_transaction_count"]}`',
                                  inline=False)
            ledger_info.add_field(name='Total Existing XLM',
                                  value=f'`{data["total_coins"]} XLM`',
                                  inline=False)
            ledger_info.add_field(name='Base Fee',
                                  value=f'`{round(data["base_fee_in_stroops"] / 10000000, 7)} XLM`',
                                  inline=False)
            ledger_info.add_field(name='Fee Pool',
                                  value=f'`{data["fee_pool"]} XLM`',
                                  inline=False)
            ledger_info.add_field(name='Protocol Version',
                                  value=f'`{data["protocol_version"]}`',
                                  inline=False)
            ledger_info.add_field(name=f'Effect For Ledger',
                                  value=f'Operations: [{operations_count}]({data["_links"]["operations"]["href"]}) \n'
                                        f'Effects: [{effects_count}]({data["_links"]["effects"]["href"]})'
                                        f'Payments: [{payments_count}]({data["_links"]["payments"]["href"]}) \n'
                                        f'Transactions: [{transactions_count}]({data["_links"]["transactions"]["href"]})')
            await ctx.author.send(embed=ledger_info)

    @ledger.error
    async def ledger_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            message = f'Ledger ID is constructed only with numbers.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)


def setup(bot):
    bot.add_cog(HorizonLedger(bot))
