import datetime
import re
import time
from datetime import datetime
from datetime import timedelta

import discord
from discord.ext import commands
from pycoingecko import CoinGeckoAPI

from backOffice.merchatManager import MerchantManager
from backOffice.profileRegistrations import AccountManager
from cogs.utils.customCogChecks import is_public, guild_has_merchant, user_has_wallet
from cogs.utils.systemMessaages import CustomMessages
from utils import numbers
from utils.tools import Helpers

helper = Helpers()
account_mng = AccountManager()
customMessages = CustomMessages()
gecko = CoinGeckoAPI()
merchant_manager = MerchantManager()
d = helper.read_json_file(file_name='botSetup.json')
notf_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_MERCHANT_ROLE_ERROR = "__Merchant System Role Error__"


class ConsumerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_round(ticker):
        if ticker == 'xlm':
            return 7
        elif ticker == 'xmr':
            return 12

    @staticmethod
    def get_emoji(ticker):
        if ticker == 'xlm':
            return CONST_STELLAR_EMOJI

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

        title = '__Membership available commands__'
        description = 'Representation of all available commands under ***membership*** category.'
        list_of_commands = [
            {"name": f'{d["command"]}membership roles',
             "value": f'All available roles to be bought on the community {ctx.message.guild}'},
            {"name": f'{d["command"]}membership subscribe <@discord Role> <ticker xlm>',
             "value": 'Gets yourself a role'},
            {"name": f'{d["command"]}membership current',
             "value": 'Returns the list and description on all roles user currently has, which have been'
                      'obtained through merchant system and have not yet expired.'}
        ]

        if ctx.invoked_subcommand is None:
            await customMessages.embed_builder(ctx=ctx, title=title, data=list_of_commands, description=description,
                                               destination=1)

    @membership.command()
    @commands.check(is_public)
    async def current(self, ctx):
        """
        Returns information on current membership details
        """
        author = ctx.message.author.id
        community = ctx.message.guild.id

        roles = merchant_manager.check_user_roles(user_id=author, discord_id=community)
        if roles:
            for data in roles:
                value_in_stellar = round(int(data['atomicValue']) / 10000000, 7)

                starting_time = datetime.fromtimestamp(int(data['start']))
                ending_time = datetime.fromtimestamp(int(data['end']))
                count_left = ending_time - datetime.utcnow()
                dollar_worth = round(int(data['pennies']) / 100, 4)

                role_name = data['roleName']
                role_id = int(data['roleId'])

                role_embed = discord.Embed(title='Active role information',
                                           colour=discord.Colour.green())
                role_embed.add_field(name="Active Role",
                                     value=f'***{role_name}*** (id:{role_id})',
                                     inline=False)
                role_embed.add_field(name="Role Obtained:",
                                     value=f"{starting_time} UTC",
                                     inline=False)
                role_embed.add_field(name="Paid for Role ",
                                     value=f"{value_in_stellar} {CONST_STELLAR_EMOJI}",
                                     inline=False)
                role_embed.add_field(name="Role value in $",
                                     value=f"${dollar_worth}",
                                     inline=True)
                role_embed.add_field(name="Role expires",
                                     value=f'{ending_time} UTC',
                                     inline=False)
                role_embed.add_field(name="Left",
                                     value=f'{count_left}',
                                     inline=False)

                await ctx.author.send(embed=role_embed)
        else:
            title = "__Merchant System Message__"
            message = f"You have not purchased any roles on {ctx.message.guild}, or all of them have expired."
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)

    @membership.command()
    @commands.check(is_public)
    async def roles(self, ctx):
        """
        Gets all available monetized roles on the community
        :return:
        """
        roles = merchant_manager.get_all_roles_community(community_id=ctx.message.guild.id)
        title = f'__Available Roles on Community {ctx.message.guild}__'
        dollar_xlm = gecko.get_price(ids='stellar', vs_currencies='usd')

        if roles:
            for role in roles:
                value = float(role["pennyValues"] / 100)
                value_in_stellar = value / dollar_xlm['stellar']['usd']
                values = [{"name": 'Role', "value": f'{role["roleName"]} ID({role["roleId"]})'},
                          {"name": 'Status', "value": role["status"]},
                          {"name": 'Fiat value', "value": f"{value} $"},
                          {"name": 'Conversion to crypto', "value": f"{value_in_stellar:.7} {CONST_STELLAR_EMOJI}"},
                          {"name": 'Role Length',
                           "value": f"{role['weeks']} week/s {role['days']} day/s {role['hours']} "
                                    f"hour/s {role['minutes']} minute/s"}]
                description = "Role details"
                await customMessages.embed_builder(ctx=ctx, title=title, description=description, destination=1,
                                                   data=values)
        else:
            title = "__Merchant System Message__"
            message = f"{ctx.message.guild} does not have any available roles for purchase at this moment."
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)

    @membership.command()
    @commands.bot_has_permissions(manage_roles=True)
    async def subscribe(self, ctx, role: discord.Role):
        """
        Obtain a role available from community
        :param ctx: Discord Context
        :param role:
        :return:
        """
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
                    role_rounded = round(role_value_crypto, self.get_round(ticker=ticker))
                    crypto_price_atomic = self.make_atomic(amount=role_value_crypto, coin_name=ticker)
                    balance = account_mng.get_balance_based_on_ticker(user_id=int(ctx.message.author.id),
                                                                      ticker=ticker)
                    # Check if user has sufficient balance
                    if balance >= crypto_price_atomic:
                        # Update the community wallet
                        if merchant_manager.modify_funds_in_community_merchant_wallet(
                                community_id=int(ctx.message.guild.id),
                                amount=int(crypto_price_atomic),
                                direction=0,
                                wallet_tick=ticker):

                            if account_mng.update_user_wallet_balance(discord_id=ctx.message.author.id,
                                                                      ticker=ticker,
                                                                      direction=1,
                                                                      amount=crypto_price_atomic):

                                # Assign the role to the user
                                await ctx.message.author.add_roles(role,
                                                                   reason='you just got yourself a role')

                                emoji = self.get_emoji(ticker=ticker)

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
                                if merchant_manager.add_user_to_payed_roles(
                                        community_id=ctx.message.guild.id,
                                        community_name=ctx.message.guild.name,
                                        user_id=ctx.message.author.id,
                                        user_name=str(ctx.message.author),
                                        start=unix_today,
                                        end=unix_future,
                                        role_id=role.id,
                                        role_name=role.name,
                                        currency=ticker,
                                        currency_value_atom=crypto_price_atomic,
                                        pennies=int(
                                            role_details["pennyValues"])):

                                    purchase_role_data = {
                                        "roleEnd": end,
                                        "roleLeft": gap,
                                        "dollarValue": convert_to_dollar,
                                        "roleRounded": role_rounded,
                                        "usdRate": coin_usd_price
                                    }

                                    # Send user payment slip info on purchased role
                                    await customMessages.user_role_purchase_msg(ctx=ctx,role=role,
                                                                                role_datails=purchase_role_data)

                                    owner = ctx.message.guild.owner
                                    incoming_funds = discord.Embed(name='__Merchant system funds credited',
                                                                   title='__Incoming funds to corporate '
                                                                         'wallet___',
                                                                   description='You have received this '
                                                                               'notification'
                                                                               ' because of new funds '
                                                                               'being inbound '
                                                                               ' through the merchant '
                                                                               'service. '
                                                                               'Details are presented'
                                                                               ' below',
                                                                   colour=discord.Colour.green())
                                    incoming_funds.add_field(name='Amount',
                                                             value=f'{convert_to_dollar} $ \n'
                                                                   f'{role_rounded} {emoji}\n'
                                                                   f'{coin_usd_price}$ /  {emoji}', )
                                    incoming_funds.add_field(name='User Details',
                                                             value=f"User: {ctx.message.author}\n"
                                                                   f"Id: {ctx.message.author.id}",
                                                             inline=False)
                                    incoming_funds.add_field(name='Role Obtained',
                                                             value=f"Name: {role.name}\n"
                                                                   f"Id: {role.id}\n"
                                                                   f"Duration:\n"
                                                                   f"Weeks: {role_details['weeks']}\n"
                                                                   f"Days: {role_details['days']}\n"
                                                                   f"Hours: {role_details['hours']}\n"
                                                                   f"Minutes: {role_details['minutes']}",
                                                             inline=False)

                                    await owner.send(embed=incoming_funds)

                                    # TODO branch out

                                    # Merchant system notification
                                    disc_channel = self.bot.get_channel(id=int(notf_channels['merchant']))
                                    role_notf = discord.Embed(title='Role purchased',
                                                              description="Role has been obtained through "
                                                                          "the Merchant "
                                                                          "system",
                                                              color=discord.Colour.gold())
                                    role_notf.add_field(name='Community details',
                                                        value=f'Community:\n{ctx.message.guild} '
                                                              f'(ID:{ctx.message.guild.id})\n'
                                                              f'Owner: \n{ctx.message.guild.owner}\n'
                                                              f'{ctx.message.guild.owner.id}')
                                    role_notf.add_field(name='Time of purchase',
                                                        value=f"{start} (UTC)",
                                                        inline=False)
                                    role_notf.add_field(name='Customer',
                                                        value=f"User: {ctx.message.author}\n"
                                                              f"Id: {ctx.message.author.id}",
                                                        inline=False)
                                    role_notf.add_field(name='Amount',
                                                        value=f'{convert_to_dollar} $ \n'
                                                              f'{role_rounded} {emoji}\n'
                                                              f'{coin_usd_price}$/ 1{emoji}',
                                                        inline=False)
                                    await disc_channel.send(embed=role_notf)

                            else:
                                message = f'Error while trying to deduct funds from user'
                                title = '__User wallet update error__'
                                await customMessages.system_message(ctx=ctx, message=message,
                                                                    sys_msg_title=title,
                                                                    color_code=1, destination=1)
                        else:
                            message = f'Error while trying to update fund in community Merchant wallet'
                            title = '__Merchant wallet update error __'
                            await customMessages.system_message(ctx=ctx, message=message,
                                                                sys_msg_title=title,
                                                                color_code=1, destination=1)
                    else:
                        message = f'You have insufficient balance in your wallet to purchase this ' \
                                  f'role. Please' \
                                  f'top-up your account with desired currency.'
                        title = '__Insufficient balance __'
                        await customMessages.system_message(ctx=ctx, message=message, sys_msg_title=title,
                                                            color_code=1, destination=0)

                else:
                    message = f'You have already obtained role with name ***{role}***. In order ' \
                              f'to extend the role you will need to first wait that role expires.'
                    await customMessages.system_message(ctx=ctx, message=message,
                                                        sys_msg_title=CONST_MERCHANT_ROLE_ERROR,
                                                        color_code=1, destination=0)
            else:
                message = f'Role {role} is either deactivated at this moment or has not bee monetized ' \
                          f'on {ctx.message.guild} and can not be obtained.  Please contact the owner of the' \
                          f' community or use ***{d["command"]}membership roles*** to ' \
                          f'familiarize yourself with all available roles and their status'
                await customMessages.system_message(ctx=ctx, message=message,
                                                    sys_msg_title=CONST_MERCHANT_ROLE_ERROR,
                                                    color_code=1,
                                                    destination=1)
        else:
            msg_title = '__Role creation error___'
            message = f'Ticker you have provided ***{ticker}*** includes special characters which are not allowed.' \
                      f' Please repeat the process!'
            await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=1,
                                                destination=1)

    @subscribe.error
    async def subscribe_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            title = 'Role error'
            message = 'role can not be given'
            await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=1,
                                                destination=1)
        elif isinstance(error, commands.BotMissingPermissions):
            title = 'Bot permission error'
            message = f'role can not be given as bot does not have sufficient rights please contact guild owner.' \
                      f' Current missing permissions are:\n' \
                      f'{error.missing_perms}'
            await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=1,
                                                destination=1)
        elif isinstance(error, commands.BadArgument):
            title = '__System Error__'
            message = f'Either you have provided bad argument or role does not exist int he merchant system'
            await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=1,
                                                destination=0)

        else:
            print(error)

    @membership.error
    async def membership_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = '__Membership and Merchant system error!__'
            message = 'Community has not activated merchant service or you have used command over the DM with the bot.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)


def setup(bot):
    bot.add_cog(ConsumerCommands(bot))
