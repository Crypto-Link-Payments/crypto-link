"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won uppon withdrawal.
"""

import time
from datetime import datetime, timedelta

from discord import Embed, Color, Colour
from discord.ext import commands

from backOffice.botWallet import BotManager
from backOffice.merchatManager import MerchantManager
from backOffice.stellarActivityManager import StellarManager
from cogs.utils.customCogChecks import is_owner, has_wallet, community_registration_status, is_public
from cogs.utils.monetaryConversions import convert_to_currency
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

bot_manager = BotManager()
stellar = StellarManager()
custom_messages = CustomMessages()
merchant_manager = MerchantManager()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')


class MerchantLicensingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(is_owner)
    @commands.check(has_wallet)
    @commands.check(community_registration_status)
    @commands.check(is_public)
    async def license(self, ctx):
        """
        Licensing system entry point for user
        :param ctx:
        :return:
        """
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.invoked_subcommand is None:
            title = "__System Message__"
            description = 'Representation of all available commands under ***merchant*** category.'
            list_of_commands = [
                {"name": f'!license about',
                 "value": 'Returns detailed information on Licensing'},
                {"name": f'!license price',
                 "value": 'Returns information on current monthly license fee calculated '
                          'into XLM and XMR.'},
                {"name": f'!license status',
                 "value": 'Returns details if license has been activated for the community.'},
                {"name": f'!license buy',
                 "value": 'Returns detailed information on ways how to purchase license'},
                {"name": f'!license buy with_xlm',
                 "value": 'Use Stellar Lumen (XLM) to buy monthly license '}
            ]
            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_commands)

    @license.command()
    async def about(self, ctx):
        """
        Gets the information about licensing what it is, etc.
        :param ctx:
        :return:
        """
        license_info = Embed(name="__System Message__",
                             description='All about licensing',
                             colour=Color.gold())
        license_info.add_field(name='About:',
                               value='License allows for withdrawal amounts from merchant wallet to, '
                                     'owners wallet without additional fees. It represents a one time fee, '
                                     'owner has to pay in order to obtain himself license.',
                               inline=False)
        await ctx.channel.send(embed=license_info)

    @license.command()
    async def price(self, ctx):
        """
        Returns information on current license price in $ and calculated to available crypto
        :param ctx:
        :return:
        """

        data = bot_manager.get_fees_by_category(key='license')
        fee_value = data['fee']
        in_lumen = convert_to_currency(fee_value, coin_name='stellar')
        fee_info = Embed(title="__Merchant license information__",
                         description="Bellow are provided details on a monthly license"
                                     " to be free from Merchant Withdrawal Fees",
                         colour=Color.blue())
        fee_info.add_field(name='License information',
                           value=f'Duration: 1 moth from the day of purchase\n'
                                 f'Fiat value: {fee_value}$\n'
                                 f'Stellar Lumen: {in_lumen["total"]} <:stelaremoji:684676687425961994>\n')
        fee_info.set_footer(text="Conversion rates provided by CoinGecko",
                            icon_url='https://static.coingecko.com/s/thumbnail-007177f3eca19695592f0b8b0eabbdae282b54154e1be912285c9034ea6cbaf2.png')
        await ctx.message.channel.send(embed=fee_info)

    @license.command()
    async def status(self, ctx):
        """
        Checks the validity of the license
        :return:
        """

        if merchant_manager.check_community_license_status(community_id=ctx.message.guild.id):
            data = merchant_manager.get_community_license_details(community_id=ctx.message.guild.id)

            license_start = datetime.fromtimestamp(int(data['start']))
            licensed_end = datetime.fromtimestamp(int(data['end']))

            license_details = Embed(title='__License information__',
                                    description="Current details on the license",
                                    colour=Colour.green())
            license_details.add_field(name='License purchase time',
                                      value=f"{license_start} (UTC)",
                                      inline=False)
            license_details.add_field(name='License expiration time',
                                      value=f"{licensed_end} (UTC)",
                                      inline=False)
            await ctx.message.channel.send(embed=license_details)
        else:
            message = '__License information error__'
            title = 'It seems like you have not purchased license yet or license has expired.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)

    @license.group()
    async def buy(self, ctx):
        """
        Initiates purchase of license
        :param ctx:
        :return:
        """

        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.invoked_subcommand is None:
            title = "__Available options to purchase license__"
            description = 'Representation of all availabale currencies and options to purchase license.'
            list_of_commands = [
                {"name": f'!license buy with_xlm',
                 "value": 'Use Stellar Lumen to purchase license'}
            ]
            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_commands)

    @buy.command()
    async def with_xlm(self, ctx):
        """
        Use XLM to buy license
        :param ctx:
        :return:
        """

        channel_id = auto_channels["merchant"]

        # Check if community does not have license yet
        if not merchant_manager.check_community_license_status(community_id=ctx.message.guild.id):
            data = bot_manager.get_fees_by_category(key='license')  # Get the fee value for the license
            fee_value = data['fee']  # Get out fee
            in_lumen = convert_to_currency(fee_value, coin_name='stellar')  # Convert fee to currency
            total = (in_lumen['total'])  # Get total in lumne
            rate = (in_lumen['usd'])  # Get conversion rate for info
            stroops = (int(total * (10 ** 7)))  # Convert to stroops 

            # Get owner wallet balance
            wallet_value = stellar.get_stellar_wallet_data_by_discord_id(discord_id=ctx.message.author.id)
            if wallet_value['balance'] >= stroops:
                if stellar.update_stellar_balance_by_discord_id(discord_id=ctx.message.author.id, stroops=stroops,
                                                                direction=0):
                    if bot_manager.update_lpi_wallet_balance(amount=stroops, wallet='xlm', direction=1):
                        license_start = datetime.utcnow()  # Current UTC date
                        four_week_range = timedelta(days=31)  # Determening the range
                        license_end = license_start + four_week_range  # Calculation of expiration date

                        unix_today = (int(time.mktime(license_start.timetuple())))  # Conversion to tuple
                        unix_future = (int(time.mktime(license_end.timetuple())))  # Converting future date to unix

                        if merchant_manager.insert_license(community_name=f'{ctx.guild}',
                                                           owner_id=ctx.author.id,
                                                           community_id=ctx.guild.id, start=unix_today,
                                                           end=unix_future,
                                                           ticker='xlm', value=stroops):

                            # Send notification to the user on purchased licence details
                            user_info = Embed(title='Merchant License Slip',
                                              description='Thank You for purchasing the 31 day license. '
                                                          'Bellow are presented details',
                                              colour=Color.green())
                            user_info.set_thumbnail(url=self.bot.user.avatar_url)
                            user_info.add_field(name='Date of Purchase',
                                                value=f'{license_start}',
                                                inline=False)
                            user_info.add_field(name='Date of Expiration',
                                                value=f'{license_end}',
                                                inline=False)
                            user_info.add_field(name='License Fee',
                                                value=f'{fee_value}$',
                                                inline=False)
                            user_info.add_field(name='Value Payed',
                                                value=f'XLM: {total}<:stelaremoji:684676687425961994>\n'
                                                      f'Rate: {rate}$ per <:stelaremoji:684676687425961994>',
                                                inline=False)
                            try:
                                await ctx.author.send(embed=user_info)
                            except Exception:
                                await ctx.channel.send(embed=user_info)

                            # send notifcation to merchant channel of LPI community
                            license_slip = Embed(title='Merchant license order processed',
                                                 description='This report was sent because, some community\n'
                                                             'obtained merchant license for 31 days. Details :',
                                                 colour=Color.green())
                            license_slip.add_field(name='Community of purchase',
                                                   value=f'{ctx.message.guild} (ID: {ctx.message.guild.id}',
                                                   inline=False)
                            license_slip.add_field(name='Community owner details',
                                                   value=f'{ctx.message.author}',
                                                   inline=False)
                            license_slip.add_field(name='Time of purchase',
                                                   value=f'{license_start}',
                                                   inline=False)
                            license_slip.add_field(name='Time of expiration',
                                                   value=f'{license_end}',
                                                   inline=False)
                            license_slip.add_field(name='Value Payed',
                                                   value=f'XLM: {total}<:stelaremoji:684676687425961994>\n'
                                                         f'Rate: {rate}$ per <:stelaremoji:684676687425961994>',
                                                   inline=False)

                            notf_channel = self.bot.get_channel(id=int(channel_id))
                            await notf_channel.send(embed=license_slip)
                        else:
                            # Revert value to user and remove value from LPI wallet
                            stellar.update_stellar_balance_by_discord_id(discord_id=ctx.message.author.id,
                                                                         stroops=stroops, direction=1)
                            bot_manager.update_lpi_wallet_balance(amount=stroops, wallet='xlm', direction=0)
                            title = "__Merchant License Purchase error__"
                            message = f" There has been an issue with the system. Please try again later. If " \
                                      f"the issue persists"
                            "contact Crypto Link Staff. Thank you for your understanding."
                            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                                 sys_msg_title=title)
                    else:
                        # Return funds to user since LPI wallet could not be credited
                        stellar.update_stellar_balance_by_discord_id(discord_id=ctx.message.author.id, stroops=stroops,
                                                                     direction=1)
                        title = "__Merchant License Purchase error__"
                        message = f" There has been an issue with the system. Please try again later. If the " \
                                  f"issue persists"
                        "contact Crypto Link Staff. Thank you for your understanding."
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                             sys_msg_title=title)

                else:
                    title = "__Merchant License Purchase error__"
                    message = f" There has been an issue with the system. Please try again later. If the issue persists"
                    "contact Crypto Link Staff. Thank you for your understanding."
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                         sys_msg_title=title)
            else:
                title = "__Merchant License Purchase error__"
                message = f"You can not purchase license due to insufficient funds:\n"
                f"License price: {total} <:stelaremoji:684676687425961994>\n"
                f"Wallet balance: {wallet_value / 10000000}<:stelaremoji:684676687425961994>. "
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                     sys_msg_title=title)
        else:
            title = "__Merchant License Purchase error__"
            message = f"It looks like you have already purchased license for Merchant System. "
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(MerchantLicensingCommands(bot))
