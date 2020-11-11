"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Colour
from cogs.utils.systemMessaages import CustomMessages
from horizonCommands.utils.customMessages import send_trades_details, send_trades_basic_details, horizon_error_msg
from horizonCommands.utils.horizon import server
from stellar_sdk.exceptions import BadRequestError

custom_messages = CustomMessages()


class HorizonTrades(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.command_string = bot.get_command_str()
        self.server = server
        self.trade = self.server.trades()

    @commands.group()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def trades(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        title = ':currency_exchange:  __Horizon Trades Queries__ :currency_exchange:   '
        description = 'Representation of all available commands available to interact with ***Trades*** Endpoint on ' \
                      'Stellar Horizon Server. Commands can be used 1/30 seconds/ per user.'
        list_of_commands = [
            {"name": f':map: Trades for Account :map:',
             "value": f'`{self.command_string}trades account <address>`'},
            {"name": f':id: Trades by Offer ID :id:  ',
             "value": f'`{self.command_string}trades offer <offer id>`'}
        ]
        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @trades.command()
    async def account(self, ctx, address: str):
        try:
            data = self.trade.for_account(account_id=address).limit(100).order(desc=True).call()
            records = data["_embedded"]["records"]
            if records:
                await send_trades_basic_details(destination=ctx.message.author,
                                                trades_enpoint="account",
                                                query_details={
                                                    "by": ":map: Address :map:",
                                                    "query": address,
                                                },
                                                hrz_link=data["_links"]["self"]["href"])

                # Process records
                counter = 0
                for t in records:
                    if counter <= 2:
                        await send_trades_details(destination=ctx.message.author, trade_data=t)
                        counter += 1
            else:
                message = f'Account `{address}` doe not have any trades'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=':currency_exchange: No Trades :currency_exchange:')

        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @trades.command()
    async def offer(self, ctx, offer_id: int):
        print('offer query')
        try:
            data = self.trade.for_offer(offer_id=offer_id).limit(100).order(desc=True).call()
            from pprint import pprint
            records = data["_embedded"]["records"]
            pprint(records)
            if records:
                pprint('sending message')
                await send_trades_basic_details(destination=ctx.message.author,
                                                trades_enpoint="offer id",
                                                query_details={
                                                    "by": ":map: Offer ID :id:",
                                                    "query": offer_id,
                                                },
                                                hrz_link=data["_links"]["self"]["href"])

                counter = 0
                for t in records:
                    if counter <= 2:
                        await send_trades_details(destination=ctx.message.author, trade_data=t)
                        counter += 1
            else:
                message = f'There are no records for offer with ID `{offer_id}`'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=':currency_exchange: No Trades :currency_exchange:')
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @offer.error
    async def offer_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            message = f"Offer ID needs to be integer number only"
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title='Query Conversion Error')


def setup(bot):
    bot.add_cog(HorizonTrades(bot))
