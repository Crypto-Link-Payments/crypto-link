"""
Cogs to handle fee management
"""

import discord
from discord.ext import commands

from backOffice.botWallet import BotManager
from backOffice.merchatManager import MerchantManager
from backOffice.profileRegistrations import AccountManager
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

bot_manager = BotManager()
custom_messages = CustomMessages()
account_mng = AccountManager()
merchant_manager = MerchantManager()
helper = Helpers()

d = helper.read_json_file(file_name='botSetup.json')
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')


def is_animus(ctx):
    return ctx.message.author.id == d['creator']


def is_one_of_gods(ctx):
    list_of_gods = [d['ownerId'], d['creator']]
    return [god for god in list_of_gods if god == ctx.message.author.id]


class FeeManagementAndControl(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(is_one_of_gods)
    async def fee(self, ctx):
        """
        Command category/ entry for the system
        :param ctx:
        :return:
        """
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.invoked_subcommand is None:
            title = '__All available commands to manipulate system fees__'
            description = "Commands presented bellow allow for manipulation of fees and their review per each segment."
            list_of_values = [
                {"name": f"{d['command']}fee change",
                 "value": f"Entry to sub category of commands to set fees for various parts of {self.bot.user} system"},
                {"name": f"{d['command']}fee current",
                 "value": f"Information on current state of the fees"},
            ]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values)

    @fee.group()
    async def change(self, ctx):
        """
        Commande endry for sub categories to manipulate fees
        :param ctx:
        :return:
        """
        if ctx.invoked_subcommand is None:
            title = '__Change fee commands__'
            description = "Representation of all commands needed to be execute if you are willing to change the fee"
            list_of_values = [
                {"name": f"{d['command']}fee change minimum_merchant_transfer_value <value in $ in format 0.00>",
                 "value": f"Minimum amount in $ crypto value to be eligable for withdrawal from it"},
                {"name": f"{d['command']}fee change merchnat_license_fee <value in $ in format 0.00>",
                 "value": f"Monthly License Fee for Merchant"},
                {"name": f"{d['command']}fee change merchant_wallet_tranfer_fee <value in $ in format 0.00>",
                 "value": f"Fee when transfering from merchant wallet of the community"},
                {"name": f"{d['command']}fee change xlm_withdrawal_fee <value in $ in format 0.00>",
                 "value": f"Withdrawal fee from personal wallet to outside wallet on Stellar chain"},

            ]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values)

    @change.command()
    async def minimum_merchant_transfer_value(self, ctx, value: float):
        """
        Set minimum amount in merchant wallet for withdrawal from it
        :param value:
        :return:
        """
        # Get value in in pennies
        pennnies = (int(value * (10 ** 2)))
        rounded = round(pennnies / 100, 2)
        if bot_manager.license_fee_handling(fee=rounded, key='merchant_min'):
            message = f'You have successfully set merchant minimum withdrawal to be {rounded}$ per currency used.'
            title = '__Merchant monthly license change information__'
            await custom_messages.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                 sys_msg_title=title)
        else:
            message = f'There has been an error while trying to set merchant minimum withdrawalamount to {rounded}$.' \
                      f'Please try again later or contact system administrator!'
            title = '__Merchant monthly license change information__'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @change.command()
    async def merchant_license_fee(self, ctx, value: float):
        """
        Change merchantq license fee
        :param value:
        :return:
        """
        # Get value in in pennies
        pennnies = (int(value * (10 ** 2)))
        rounded = round(pennnies / 100, 2)
        if bot_manager.license_fee_handling(fee=rounded, key='license'):
            message = f'You have successfully set merchant monthly license fee to be {rounded}$.'
            title = '__Merchant monthly license change information__'
            await custom_messages.system_message(ctx=ctx, color_code=0, message=message, destination=1,
                                                 sys_msg_title=title)
        else:
            message = f'There has been an error while trying to set monthly merchant license fee to {rounded}$.' \
                      f'Please try again later or contact system administrator!'
            title = '__Merchant monthly license change information__'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @change.command()
    async def merchant_wallet_transfer_fee(self, ctx, value: float):
        """
        Change fee for merchant wallet transfer in $
        :param value:
        :return:
        """
        # Get value in in pennies
        pennnies = (int(value * (10 ** 2)))
        rounded = round(pennnies / 100, 2)
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
        # Get value in in pennies
        pennnies = (int(value * (10 ** 2)))
        rounded = round(pennnies / 100, 2)
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

    @fee.command()
    async def current(self, ctx):
        fees = bot_manager.get_fees_by_category(all=1)
        fee_info = discord.Embed(title='Applied fees for system',
                                 description='State of fees for each segment of the bot',
                                 colour=discord.Colour.blue())

        for data in fees:
            fee_info.add_field(name=data['type'],
                               value=f"{data['fee']}$",
                               inline=False)

        fee_info.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.channel.send(embed=fee_info)


def setup(bot):
    bot.add_cog(FeeManagementAndControl(bot))
