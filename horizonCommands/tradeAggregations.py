"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers
from datetime import datetime

from cogs.utils.securityChecks import check_stellar_address
from horizonCommands.horizonAccess.horizon import server
from stellar_sdk import Asset, PathPayment

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'


class HorizonTrdeaAggregations(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.command_string = bot.get_command_str()
        self.server = server

    @staticmethod
    def process_resolution(resolution: int):
        """
        segment duration as millis since epoch. *Supported values
            are 1 minute (60000), 5 minutes (300000), 15 minutes (900000),
            1 hour (3600000), 1 day (86400000) and 1 week (604800000).

        """
        if resolution == 1:
            return 60000
        elif resolution == 5:
            return 300000
        elif resolution == 15:
            return 900000
        else:
            return None

    @commands.group()
    async def trade(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        title = ':bar_chart: __Horizon Trade Aggregations Queries__ :bar_chart: '
        description = 'Representation of all available commands available to interact with ***Trade Aggregations*** ' \
                      'Endpoint on Stellar Horizon Server'

        list_of_commands = [
            {"name": f':chart_with_upwards_trend: XLM vs Asset Trades',
             "value": f'`{self.command_string}trade agg <counter asset> <counter issuer> <resolution> `\n'
                      f'***__Note__***: Resolutions allowed 1, 5, and 15 minutes'},
        ]
        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @trade.command(aliases=["agg"])
    async def aggregations(self, ctx, counter_asset: str, counter_issuer: str,
                           resolution: int):
        base = Asset(code="XLM").native()
        counter = Asset(code=counter_asset.upper(), issuer=counter_issuer)
        resolution_actual = self.process_resolution(resolution=resolution)
        data = self.server.trade_aggregations(base=base, counter=counter, resolution=resolution_actual).call()

        # Embed
        agg_details = Embed(title=f':bar_chart: Aggregated Trades result :bar_chart: ',
                            colour=Colour.lighter_gray())
        agg_details.add_field(name=f':gem: Base Asset Details :gem:',
                              value=f'***__XLM__***')
        agg_details.add_field(name=f':gem: Counter Asset Details :gem:',
                              value=f'***__{counter_asset.upper()}__***\n'
                                    f'```{counter_issuer}```',
                              inline=False)
        agg_details.add_field(name=f':gem: Resolution :gem:',
                              value=f'{resolution} Minutes',
                              inline=False)
        agg_details.add_field(name=f':sunrise: Horizon Link :sunrise:',
                              value=f'[Trades for Query]({data["_links"]["self"]["href"]})',
                              inline=False)
        await ctx.author.send(embed=agg_details)

        records = data['_embedded']["records"]
        if resolution and records:
            rec = Embed(title=f'Aggregated Trades',
                        colour=Colour.lighter_gray())
            rev_records = reversed(records)
            counter = 0
            for r in rev_records:
                if counter <= 2:
                    milliseconds = int(r["timestamp"]) / 1000
                    actual = datetime.utcfromtimestamp(milliseconds)
                    rec.add_field(name=f':clock1: {actual} :clock1: ',
                                  value=f'***Σ Trades***: `{r["trade_count"]}`\n'
                                        f'***Average:*** `{r["avg"]}`\n'
                                        f'***Open:*** `{r["open"]}`\n'
                                        f'***High:*** `{r["high"]}`\n'
                                        f'***Low:*** `{r["low"]}`\n'
                                        f'***Close:*** `{r["close"]}`\n'
                                        f'***Base Vol:*** `{r["base_volume"]}`\n'
                                        f'***Counter Vol:*** `{r["counter_volume"]}`\n',
                                  inline=False)
                    counter += 1
            await ctx.author.send(embed=rec)


def setup(bot):
    bot.add_cog(HorizonTrdeaAggregations(bot))
