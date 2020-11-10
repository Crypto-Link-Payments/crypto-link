"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from horizonCommands.utils.horizon import server
from horizonCommands.utils.tools import format_date, process_memo
from horizonCommands.utils.customMessages import tx_info_for_account, horizon_error_msg, tx_info_for_hash, \
    tx_info_for_ledger
from stellar_sdk.exceptions import BadRequestError, NotFoundError

custom_messages = CustomMessages()


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

    @commands.group(aliases=["tx"])
    @commands.cooldown(1, 30, commands.BucketType.user)
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
        try:
            data = self.txs.transaction(transaction_hash=transaction_hash).call()

            sig_str = '\n'.join([f'`{sig}`' for sig in data['signatures']])
            date_fm = format_date(data["created_at"])
            memo = process_memo(record=data)

            await tx_info_for_hash(destination=ctx.message.author,
                                   data=data,
                                   signatures=sig_str, date=date_fm, memo=memo)
        except NotFoundError:
            await horizon_error_msg(destination=ctx.message.author, error=f"Transaction has you have provided could"
                                                                          f" not be found on the network. Please"
                                                                          f" recheck the data provided")
        except BadRequestError:
            await horizon_error_msg(destination=ctx.message.author, error=f"A transaction hash must be a hex-encoded, "
                                                                          f"lowercase SHA-256 hash")

    @transactions.command()
    async def account(self, ctx, account_address: str):
        """
        Get last three transactions for the account
        """
        data = self.txs.for_account(account_id=account_address).order(desc=True).call()

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
                    memo = process_memo(record=record)
                    date_fm = format_date(record["created_at"])
                    sig_str = '\n'.join([f'`{sig}`' for sig in record['signatures']])

                    await tx_info_for_account(destination=ctx.message.author, record=record, signers=sig_str,
                                              memo=memo, date=date_fm)
                    counter += 1
        else:
            message = f'Account ```{account_address}```  does not exist or has not been activated yet.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=':map: Account not found :map:')

    @transactions.command()
    async def ledger(self, ctx, ledger_id: int):
        try:
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

                    await tx_info_for_ledger(destination=ctx.message.author,ledger_id=ledger_id, record=record, signatures=sig_str,
                                             date=format_date(record["created_at"]))

            else:
                message = f'Ledger with :id: {ledger_id} could not be found'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=':ledger: Ledger not found :ledger:')
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])


def setup(bot):
    bot.add_cog(HorizonTransactions(bot))
