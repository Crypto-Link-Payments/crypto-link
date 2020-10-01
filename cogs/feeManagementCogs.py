"""
Cogs to handle fee management
"""

import discord
from discord.ext import commands

from backOffice.botWallet import BotManager
from cogs.utils.customCogChecks import is_one_of_gods
from cogs.utils.monetaryConversions import convert_to_currency, get_rates
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

bot_manager = BotManager()
custom_messages = CustomMessages()
helper = Helpers()

d = helper.read_json_file(file_name='botSetup.json')
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_MERCHANT_LICENSE_CHANGE = '__Merchant monthly license change information__'


class FeeManagementAndControl(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def filter_db_keys(fee_type: str):

        if fee_type == 'withdrawal_fees':
            fee_type = "Coin withdrawal fees"
        elif fee_type == 'merch_transfer_cost':
            fee_type = "Merchant wallet withdrawal fee"
        elif fee_type == 'merch_license':
            fee_type = "Merchant Monthly License cost"
        elif fee_type == 'merch_transfer_min':
            fee_type = 'Merchant minimum transfer'

        return fee_type

    @commands.command()
    async def fees(self, ctx):
        fees = bot_manager.get_fees_by_category(all_fees=True)
        from pprint import pprint
        pprint(fees)
        fee_info = discord.Embed(title='Applied fees for system',
                                 description='State of fees for each segment of the bot',
                                 colour=discord.Colour.blue())

        rates = get_rates(coin_name='stellar')
        for data in fees:
            if not data.get('fee_list'):
                conversion = convert_to_currency(amount=float(data['fee']), coin_name='stellar')
                fee_type = self.filter_db_keys(fee_type=data['type'])

                fee_info.add_field(name=fee_type,
                                   value=f"XLM = {conversion['total']} {CONST_STELLAR_EMOJI}\n"
                                         f"Dollar = {data['fee']}$",
                                   inline=False)
            else:
                fee_type = self.filter_db_keys(fee_type=data['type'])
                fee_info.add_field(name=fee_type,
                                   value=f"{data['fee_list']}",
                                   inline=False)

        fee_info.add_field(name='Conversion rates',
                           value=f'{rates["stellar"]["usd"]} :dollar: / {CONST_STELLAR_EMOJI}\n'
                                 f'{rates["stellar"]["eur"]} :euro: / {CONST_STELLAR_EMOJI}')

        fee_info.set_thumbnail(url=self.bot.user.avatar_url)
        fee_info.set_footer(text='Conversion rates provided by CoinGecko',
                            icon_url='https://static.coingecko.com/s/thumbnail-'
                                     '007177f3eca19695592f0b8b0eabbdae282b54154e1be912285c9034ea6cbaf2.png')
        await ctx.channel.send(embed=fee_info)

    @commands.group()
    @commands.check(is_one_of_gods)
    async def fee(self, ctx):
        """
        Command category/ entry for the system
        :param ctx:
        :return:
        """
        if ctx.invoked_subcommand is None:
            title = '__All available commands to manipulate system fees__'
            description = "Commands presented bellow allow for manipulation of fees and their review per each segment."
            list_of_values = [
                {"name": f"{d['command']}fee change",
                 "value": f"Entry to sub category of commands to set fees for various parts of {self.bot.user} system"},
                {"name": f"{d['command']}fee current",
                 "value": f"Information on current state of the fees"},
            ]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                thumbnail=self.bot.user.avatar_url, destination=ctx.message.author)

    @fee.group()
    async def change(self, ctx):
        """
        Commands entry for sub categories to manipulate fees
        :param ctx:
        :return:
        """
        if ctx.invoked_subcommand is None:
            title = '__Change fee commands__'
            description = "Representation of all commands needed to be execute if you are willing to change the fee"
            list_of_values = [
                {"name": f"{d['command']}fee change minimum_merchant_transfer_value <value in $ in format 0.00>",
                 "value": "Minimum amount in $ crypto value to be eligible for withdrawal from it"},
                {"name": f"{d['command']}fee change merchant_license_fee <value in $ in format 0.00>",
                 "value": "Monthly License Fee for Merchant"},
                {"name": f"{d['command']}fee change merchant_wallet_transfer_fee <value in $ in format 0.00>",
                 "value": "Fee when transferring from merchant wallet of the community"},
                {"name": f"{d['command']}fee change xlm_withdrawal_fee <value in $ in format 0.00>",
                 "value": "Withdrawal fee from personal wallet to outside wallet on Stellar chain"},

            ]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                thumbnail=self.bot.user.avatar_url, destination=ctx.message.author)

    @change.command()
    async def minimum_merchant_transfer_value(self, ctx, value: float):
        """
        Set minimum amount in merchant wallet for withdrawal from it
        :param ctx: Discord Context
        :param value:
        :return:
        """
        # Get value in in pennies
        penny = (int(value * (10 ** 2)))
        rounded = round(penny / 100, 2)
        if bot_manager.license_fee_handling(fee=rounded, key='merchant_min'):
            message = f'You have successfully set merchant minimum withdrawal to be {rounded}$ per currency used.'
            await custom_messages.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                 sys_msg_title=CONST_MERCHANT_LICENSE_CHANGE)
        else:
            message = f'There has been an error while trying to set merchant minimum withdrawal amount to {rounded}$.' \
                      f'Please try again later or contact system administrator!'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_MERCHANT_LICENSE_CHANGE)

    @change.command()
    async def merchant_license_fee(self, ctx, value: float):
        """
        Change merchant license fee
        :param ctx: Discord Context
        :param value:
        :return:
        """
        # Get value in in pennies
        penny = (int(value * (10 ** 2)))
        rounded = round(penny / 100, 2)
        if bot_manager.license_fee_handling(fee=rounded, key='license'):
            message = f'You have successfully set merchant monthly license fee to be {rounded}$.'
            await custom_messages.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                 sys_msg_title=CONST_MERCHANT_LICENSE_CHANGE)
        else:
            message = f'There has been an error while trying to set monthly merchant license fee to {rounded}$.' \
                      f'Please try again later or contact system administrator!'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_MERCHANT_LICENSE_CHANGE)

    @change.command()
    async def merchant_wallet_transfer_fee(self, ctx, value: float):
        """
        Change fee for merchant wallet transfer in $
        :param ctx: Discord Context
        :param value:
        :return:
        """
        # Get value in in pennies
        penny = (int(value * (10 ** 2)))
        rounded = round(penny / 100, 2)
        if bot_manager.license_fee_handling(fee=rounded, key='wallet_transfer'):
            message = f'You have successfully set merchant wallet transfer fee to be {rounded}$.'
            title = '__Merchant wallet transfer fee information__'
            await custom_messages.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                 sys_msg_title=title)
        else:
            message = f'There has been an error while trying to set merchant wallet transfer fee to {rounded}$.' \
                      f'Please try again later or contact system administrator!'
            title = '__Merchant wallet transfer fee information__'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @change.command()
    async def xlm_withdrawal_fee(self, ctx, value: float):
        """
        Setting up discord user withdrawal fee
        """
        penny = (int(value * (10 ** 2)))
        rounded = round(penny / 100, 2)
        if bot_manager.license_fee_handling(fee=rounded, key="xlm"):
            message = f'You have successfully set Stellar Lumen withdrawal fee to be {rounded}$.'
            title = '__Stellar Lumen withdrawal fee information__'
            await custom_messages.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                 sys_msg_title=title)
        else:
            message = f'There has been an error while trying to set Stellar Lumen withdrawal fee to {rounded}$.' \
                      f'Please try again later or contact system administrator!'
            title = '__Stellar Lumen withdrawal fee information__'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(FeeManagementAndControl(bot))
