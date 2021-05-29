import datetime
import time
from datetime import datetime
from datetime import timedelta

import discord
from discord import Colour
from discord.ext import commands
from pycoingecko import CoinGeckoAPI

from utils.customCogChecks import is_public, guild_has_merchant, has_wallet
from cogs.utils.systemMessaages import CustomMessages

custom_messages = CustomMessages()
gecko = CoinGeckoAPI()
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_MERCHANT_ROLE_ERROR = "__Merchant System Role Error__"
CONST_MERCHANT_PURCHASE_ERROR = ":warning: __Merchant System Purchase Error__:warning: "


class ConsumerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()

    @commands.group(alieases=["subscription", "perk", "perks"])
    @commands.check(guild_has_merchant)
    @commands.check(has_wallet)
    @commands.check(is_public)
    async def membership(self, ctx):
        """
        Entry point for membership connected with wmerchant system
        """

        if ctx.invoked_subcommand is None:
            title = ':joystick: __Membership available commands__ :joystick:'
            description = 'Representation of all available commands under ***membership*** category '
            list_of_commands = [
                {"name": f':circus_tent: Available Roles on {ctx.message.guild} :circus_tent:',
                 "value": f'```{self.command_string}membership roles```'},
                {"name": f':person_juggling: Subscribe for role on community :person_juggling: ',
                 "value": f'```{self.command_string}membership subscribe <@discord Role>```'},
                {"name": f':man_mage: List active roles on community:man_mage:',
                 "value": f'```{self.command_string}membership current```'}
            ]
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands, description=description,
                                                destination=1, c=Colour.magenta())

    @membership.command(aliases=["live"])
    @commands.check(is_public)
    async def current(self, ctx):
        """
        Returns information on current membership details user currently has active
        """
        author = ctx.message.author.id
        community = ctx.message.guild.id

        roles = self.backoffice.merchant_manager.check_user_roles(user_id=author, discord_id=community)
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
            message = f"You have no active roles on {ctx.message.guild}, or all of them have expired."
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_MERCHANT_ROLE_ERROR)

    @membership.command(aliases=['rls'])
    @commands.check(is_public)
    async def roles(self, ctx):
        """
        Gets all available monetized roles on the community
        :return:
        """
        roles = self.backoffice.merchant_manager.get_all_roles_community(community_id=ctx.message.guild.id)
        title = f':circus_tent: __Available Roles on Community {ctx.message.guild}__ :circus_tent:'
        dollar_xlm = gecko.get_price(ids='stellar', vs_currencies='usd')

        if roles:
            for role in roles:
                value = float(role["pennyValues"] / 100)
                value_in_stellar = value / dollar_xlm['stellar']['usd']
                values = [{"name": ':person_juggling: Role :person_juggling: ',
                           "value": f'```{role["roleName"]} ID({role["roleId"]})```'},
                          {"name": ':vertical_traffic_light: Status :vertical_traffic_light:',
                           "value": f'```{role["status"]}```'},
                          {"name": ':dollar: Fiat value :dollar: ', "value": f"```{value} $```"},
                          {"name": ':currency_exchange: Conversion to crypto :currency_exchange: ',
                           "value": f"```{value_in_stellar:.7} XLM```"},
                          {"name": ':timer: Role Length:timer:  ',
                           "value": f"```{role['weeks']} week/s \n{role['days']} day/s \n{role['hours']}"
                                    f" hour/s \n{role['minutes']} minute/s```"}]
                description = "Role details"
                await custom_messages.embed_builder(ctx=ctx, title=title, description=description, destination=1,
                                                    data=values, c=Colour.magenta())
        else:
            message = f"{ctx.message.guild} does not have any available roles for purchase at this moment."
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=CONST_MERCHANT_ROLE_ERROR)

    @membership.command(aliases=['purchase', 'buy', 'get'])
    @commands.bot_has_permissions(manage_roles=True)
    async def subscribe(self, ctx, role: discord.Role, ticker: str = None):
        """
        Subscribe to service
        """

        # User XLM incase the ticker of the currency is not provided
        if not ticker:
            ticker = "xlm"
        else:
            ticker = 'xlm'

        role_details = self.backoffice.merchant_manager.find_role_details(
            role_id=role.id)  # Get the roles from the system

        # Check if community has activated merchant
        if role_details and role_details['status'] == 'active':

            # Check if user has already applied for the role
            if role.id not in [author_role.id for author_role in
                               ctx.message.author.roles]:  # Check if user has not purchased role yet

                # Calculations and conversions
                convert_to_dollar = role_details["pennyValues"] / 100  # Convert to $
                coin_usd_price = gecko.get_price(ids='stellar', vs_currencies='usd')['stellar']['usd']

                # Check if api returned price
                if coin_usd_price:
                    role_value_crypto = float(convert_to_dollar / coin_usd_price)
                    role_value_rounded = round(role_value_crypto, 7)
                    role_value_atomic = int(role_value_rounded * (10 ** 7))

                    # Get users balance
                    balance = self.backoffice.account_mng.get_balance_based_on_ticker(
                        user_id=int(ctx.message.author.id),
                        ticker=ticker)

                    # Check if user has sufficient balance
                    if balance >= role_value_atomic and self.backoffice.merchant_manager.modify_funds_in_community_merchant_wallet(
                            community_id=int(ctx.message.guild.id),
                            amount=int(role_value_atomic),
                            direction=0,
                            wallet_tick=ticker):

                        # Update community wallet
                        if self.backoffice.account_mng.update_user_wallet_balance(discord_id=ctx.message.author.id,
                                                                                  ticker=ticker,
                                                                                  direction=1,
                                                                                  amount=role_value_atomic):

                            # Assign the role to the user
                            await ctx.message.author.add_roles(role,
                                                               reason='Merchnat purchased role given')
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
                                "atomicValue": role_value_atomic,
                                "pennies": int(role_details["pennyValues"]),
                                "communityName": f'{ctx.message.guild}',
                                "communityId": int(ctx.message.guild.id)}

                            # Add active user to database of applied merchant
                            if self.backoffice.merchant_manager.add_user_to_payed_roles(purchase_data=purchase_data):
                                purchase_role_data = {
                                    "roleStart": f"{start} UTC",
                                    "roleEnd": end,
                                    "roleLeft": gap,
                                    "dollarValue": convert_to_dollar,
                                    "roleRounded": role_value_rounded,
                                    "usdRate": coin_usd_price,
                                    "roleDetails": f"weeks: {role_details['weeks']}\n"
                                                   f"days: {role_details['days']}\n"
                                                   f"hours: {role_details['hours']}\n"
                                                   f"minutes: {role_details['minutes']}"
                                }

                                # Send user payment slip info on purchased role
                                await custom_messages.user_role_purchase_msg(ctx=ctx, role=role,
                                                                             role_details=purchase_role_data)

                                # Send report to guild oowner that he recieved funds
                                await custom_messages.guild_owner_role_purchase_msg(ctx=ctx, role=role,
                                                                                    role_details=purchase_role_data)

                                user_stats_update = {
                                    f'{ticker}.spentOnRoles': float(role_value_rounded),
                                    f'{ticker}.roleTxCount': int(1)
                                }

                                # Update user purchase stats
                                await self.backoffice.stats_manager.as_update_role_purchase_stats(
                                    user_id=ctx.message.author.id,
                                    merchant_data=user_stats_update)

                                global_merchant_stats = {
                                    'totalSpentInUsd': convert_to_dollar,
                                    'totalSpentInXlm': role_value_rounded
                                }

                                global_ticker_stats = {
                                    "merchantPurchases": 1,
                                    "merchantMoved": role_value_rounded
                                }

                                # Update merchant stats of CL
                                await self.backoffice.stats_manager.update_cl_merchant_stats(ticker='xlm',
                                                                                             merchant_stats=global_merchant_stats,
                                                                                             ticker_stats=global_ticker_stats)

                                guild_stats = {
                                    f"{ticker}.roleTxCount": 1,
                                    f"{ticker}.volume": role_value_rounded,
                                    f'{ticker}.txCount': 1

                                }
                                # Update guild stats
                                await self.backoffice.stats_manager.update_guild_stats(guild_id=ctx.message.guild.id,
                                                                                       guild_stats_data=guild_stats)

                                # TODO integrate guild overall transaction count once role purchased
                                data = {
                                    "overallGained": role_value_rounded,
                                    "rolesObtained": 1
                                }
                                await self.backoffice.guild_profiles.update_stellar_community_wallet_stats(
                                    guild_id=ctx.guild.id, data=data)

                                # Send notifcications
                                load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                                                 self.backoffice.guild_profiles.get_all_explorer_applied_channels()]
                                explorer_msg = f':man_juggling: purchased in value {role_value_rounded} {CONST_STELLAR_EMOJI} ' \
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
                                  f' current balance is {balance / (10 ** 7)}{CONST_STELLAR_EMOJI} and role value ' \
                                  f'according to current rate is {role_value_crypto}{CONST_STELLAR_EMOJI}.'
                        await custom_messages.system_message(ctx=ctx, message=message,
                                                             sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                                                             color_code=1, destination=0)

                else:
                    message = f'Role can not be purchased at this moment as conversion rates could no be obtained' \
                              f'from CoinGecko. Please try again later. We apologize for inconvenience.'
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
