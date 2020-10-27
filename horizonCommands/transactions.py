"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers
from horizonCommands.horizonAccess.horizon import server

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'


class HorizonTransactions(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.server = server
        self.txs = self.server.transactions()

    def get_emoji(self, title):
        if title == 'ledger':
            return ':ledger:'
        elif title == 'Transaction Hash':
            return ':hash:'
        elif title == "account":
            return ':map:'

    @commands.group()
    async def transactions(self, ctx):
        title = ':incoming_envelope: __Horizon Transactions Operations__ :incoming_envelope:'
        description = 'Representation of all available commands available to interact with ***Transactions*** Endpoint on ' \
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

    @transactions.command()
    async def single(self, ctx, transaction_hash: str):
        data = self.txs.transaction(transaction_hash=transaction_hash).call()
        sig_str = '\n'.join([f'`{sig}`' for sig in data['signatures']])
        single_info = Embed(title=f':hash: Transaction Hash Details :hash:',
                            colour=Colour.dark_orange())
        single_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                              value=f'[Transaction Hash]({data["_links"]["self"]["href"]})')
        single_info.add_field(name=':ledger: Ledger :ledger: ',
                              value=f'`{data["ledger"]}`')
        single_info.add_field(name=':white_circle: Paging Token :white_circle: ',
                              value=f'`{data["paging_token"]}`',
                              inline=True)
        single_info.add_field(name=f':calendar: Created :calendar: ',
                              value=f'`{data["created_at"]}`',
                              inline=False)
        single_info.add_field(name=f' :map: Source account :map: ',
                              value=f'`{data["source_account"]}`',
                              inline=False)
        single_info.add_field(name=f' :pencil:  Memo :pencil: ',
                              value=f'`{data["memo"]} (Type: {data["memo_type"]})`',
                              inline=False)
        single_info.add_field(name=f':pen_ballpoint: Signers :pen_ballpoint: ',
                              value=sig_str,
                              inline=False)
        single_info.add_field(name=':hash: Hash :hash: ',
                              value=f'`{data["hash"]}`',
                              inline=False)
        single_info.add_field(name=':money_with_wings: Fee :money_with_wings: ',
                              value=f'`{round(int(data["fee_charged"]) / 10000000, 7):.7f} XLM`',
                              inline=False)
        single_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                              value=f'[Ledger]({data["_links"]["ledger"]["href"]})\n'
                                    f'[Transactions]({data["_links"]["transaction"]["href"]})\n'
                                    f'[Effects]({data["_links"]["effects"]["href"]})\n'
                                    f'[Operations]({data["_links"]["succeeds"]["href"]}\n)'
                                    f'[Succeeds]({data["_links"]["succeeds"]["href"]})\n'
                                    f'[Precedes]({data["_links"]["precedes"]["href"]})')
        await ctx.author.send(embed=single_info)

    @transactions.command()
    async def account(self, ctx, account_address: str):
        data = self.txs.for_account(account_id=account_address).call()
        if data:
            records = data['_embedded']['records']
            account_info = Embed(title=f':map: Account Transactions Information :map:',
                                 colour=Colour.lighter_gray())
            account_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                                   value=f'[Account Transactions]({data["_links"]["self"]["href"]})')
            account_info.add_field(name=f'Last :three: entries',
                                   value=f':arrow_double_down: ',
                                   inline=False)
            await ctx.author.send(embed=account_info)
            counter = 0
            for record in records:
                if counter <= 2:
                    sig_str = '\n'.join([f'`{sig}`' for sig in record['signatures']])
                    account_record = Embed(title=f':record_button: Account Transaction Record :record_button:',
                                           colour=Colour.dark_orange())
                    account_record.add_field(name=':ledger: Ledger :ledger: ',
                                             value=f'`{record["ledger"]}`')
                    account_record.add_field(name=':white_circle: Paging Token :white_circle: ',
                                             value=f'`{record["paging_token"]}`',
                                             inline=True)
                    account_record.add_field(name=f':calendar: Created :calendar: ',
                                             value=f'`{record["created_at"]}`',
                                             inline=False)
                    account_record.add_field(name=f' :map: Source account :map: ',
                                             value=f'`{record["source_account"]}`',
                                             inline=False)
                    account_record.add_field(name=f' :pen: Memo :pen: ',
                                             value=f'`{record["memo"]} (Type: {record["memo_type"]})`',
                                             inline=False)
                    account_record.add_field(name=f':pen_ballpoint: Signers :pen_ballpoint: ',
                                             value=sig_str,
                                             inline=False)
                    account_record.add_field(name=':hash: Hash :hash: ',
                                             value=f'`{record["hash"]}`',
                                             inline=False)
                    account_record.add_field(name=':money_with_wings: Fee :money_with_wings: ',
                                             value=f'`{round(int(record["fee_charged"]) / 10000000, 7):.7f} XLM`',
                                             inline=False)
                    account_record.add_field(name=f':sunrise: Horizon Link :sunrise:',
                                             value=f'[Account]({record["_links"]["account"]["href"]})\n'
                                                   f'[Ledger]({record["_links"]["ledger"]["href"]})\n'
                                                   f'[Transactions]({record["_links"]["transaction"]["href"]})\n'
                                                   f'[Effects]({record["_links"]["effects"]["href"]})\n'
                                                   f'[Operations]({record["_links"]["succeeds"]["href"]}\n)'
                                                   f'[Succeeds]({record["_links"]["succeeds"]["href"]})\n'
                                                   f'[Precedes]({record["_links"]["precedes"]["href"]})')
                    await ctx.author.send(embed=account_record)
                    counter += 1
        else:
            message = f'Account ```{account_address}```  does not exist or has not been activated yet.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=':map: Account not found :map:')

    @transactions.command()
    async def ledger(self, ctx, ledger_id: int):
        data = self.txs.for_ledger(sequence=ledger_id).call()
        if data:
            records = data['_embedded']['records']
            ledger_info = Embed(title=f':ledger: Ledger {ledger_id} Information :ledger:',
                                description='Bellow is represent information for requested ledger.',
                                colour=Colour.lighter_gray())
            ledger_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                                  value=f'[Ledger]({data["_links"]["self"]["href"]})')
            await ctx.author.send(embed=ledger_info)
            for record in records:
                sig_str = '\n'.join([f'`{sig}`' for sig in record['signatures']])
                ledger_record = Embed(title=f':record_button: Record for {ledger_id} :record_button:',
                                      colour=Colour.dark_orange())
                ledger_record.add_field(name=':white_circle: Paging Token :white_circle: ',
                                        value=f'`{record["paging_token"]}`',
                                        inline=False)
                ledger_record.add_field(name=f':calendar: Created :calendar: ',
                                        value=f'`{record["created_at"]}`',
                                        inline=False)
                ledger_record.add_field(name=f' :map: Source account :map: ',
                                        value=f'`{record["source_account"]}`',
                                        inline=False)
                ledger_record.add_field(name=f' Source account Sequence ',
                                        value=f'`{record["source_account_sequence"]}`',
                                        inline=False)
                ledger_record.add_field(name=f':pen_ballpoint: Signers :pen_ballpoint: ',
                                        value=sig_str,
                                        inline=False)
                ledger_record.add_field(name=':hash: Hash :hash: ',
                                        value=f'`{record["hash"]}`',
                                        inline=False)
                ledger_record.add_field(name=f':sunrise: Horizon Link :sunrise:',
                                        value=f'[Record]({record["_links"]["self"]["href"]})\n'
                                              f'[Account]({record["_links"]["account"]["href"]})\n'
                                              f'[Ledger]({record["_links"]["ledger"]["href"]})\n'
                                              f'[Transactions]({record["_links"]["transaction"]["href"]})\n'
                                              f'[Effects]({record["_links"]["effects"]["href"]})\n'
                                              f'[Succeeds]({record["_links"]["succeeds"]["href"]})\n'
                                              f'[Precedes]({record["_links"]["precedes"]["href"]})')
                await ctx.author.send(embed=ledger_record)
        else:
            message = f'Ledger with :id: {ledger_id} could not be found'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=':ledger: Ledger not found :ledger:')


def setup(bot):
    bot.add_cog(HorizonTransactions(bot))
