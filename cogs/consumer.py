import datetime
import re
import time
from datetime import datetime
from datetime import timedelta

import discord
from discord import Colour
from discord.ext import commands
from pycoingecko import CoinGeckoAPI

from cogs.utils.customCogChecks import is_public, guild_has_merchant, user_has_wallet
from cogs.utils.systemMessaages import CustomMessages

from cogs.utils.monetaryConversions import get_decimal_point
from utils import numbers
from utils.tools import Helpers

helper = Helpers()
custom_messages = CustomMessages()
gecko = CoinGeckoAPI()
sys_channel = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_MERCHANT_ROLE_ERROR = "__Merchant System Role Error__"
CONST_MERCHANT_PURCHASE_ERROR = ":warning: __Merchant System Purchase Error__:warning: "


class ConsumerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()

    @staticmethod
    def get_coin_usd_value(coin_name):
        """
        Get the USD coin value
        :param coin_name:
        :return:
        """
        if coin_name == 'xlm':
            return gecko.get_price(ids='stellar', vs_currencies='usd')['stellar']['usd']

    @staticmethod
    def make_atomic(amount, coin_name):
        if coin_name == 'xlm':
            return int(amount * (10 ** 7))

    @staticmethod
    def convert_to_format(amount, coin_name):
        if coin_name == 'xlm':
            return numbers.scientific_conversion(value=amount, decimals=7)

    @commands.group()
    @commands.check(guild_has_merchant)
    @commands.check(user_has_wallet)
    @commands.check(is_public)
    async def membership(self, ctx):
        """
        Entry point for membership connected with merchant system
        """

        title = ':joystick: __Subscription available commands__ :joystick:'
        description = 'Representation of all available commands under ***membership*** category to purchase' \
                      ' and monitor roles.'
        list_of_commands = [
            {"name": f':circus_tent: Available Roles on {ctx.message.guild} :circus_tent:',
             "value": f'`{self.command_string}membership roles`'},
            {"name": f':person_juggling: Gets yourself a role :person_juggling: ',
             "value": f'`{self.command_string}membership subscribe <@discord Role>`'},
            {"name": f':man_mage: List active roles :man_mage:',
             "value": f'`{self.command_string}membership current`'}
        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands, description=description,
                                                destination=1, c= Colour.magenta())

    @membership.command()
    @commands.check(is_public)
    async def current(self, ctx):
        """
        Returns information on current membership details
        """
        author = ctx.message.author.id
        community = ctx.message.guild.id

        merchant_manager = self.backoffice.merchant_manager

        roles = merchant_manager.check_user_roles(user_id=author, discord_id=community)
        if roles:
            for role in roles:
                value_in_stellar = round(int(role['atomicValue']) / 10000000, 7)

                starting_time = datetime.fromtimestamp(int(role['start']))
                ending_time = datetime.fromtimestamp(int(role['end']))
                count_left = ending_time - datetime.utcnow()
                dollar_worth = round(int(role['pennies']) / 100, 4)

                role_name = role['roleName']
                role_id = int(role['roleId'])

                role_embed = discord.Embed(title=f':person_juggling: Active role information :person_juggling:',
                                           colour=Colour.magenta())
                role_embed.add_field(name=":circus_tent: Active Role :circus_tent:",
                                     value=f'***{role_name}*** (id:{role_id})',
                                     inline=False)
                role_embed.add_field(name=":calendar: Role Obtained :calendar: ",
                                     value=f"{starting_time} UTC",
                                     inline=False)
                role_embed.add_field(name=":money_with_wings: Role Value :money_with_wings: ",
                                     value=f"{value_in_stellar} {CONST_STELLAR_EMOJI} (${dollar_worth})",
                                     inline=False)
                role_embed.add_field(name=":stopwatch: Role Expires :stopwatch: ",
                                     value=f'{ending_time} UTC',
                                     inline=False)
                role_embed.add_field(name=":timer: Time Remaining :timer: ",
                                     value=f'{count_left}',
                                     inline=False)

                await ctx.author.send(embed=role_embed)
        else:
            message = f"You have not purchased any roles on {ctx.message.guild}, or all of them have expired."
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=CONST_MERCHANT_ROLE_ERROR)

    @membership.command(aliases=['rls'])
    @commands.check(is_public)
    async def roles(self, ctx):
        """
        Gets all available monetized roles on the community
        :return:
        """
        merchant_manager = self.backoffice.merchant_manager
        roles = merchant_manager.get_all_roles_community(community_id=ctx.message.guild.id)
        title = f':circus_tent: __Available Roles on Community {ctx.message.guild}__ :circus_tent:'
        dollar_xlm = gecko.get_price(ids='stellar', vs_currencies='usd')

        if roles:
            for role in roles:
                value = float(role["pennyValues"] / 100)
                value_in_stellar = value / dollar_xlm['stellar']['usd']
                values = [{"name": ':person_juggling: Role :person_juggling: ',
                           "value": f'{role["roleName"]} ID({role["roleId"]})'},
                          {"name": 'Status', "value": role["status"]},
                          {"name": ':dollar: Fiat value :dollar: ', "value": f"{value} $"},
                          {"name": ':currency_exchange: Conversion to crypto :currency_exchange: ',
                           "value": f"{value_in_stellar:.7} {CONST_STELLAR_EMOJI}"},
                          {"name": ':timer: Role Length:timer:  ',
                           "value": f"{role['weeks']} week/s {role['days']} day/s {role['hours']} "
                                    f"hour/s {role['minutes']} minute/s"}]
                description = "Role details"
                await custom_messages.embed_builder(ctx=ctx, title=title, description=description, destination=1,
                                                    data=values, c=Colour.magenta())
        else:
            message = f"{ctx.message.guild} does not have any available roles for purchase at this moment."
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=CONST_MERCHANT_ROLE_ERROR)

    @membership.command(aliases=['purchase', 'buy', 'get'])
    @commands.bot_has_permissions(manage_roles=True)
    async def subscribe(self, ctx, role: discord.Role):
        """
        Obtain a role available from community
        :param ctx: Discord Context
        :param role:
        :return:
        """
        merchant_manager = self.backoffice.merchant_manager
        ticker = 'xlm'
        tickers = ['xlm']
        if not re.search("[~!#$%^&*()_+{}:;\']", ticker) and ticker in tickers:
            role_details = merchant_manager.find_role_details(role_id=role.id)
            # Check if community has activated merchant
            if role_details and role_details['status'] == 'active':
                # Check if user has already applied for the role
                if role.id not in [author_role.id for author_role in ctx.message.author.roles]:
                    # Calculations and conversions
                    convert_to_dollar = role_details["pennyValues"] / 100  # Convert to $
                    coin_usd_price = self.get_coin_usd_value(ticker)
                    role_value_crypto = float(convert_to_dollar / coin_usd_price)
                    role_rounded = round(role_value_crypto, get_decimal_point(symbol=ticker))
                    crypto_price_atomic = self.make_atomic(amount=role_value_crypto, coin_name=ticker)
                    balance = self.backoffice.account_mng.get_balance_based_on_ticker(
                        user_id=int(ctx.message.author.id),
                        ticker=ticker)
                    # Check if user has sufficient balance
                    if balance >= crypto_price_atomic and merchant_manager.modify_funds_in_community_merchant_wallet(
                            community_id=int(ctx.message.guild.id),
                            amount=int(crypto_price_atomic),
                            direction=0,
                            wallet_tick=ticker):

                        # Update the community wallet
                        if self.backoffice.account_mng.update_user_wallet_balance(discord_id=ctx.message.author.id,
                                                                                  ticker=ticker,
                                                                                  direction=1,
                                                                                  amount=crypto_price_atomic):

                            # Assign the role to the user
                            await ctx.message.author.add_roles(role,
                                                               reason='you just got yourself a role')

                            # Current time
                            start = datetime.utcnow()

                            # get the timedelta from the role description
                            td = timedelta(weeks=role_details['weeks'],
                                           days=role_details['days'],
                                           hours=role_details['hours'],
                                           minutes=role_details['minutes'])

                            # calculate future date
                            end = start + td
                            gap = end - start
                            unix_today = (int(time.mktime(start.timetuple())))
                            unix_future = (int(time.mktime(end.timetuple())))

                            # make data for store in database
                            purchase_data = {
                                "userId": int(ctx.message.author.id),
                                "userName": str(ctx.message.author),
                                "roleId": int(role.id),
                                "roleName": f'{role.name}',
                                "start": unix_today,
                                "end": unix_future,
                                "currency": ticker,
                                "atomicValue": crypto_price_atomic,
                                "pennies": int(role_details["pennyValues"]),
                                "communityName": f'{ctx.message.guild}',
                                "communityId": int(ctx.message.guild.id)}

                            if merchant_manager.add_user_to_payed_roles(purchase_data=purchase_data):
                                purchase_role_data = {
                                    "roleStart": f"{start} UTC",
                                    "roleEnd": end,
                                    "roleLeft": gap,
                                    "dollarValue": convert_to_dollar,
                                    "roleRounded": role_rounded,
                                    "usdRate": coin_usd_price,
                                    "roleDetails": f"weeks: {role_details['weeks']}\n"
                                                   f"days: {role_details['days']}\n"
                                                   f"hours: {role_details['hours']}\n"
                                                   f"minutes: {role_details['minutes']}"
                                }

                                # Send user payment slip info on purchased role
                                await custom_messages.user_role_purchase_msg(ctx=ctx, role=role,
                                                                             role_details=purchase_role_data)

                                await custom_messages.guild_owner_role_purchase_msg(ctx=ctx, role=role,
                                                                                    role_details=purchase_role_data)

                                print('Updating user role stats')
                                user_stats_update = {
                                    'xlmStats.spentOnRoles': float(role_rounded),
                                    'xlmStats.roleTxCount': int(1),
                                }

                                await self.backoffice.stats_manager.as_update_role_purchase_stats(
                                    user_id=ctx.message.author.id,
                                    merchant_data=user_stats_update)

                                global_merchant_stats = {
                                    'totalSpentInUsd': convert_to_dollar,
                                    'totalSpentInXlm': role_rounded
                                }

                                global_ticker_stats = {
                                    "merchantPurchases": 1,
                                    "merchantMoved": role_rounded
                                }
                                await self.backoffice.stats_manager.update_cl_merchant_stats(ticker='xlm',
                                                                                             merchant_stats=global_merchant_stats,
                                                                                             ticker_stats=global_ticker_stats)

                                guild_stats = {

                                    "communityStats.roleTxCount": 1,
                                    "communityStats.xlmVolume": role_rounded

                                }
                                await self.backoffice.stats_manager.update_guild_stats(guild_id=ctx.message.guild.id,
                                                                                       guild_stats_data=guild_stats)

                                load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                                                 self.backoffice.guild_profiles.get_all_explorer_applied_channels()]
                                explorer_msg = f':man_juggling: purchased in value {role_rounded} {CONST_STELLAR_EMOJI} ' \
                                               f'(${convert_to_dollar}) on ' \
                                               f'{ctx.message.guild}'
                                await custom_messages.explorer_messages(applied_channels=load_channels,
                                                                        message=explorer_msg, on_chain=False,
                                                                        tx_type='role_purchase')
                        else:
                            message = f'Error while trying to deduct funds from user'
                            await custom_messages.system_message(ctx=ctx, message=message,
                                                                 sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                                                                 color_code=1, destination=1)
                    else:
                        message = f'You have insufficient balance in your wallet to purchase {role.mention}. Your' \
                                  f' current balance is {balance / 10000000}{CONST_STELLAR_EMOJI} and role value ' \
                                  f'according to current rate is {role_value_crypto}{CONST_STELLAR_EMOJI}.'
                        await custom_messages.system_message(ctx=ctx, message=message,
                                                             sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                                                             color_code=1, destination=0)

                else:
                    message = f'You have already obtained role with name ***{role}***. In order ' \
                              f'to extend the role you will need to first wait that role expires.'
                    await custom_messages.system_message(ctx=ctx, message=message,
                                                         sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                                                         color_code=1, destination=0)
            else:
                message = f'Role {role} is either deactivated at this moment or has not bee monetized ' \
                          f'on {ctx.message.guild}. Please contact {ctx.guild.owner} or use ' \
                          f' ***{self.command_string}membership roles*** to familiarize yourself with all available ' \
                          f'roles and their status'
                await custom_messages.system_message(ctx=ctx, message=message,
                                                     sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                                                     color_code=1,
                                                     destination=1)
        else:
            message = f'You can not purchase {role} with {ticker} as it is not integrated into the {self.bot.user}.'
            await custom_messages.system_message(ctx=ctx, sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR, message=message,
                                                 color_code=1,
                                                 destination=1)

    @subscribe.error
    async def subscribe_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            title = 'Role error'
            message = 'role can not be given'
            await custom_messages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=1,
                                                 destination=1)
        elif isinstance(error, commands.BotMissingPermissions):
            message = f'Role can not be given as bot does not have sufficient rights please contact guild ' \
                      f'owner {ctx.guild.owner.mention}.' \
                      f' Current missing permissions are:\n' \
                      f'{error.missing_perms}'
            await custom_messages.system_message(ctx=ctx, sys_msg_title=CONST_MERCHANT_ROLE_ERROR, message=message,
                                                 color_code=1,
                                                 destination=1)
        elif isinstance(error, commands.BadArgument):
            message = f'Either you have provided bad argument or role does not exist int he merchant system'
            await custom_messages.system_message(ctx=ctx, sys_msg_title=CONST_MERCHANT_ROLE_ERROR, message=message,
                                                 color_code=1,
                                                 destination=0)

        else:
            print(error)

    @membership.error
    async def membership_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = 'Community has not activated merchant service or you have used command over the DM with the bot.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_MERCHANT_ROLE_ERROR)


def setup(bot):
    bot.add_cog(ConsumerCommands(bot))
