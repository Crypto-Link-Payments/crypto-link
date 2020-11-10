"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers
from horizonCommands.utils.horizon import server

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'


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
    async def trades(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        title = ':currency_exchange:  __Horizon Trades Queries__ :currency_exchange:   '
        description = 'Representation of all available commands available to interact with ***Trades*** Endpoint on ' \
                      'Stellar Horizon Server'
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

    async def send_trade_details(self, ctx, trade: dict):
        """
            'base_offer_id': '4611998412873666561',
            """
        if trade["base_asset_type"] != 'native':
            base_asset = f"{trade['base_asset_code']}"
            base_issuer = f'{trade["base_asset_issuer"]}'
        else:
            base_asset = 'XLM'
            base_issuer = f'Stellar'

        if trade["counter_asset_type"] != 'native':
            counter_asset = f"{trade['counter_asset_code']}"
            counter_issuer = f'{trade["counter_asset_issuer"]}'
        else:
            counter_asset = 'XLM'
            counter_issuer = f'Stellar'

        trade_report = Embed(title=f':id: {trade["id"]}',
                             description=f'__**Base seller**__: {trade["base_is_seller"]}',
                             colour=Colour.lighter_gray())
        trade_report.add_field(name=f':calendar: Close Time :calendar: ',
                               value=f'`{trade["ledger_close_time"]}`')
        trade_report.add_field(name=f':white_circle: Paging Token :white_circle:',
                               value=f'`{trade["paging_token"]}`')
        trade_report.add_field(name=f':map: Offer ID :map:',
                               value=f'`{trade["offer_id"]}`',
                               inline=True)
        trade_report.add_field(name=f':mag_right: Trade Details :mag_right:  ',
                               value=f'`{trade["base_amount"]} {base_asset}` :currency_exchange: '
                                     f'`{trade["counter_amount"]} {counter_asset}`',
                               inline=False)
        trade_report.add_field(name=f':men_wrestling: Parties :men_wrestling:',
                               value=f'Base:\n'
                                     f'```{trade["base_account"]}```\n'
                                     f'Counter:\n'
                                     f'```{trade["counter_account"]}```',
                               inline=False)
        trade_report.add_field(name=f':gem: Asset Details :gem:',
                               value=f':bank: **__ (Base) {base_asset} Issuer Details__** :bank:\n'
                                     f'```{base_issuer}```'
                                     f':bank: **__ (Counter) {counter_asset} Issuer Details__** :bank:\n'
                                     f'```{counter_issuer}```',
                               inline=False)
        trade_report.add_field(name=f':sunrise: Horizon Links :sunrise:',
                               value=f'[Base]({trade["_links"]["base"]["href"]})\n'
                                     f'[Counter]({trade["_links"]["counter"]["href"]})\n'
                                     f'[Operation]({trade["_links"]["operation"]["href"]})\n')
        await ctx.author.send(embed=trade_report)

    @trades.command()
    async def account(self, ctx, address: str):
        data = self.trade.for_account(account_id=address).limit(100).order(desc=True).call()
        trades = data["_embedded"]["records"]

        address_details = Embed(title=f':currency_exchange: Trades for Account :currency_exchange:',
                                colour=Colour.lighter_gray())
        address_details.add_field(name=f':map: Address :map:',
                                  value=f'```{address}```',
                                  inline=False)
        address_details.add_field(name=f':sunrise: Horizon Link :sunrise:',
                                  value=f'[Trades for Account]({data["_links"]["self"]["href"]})',
                                  inline=False)
        address_details.add_field(name=f':three: Last 3 trades for Account :three:',
                                  value=f':arrow_double_down:',
                                  inline=False)
        await ctx.author.send(embed=address_details)

        counter = 0
        for t in trades:
            if counter <= 2:
                await self.send_trade_details(ctx=ctx, trade=t)
                counter += 1

    @trades.command()
    async def offer(self, ctx, offer_id: int):
        data = self.trade.for_offer(offer_id=offer_id).limit(100).order(desc=True).call()

        offer_details = Embed(title=f':currency_exchange: Trades for Offer :currency_exchange:',
                              colour=Colour.lighter_gray())
        offer_details.add_field(name=f':id:',
                                value=f'```{offer_id}```',
                                inline=False)
        offer_details.add_field(name=f':sunrise: Horizon Link :sunrise:',
                                value=f'[Trades for Offer]({data["_links"]["self"]["href"]})',
                                inline=False)
        await ctx.author.send(embed=offer_details)

        for t in data["_embedded"]["records"]:
            await self.send_trade_details(ctx=ctx, trade=t)


def setup(bot):
    bot.add_cog(HorizonTrades(bot))
