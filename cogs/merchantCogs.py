import re
from datetime import datetime

from discord import Role, Embed, Color, utils
from discord.ext import commands

from backOffice.botWallet import BotManager
from backOffice.merchatManager import MerchantManager
from backOffice.profileRegistrations import AccountManager
from backOffice.stellarActivityManager import StellarManager
from cogs.utils.customCogChecks import is_owner, has_wallet, is_public, community_registration_status
from cogs.utils.monetaryConversions import convert_to_currency, get_decimal_point
from cogs.utils.monetaryConversions import get_normal
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
lpi_wallet = BotManager()
merchant_manager = MerchantManager()
stellar_manager = StellarManager()
customMessages = CustomMessages()
account_mng = AccountManager()
d = helper.read_json_file(file_name='botSetup.json')
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')
CONST_FEE = 4.00  # In Dollar
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'


class MerchantCommunityOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(is_owner)
    @commands.check(has_wallet)
    @commands.check(is_public)
    async def merchant_initiate(self, ctx):
        """
        Command to initiate merchant setup process and register community into the Merchant system
        :param ctx:
        :return:
        """
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if not merchant_manager.check_if_community_exist(community_id=ctx.message.guild.id):
            if merchant_manager.register_community_wallet(community_id=ctx.message.guild.id,
                                                          community_owner_id=ctx.message.author.id):
                msg_title = '__Community Wallet Registration Status___'
                message = f'You have successfully created community wallet. You can proceed with {d["command"]}merchant in order ' \
                          f' to familiarize yourself with all available commands. '
                await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=0,
                                                    destination=1)
            else:
                msg_title = '__Community Wallet Registration Status___'
                message = f'There has been an issue while registering wallet into the system. Please try again later.' \
                          f' or contact one of the support staff. '
                await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=1,
                                                    destination=1)
        else:
            msg_title = '__Community Wallet Registration Status___'
            message = f'You have already registered {ctx.guild} for Merchant system on {self.bot.user}. Proceed' \
                      f' with command ***{d["command"]} merchant***'
            await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=1,
                                                destination=1)

    @commands.group()
    @commands.check(is_public)
    @commands.check(is_owner)  # Check if author is community owner
    @commands.check(community_registration_status)  # Check if community has been registered in the system
    @commands.check(has_wallet)  # Chekc if owner has community wallet
    @commands.bot_has_permissions(manage_roles=True)
    async def merchant(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.invoked_subcommand is None:
            title = "__Merchant System Message Setup__"
            description = 'Representation of all available commands under ***merchant*** category.'
            list_of_commands = [
                {"name": f'!merchant manual',
                 "value": 'Step by step guide how to set-up and monetize community'},
                {"name": f'!merchant monetize',
                 "value": 'All available commands to monetize the roles on Discord'},
                {"name": f'!merchant wallet',
                 "value": 'All commands available for community wallet operations'},
                {"name": f'{d["command"]}merchant create_role <role name> <value in dollars > '
                         f'<weeks> <days> <hours> <minutes>',
                 "value": 'Creates the role which is monetized with desired length'},
                {"name": f'{d["command"]}merchant  delete_role <@Discord Role>',
                 "value": 'Deletes the monetized role from the system and removes if from list of roles on community.'},
                {"name": f'{d["command"]}merchant stop_role <@Discord Role>',
                 "value": 'Stops the role from being obtained by the users however does not delete it from the system'},
                {"name": f'{d["command"]}merchant  start_role <@Discord Role>',
                 "value": 'Restarts the role which has been stopped and makes it available to discord members again.'},
                {"name": f'{d["command"]}merchant community_roles',
                 "value": 'Returns information on all roles you have set to be monetized on the community'}
            ]
            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_commands)

    @merchant.command()
    async def manual(self, ctx):
        manual = Embed(title='__Merchant system manual__',
                       colour=Color.green())
        manual.add_field(name='Create monetized roles',
                         value=f'{d["command"]}monetize create_role <role name> <Dollar value of role> '
                               f'<duration weeks> <days> <hours> <minutes>',
                         inline=False)
        manual.add_field(name='Note',
                         value='--> At least one of the time parameters needs to be greater than 0\n'
                               '--> Dollar value of the role is not allowed to be 0.00 $',
                         inline=False)
        await ctx.channel.send(embed=manual, delete_after=600)

    @merchant.command()
    @commands.check(is_public)
    @commands.bot_has_permissions(manage_roles=True)
    async def create_role(self, ctx, role_name: str, dolar_value: float, weeks_count: int, days_count: int,
                          hours_count: int, minutes_count: int):
        """
        Procedure to create role in the system
        :param ctx:
        :param role_name: String representation of the role
        :param dolar_value: Value in dollar
        :param weeks_count: length in weeks
        :param days_count: lenght in days
        :param hours_count: length in hours
        :param minutes_count: length in minutes
        :return:
        """

        in_penny = (int(dolar_value * (10 ** 2)))  # Convert to pennies
        total = weeks_count + days_count + hours_count + minutes_count

        if not (weeks_count < 0) and not (days_count < 0) and not (hours_count < 0) and not (minutes_count < 0) and (
                total > 0):

            if not re.search("[~!#$%^&*()_+{}:;\']", role_name):  # Check for special characters
                if len(role_name) <= 10:  # Check for role length
                    role = utils.get(ctx.guild.roles, name=role_name)  # Check if role present already
                    if not role:
                        if in_penny > 0:  # Checks if it is greater than 0 for xcash
                            created_role = await ctx.guild.create_role(
                                name=role_name)  # Create role and return its details

                            if merchant_manager.register_role(community_id=ctx.message.guild.id,
                                                              role_id=int(created_role.id),
                                                              role_name=created_role.name,
                                                              penny_value=in_penny,
                                                              weeks=weeks_count,
                                                              days=days_count,
                                                              hours=hours_count,
                                                              minutes=minutes_count):

                                # Send the message to the owner
                                msg_title = '__Role Creation Status___'
                                message = f'Role with name ***{role_name}*** has been successfully created.\n' \
                                          f'Details:\n' \
                                          f'Role ID: {created_role.id}\n' \
                                          f'Value: {dolar_value} $\n' \
                                          f'Duration of role: \n' \
                                          f'{weeks_count} week/s, {days_count} day/s {hours_count} hour/s {minutes_count}minute/s'

                                await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message,
                                                                    color_code=0,
                                                                    destination=1)

                                msg_title = '__Time to Inform Members___'
                                message = f'Users can now apply for the role by executing the' \
                                          f' command bellow: \n ***{d["command"]}membership subscribe <@Discord Role> ' \
                                          f'<ticker>***\n. ' \
                                          f'Thank You for using Merchant Service'
                                await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message,
                                                                    color_code=0,
                                                                    destination=1)
                            else:
                                msg_title = '__Role Creation Error___'
                                message = f'Role could not be stores into the system at this point. Please try again' \
                                          f' later. We apologize for inconvenience.'
                                await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message,
                                                                    color_code=1,
                                                                    destination=1)
                        else:
                            msg_title = '__Role Creation Error___'
                            message = f'The amount user will have to pay for role needs to be greater than 0.00$'
                            await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message,
                                                                color_code=1,
                                                                destination=1)
                    else:
                        msg_title = '__Role creation error___'
                        message = f'Role with name ***{role_name}*** already exist on the community ' \
                                  f'or in the system and can not be created.'
                        await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message,
                                                            color_code=1,
                                                            destination=1)
                else:
                    msg_title = '__Role creation error___'
                    message = f'Role with name ***{role_name}*** is too long. Max allowed length is 10 characters'
                    await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message,
                                                        color_code=1,
                                                        destination=1)
            else:
                msg_title = '__Role creation error___'
                message = f'Role with name ***{role_name}*** includes special characters which are not allowed. Please' \
                          f' repeat the process'
                await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=1,
                                                    destination=1)

        else:
            msg_title = '__Role creation error___'
            message = f'Role could not be create since the length of the role is either' \
                      f' limitless or expiration time is' \
                      f' not in future. In order to create a role data for week, days hours and minutes needs ' \
                      f'to be provide as followed:\n' \
                      f'week: whole number greater than 0\n' \
                      f'day: whole number greater than 0\n' \
                      f'hour: whole number greater than 0\n' \
                      f'minute: whole number greater than 0\n' \
                      f'Note: 0 is also acceptable however the sum of all variables needs to be greater than 0 at ' \
                      f'the end. '
            await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=1,
                                                destination=1)

    @merchant.command()
    @commands.bot_has_permissions(manage_roles=True)
    async def delete_role(self, ctx, discord_role: Role):
        """
        Delete monetized role from the system and community
        :param ctx:
        :param discord_role:
        :return:
        """
        if merchant_manager.find_role_details(role_id=discord_role.id):
            if merchant_manager.remove_monetized_role_from_system(role_id=discord_role.id,
                                                                  community_id=ctx.message.guild.id):
                await discord_role.delete()
                title = '__Role Delete System notification__'
                message = f'Monetized role has been successfully delete from the Merchant System, Community and from, ' \
                          f' all the users who obtained it.'
                await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=0,
                                                    destination=1)
            else:
                title = '__Role Delete System error__'
                message = f'Role could not be removed from the Merchant System. Please contact the team with details.'
                await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=0,
                                                    destination=1)
        else:
            title = '__Unknown role error__'
            message = f'This Role could not be deleted as it is not registered in the merchant system'
            await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=0,
                                                destination=1)

    @merchant.command()
    @commands.check(is_owner)
    @commands.check(is_public)
    async def community_roles(self, ctx):
        """
        Return all the community roles from the system
        :param ctx:
        :return:
        """
        roles = merchant_manager.get_all_roles_community(community_id=ctx.message.guild.id)
        title = f'__Available Roles on Community {ctx.message.guild}__'
        description = 'Details on monetized role.'
        if roles:
            for role in roles:
                dollar_value = float(role["pennyValues"] / 100)
                values = [{"name": 'Role', "value": f'{role["roleName"]} ID({role["roleId"]}'},
                          {"name": 'Status', "value": role["status"]},
                          {"name": 'Values', "value": f"{dollar_value} $"},
                          {"name": 'Role Length',
                           "value": f"{role['weeks']} week/s {role['days']} day/s {role['hours']} "
                                    f"hour/s {role['minutes']} minute/s"}]
                await customMessages.embed_builder(ctx=ctx, title=title, description=description, destination=1,
                                                   data=values, thumbnail=self.bot.user.avatar_url)
        else:
            title1 = "__Merchant System notification__"
            message = "Currently you have no monetized roles. "
            await customMessages.system_message(ctx=ctx, sys_msg_title=title1, message=message, color_code=1,
                                                destination=1)

    @merchant.command()
    @commands.check(is_public)
    @commands.check(is_owner)
    async def stop_role(self, ctx, role: Role):
        """
        Command used to change activity status of the role
        :param role:
        :return:
        """
        role_details = merchant_manager.find_role_details(role_id=role.id)
        from pprint import pprint
        pprint(role_details)
        if role_details:
            if role_details['status'] == 'active':
                role_details['status'] = 'inactive'
                if merchant_manager.change_role_details(role_data=role_details):
                    title = '__Role status change notification__'
                    message = f'Role has been deactivated successfully. in order to re-activate it and make it ' \
                              f'available to users again, use command {d["command"]}monetize start_role <@discord.Role>'
                    await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=0,
                                                        destination=1)
                else:
                    title = '__Role status change error__'
                    message = f'Role could not be deactivated, please try again later. Please try again. If the issue ' \
                              f'persists, contact one staff. '
                    await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=1,
                                                        destination=1)

            else:
                title = '__Role status change error__'
                message = f'Role {role} has been already deactivate. '
                await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=1,
                                                    destination=1)
        else:
            title = '__Role status change error__'
            message = f'Role {role} does either not exist in the system or has not been created. Please use ' \
                      f'{d["command"]} monetize community_roles to obtain all roles on the community'
            await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=1,
                                                destination=1)

    @merchant.command()
    @commands.check(is_public)
    @commands.check(is_owner)
    async def start_role(self, ctx, role: Role):
        """
        Change status of the role
        :param role:
        :return:
        """

        role_details = merchant_manager.find_role_details(role_id=role.id)
        from pprint import pprint
        pprint(role_details)
        if role_details:
            if role_details['status'] == 'inactive':
                role_details['status'] = 'active'
                if merchant_manager.change_role_details(role_data=role_details):
                    title = '__Role status change notification__'
                    message = f'Role {role} has been re-activate successfully.'
                    await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=0,
                                                        destination=1)
                else:
                    title = '__Role status change error__'
                    message = f'Role could not be re-activated, please try again later. Please try again. If the issue ' \
                              f'persists, contact one staff. '
                    await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=1,
                                                        destination=1)
            else:
                title = '__Role status change error__'
                message = f'Role {role} is already active. '
                await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=1,
                                                    destination=1)
        else:
            title = '__Role status change error__'
            message = f'Role {role} does either not exist in the system or has not been created. Please use ' \
                      f'{d["command"]} monetize community_roles to obtain all roles on the community'
            await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=1,
                                                destination=1)

    @merchant.command()
    @commands.check(is_owner)
    async def balance(self, ctx):
        """
        Returns the current value of the community wallet in monero and stellar
        :param ctx:
        :return:
        """
        data = merchant_manager.get_wallet_balance(community_id=ctx.message.guild.id)

        if data:
            stellar_balance = data['stellar']['balance']
            get_xlm_point = get_decimal_point(symbol='xlm')
            stellar_real = get_normal(value=str(stellar_balance), decimal_point=get_xlm_point)

            wallet_details = Embed(title='Merchant wallet status',
                                   description="Current state of the Merchan Community wallet",
                                   colour=Color.gold())
            wallet_details.add_field(name='Stellar balance',
                                     value=f"{stellar_real} {CONST_STELLAR_EMOJI}",
                                     inline=False)

            await ctx.author.send(embed=wallet_details)
        else:
            title = '__Balance Check Error__'
            message = f'There has been an issue while obtaining community balance. Please try again later and if the ' \
                      f'issue persists contact the team. '
            await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=1,
                                                destination=1)

    @merchant.command()
    @commands.check(is_owner)
    async def transfer_xlm(self, ctx):
        """
        Transfers Stellar from Merchant corp wallet to community owner's own wallet
        :param ctx:
        :return:
        """
        ticker = 'xlm'
        channel_id = auto_channels["merchant"]  # Channel where message will be sent on transfer
        author_id = ctx.message.author.id
        autho_name = ctx.message.author
        current_time = datetime.utcnow()

        fee_in_stroops = 0

        # Check merchant situatioan and modify fee accordingly
        if not merchant_manager.check_community_license_status(community_id=ctx.message.author.id):
            fee_dollar_details = lpi_wallet.get_fees_by_category(key='wallet_transfer')
            fee_value = fee_dollar_details['fee']  # Get out fee
            in_stellar = convert_to_currency(fee_value, coin_name='stellar')  # Convert fee to currency
            total = (in_stellar['total'])  # Get total in lumne
            rate = (in_stellar['usd'])  # Get conversion rate for info
            fee_in_stroops = (int(total * (10 ** 7)))  # Convert to stroops

        # Get the current minimum withdrawal fee in Dollars
        minimum_with_limit = lpi_wallet.get_fees_by_category(key='merchant_min')
        with_fee = minimum_with_limit['fee']  # Get out fee
        with_fee_stellar = convert_to_currency(with_fee, coin_name='stellar')  # Convert fee to currency
        total_xlm = (with_fee_stellar['total'])
        minimum_in_stroops = (int(total_xlm * (10 ** 7)))  # Convert to piconero

        # Get merchant wallet balance of the community
        balance = merchant_manager.get_balance_based_on_ticker(community_id=ctx.message.guild.id, ticker=ticker)
        # Compare wallet balance to minimum withdrawal limit
        if balance >= minimum_in_stroops:
            if balance > fee_in_stroops:
                # Deduct total amount reuqired from the community merchant wallet
                if merchant_manager.modify_funds_in_community_merchant_wallet(direction=1,
                                                                              community_id=ctx.message.guild.id,
                                                                              wallet_tick='xlm',
                                                                              amount=balance):
                    for_owner = balance - fee_in_stroops
                    #TODO fix bug where it could happen that fee in stroops us greater than the available balance

                    # credit fee to launch pad investment wallet
                    if lpi_wallet.update_lpi_wallet_balance(amount=fee_in_stroops, wallet='xlm', direction=1):

                        # Append withdrawal ammount to the community owner personal wallet
                        if account_mng.update_user_wallet_balance(discord_id=author_id, ticker='xlm', direction=0,
                                                                  amount=for_owner):
                            info_embed = Embed(title='__Corporate account Transaction details__',
                                               description="Here are the details on withdrawal from Merchant "
                                                           "Corporate Account to your personal account.",
                                               colour=Color.green())
                            info_embed.add_field(name='Time of withdrawal',
                                                 value=f"{current_time} (UTC)",
                                                 inline=False)
                            info_embed.add_field(name="Wallet Balance Before Withdrawal",
                                                 value=f"{balance / 10000000} {CONST_STELLAR_EMOJI}",
                                                 inline=False)

                            # Info according to has license or does not have license
                            if fee_in_stroops != 0:
                                info_embed.add_field(name="Final Withdrawal Amount",
                                                     value=f'{balance / 10000000} {CONST_STELLAR_EMOJI}\n'
                                                           f'Service Fee: {fee_in_stroops / 10000000} {CONST_STELLAR_EMOJI} (aprx. {total}$)',
                                                     inline=False)
                            else:
                                info_embed.add_field(name="Final Withdrawal Amount",
                                                     value=f'{balance / 10000000} {CONST_STELLAR_EMOJI}\n'
                                                           f'Service Fee: 0 {CONST_STELLAR_EMOJI} (License activated)',
                                                     inline=False)

                            await ctx.author.send(embed=info_embed)

                            # Send information to corporate account channel

                            corp_info = Embed(title="__ Merchant withdrawal fee incoming to Corp Wallet__",
                                              description="This message was sent from the system, to inform you,"
                                                          "that additional funds have been transfered and credited"
                                                          " to Launch Pad Investment Corporate wallet",
                                              colour=Color.green()
                                              )
                            corp_info.add_field(name='Time of initiated withdrawal',
                                                value=f"{current_time} UTC",
                                                inline=False)
                            corp_info.add_field(name="Merchant Corp Account of:",
                                                value=f"{ctx.message.guild}",
                                                inline=False)
                            corp_info.add_field(name="Owner",
                                                value=f"{ctx.message.author}",
                                                inline=False)
                            corp_info.add_field(name="Income amount to corpo wallet",
                                                value=f"Amount: {fee_in_stroops / 10000000} {CONST_STELLAR_EMOJI}\n"
                                                      f"Amount is 0 if community has purchased monthly license",
                                                inline=False)
                            corp_info.add_field(name="Slip",
                                                value=f"Wallet balance:{balance / 10000000} {CONST_STELLAR_EMOJI}\n"
                                                      f"Net withdrawal: {for_owner / 10000000} {CONST_STELLAR_EMOJI}",
                                                inline=False)
                            notf_channel = self.bot.get_channel(id=int(channel_id))
                            await notf_channel.send(embed=corp_info)

                        else:
                            sys_msg_title = '__System Withdrawal error__'
                            message = f'There has been an issue with withdrawal from Merchant Corporate account to your ' \
                                      f'personal wallet. Please try again later, or contact the staff members. '
                            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                                sys_msg_title=sys_msg_title)
                    else:
                        merch_fee = Embed(title="__Merchant Transfer error__",
                                          description='This is error notification as funds from '
                                                      'corporate Merchant wallet could not be transferred to'
                                                      'Launchpad Investment Corp Wallet. Details bellow ',
                                          colour=Color.red())
                        merch_fee.set_footer(text=f"{current_time}")
                        merch_fee.add_field(name='Discord Details',
                                            value=f"Guild: {ctx.message.guild}\n"
                                                  f"ID: {ctx.message.guild.id}\n"
                                                  f"Owner:{autho_name}\n"
                                                  f"ID: {ctx.message.author.id}")
                        merch_fee.add_field(name='Command',
                                            value=f"{d['command']}corp transfer_xlm",
                                            inline=False)
                        merch_fee.add_field(name='Error details',
                                            value='Could not apply fees from transaction to Launch Pad Investment Corp'
                                                  'wallet.',
                                            inline=False)
                        merch_fee.add_field(name='Details',
                                            value=f"To Withdraw: {balance / 10000000} {CONST_STELLAR_EMOJI}\n"
                                                  f"Fees: {fee_in_stroops / 10000000}{CONST_STELLAR_EMOJI}\n"
                                                  f"To owner: {for_owner / 10000000}{CONST_STELLAR_EMOJI}",
                                            inline=False)
                        merch_fee.add_field(name='Action Required',
                                            value='Try Again later')
                        await channel_id.send(embed=merch_fee)

                        sys_msg_title = '__System Withdrawal error__'
                        message = f'There has been an issue with withdrawal from Merchant Corporate account to your ' \
                                  f'personal wallet. Please try again later, or contact the staff members. '
                        await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                            sys_msg_title=sys_msg_title)
                else:
                    sys_msg_title = '__System Message error__'
                    message = f'There has been an error while trying to withdraw total balance from Stellar Merchant ' \
                              f'Community Wallet. Please try again later and if the issue persists contact support staff.'
                    await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                        sys_msg_title=sys_msg_title)
            else:
                sys_msg_title = '__System Message error__'
                message = f'Fees are currently greater than the balance amount to initiate withdrawal' \
                          f'Current Balance is {balance / 10000000} {CONST_STELLAR_EMOJI} while ' \
                          f'fee is {total_xlm}{CONST_STELLAR_EMOJI}'
                await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                    sys_msg_title=sys_msg_title)
        else:
            sys_msg_title = '__System Message error__'
            message = f'You have insufficient balance in Stellar Merchant Community wallet, to initiate withdrawal ' \
                      f'system. Current minimum balance for withdrawal is set to {total_xlm} {CONST_STELLAR_EMOJI}' \
                      f' XLM and your balance is {balance / 10000000} {CONST_STELLAR_EMOJI}'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=sys_msg_title)

    @create_role.error
    async def create_role_on_error(self, ctx, error):
        """
        Custom error handlers for role creation procedure
        :param ctx:
        :param error:
        :return:
        """
        if isinstance(error, commands.MissingRequiredArgument):
            message = f'You have not provide some of the arguments. Command structure is:\n' \
                      f'{d["command"]}merchant monetize create_role <xcash value> <length in weeks as ' \
                      f'integer> <length in days as integer>  <length in hours as integer>'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title="__Role creation error___")
        elif isinstance(error, commands.BadArgument):
            message = f'You have not provide some of the arguments. Command structure is:\n' \
                      f'{d["command"]}merchant monetize create_role <dollar value $> <length in weeks ' \
                      f'as integer> <length in days as integer>  <length in hours as integer>\n' \
                      f'dollar value => float number with tvo decimals, where decimals are indicated with .\n' \
                      f'length in weeks => Integer\n' \
                      f'length in days => Integer\n' \
                      f'length in hours => Integer\n' \
                      f'Note: all values for duration accept 0 as property which indicates that duration for calculation' \
                      f'will be excluded. At least one duration property needs to have integer greater than 0.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)

    @merchant.error
    async def merchant_error(self, ctx, error):
        """
        Custom error handler for merchant system registration
        :param ctx:
        :param error:
        :return:
        """
        if isinstance(error, commands.CheckFailure):
            message = f'Something went wrong while trying to access **merchant platform**:\n' \
                      f'\n' \
                      f'All checks need to be met in order for access to be granted:\n' \
                      f' --> You need to be the owner of community \n' \
                      f' --> You need to have personal discord wallet  \n' \
                      f'--> Community needs to be registered in the system \n' \
                      f'--> Command needs to be executed on public channel \n' \
                      f'If issue persists please contact staff.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1)

    @merchant_initiate.error
    async def merchant_initiate_error(self, ctx, error):
        """
        Custom error handler for merchant system registration
        :param ctx:
        :param error:
        :return:
        """
        if isinstance(error, commands.CheckFailure):
            message = f'Something fot wrong while trying to register for merchant service:\n' \
                      f'All checks need to be met in order to be successful:\n' \
                      f'--> You need to be the owner :white_check_mark: \n' \
                      f'--> You need to have personal discord wallet :white_check_mark: \n' \
                      f'--> Command needs to be executed on public channel :white_check_mark:\n' \
                      f'__If issue persists please contact staff.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)

        elif isinstance(error, commands.BotMissingPermissions):
            message = f'You can not register {ctx.guild} into the system because {self.bot.user} does not have ' \
                      f' ***Manage Role*** permission which is required for bot to function optimally.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)

    @create_role.error
    async def create_role_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            message = f"In order for system to be able to create role it requires **manage role** permission"
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)
        elif isinstance(error, commands.CheckFailure):
            message = f'In order to be able to create role on {ctx.message.guild} you need to execute command on one ' \
                      f'of the public channels of the community you are owner off.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)
        elif isinstance(error, commands.BadArgument):
            message = f'You have provided wrong command arguments. Appropriate command structure is:\n' \
                      f'**{d["command"]}merchant monetize create_role <role name> <dolar value> <week amount> ' \
                      f'<day amount> <hour amount> <minute amount>.\n' \
                      f'__Note__: duration amount need to be given as integer.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)

    @delete_role.error
    async def delete_role_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            message = f"In order for system to be able to delete role, bot requires **manage role** permission"
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)
        elif isinstance(error, commands.BadArgument):
            message = f"You have provided bad argument for Role parameter. Use @ infront of the role name and tag it"
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)

    @delete_role.error
    async def community_tole_check_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to be able to check all monetized roles on community, please execute the function' \
                      f' on one of the channels on community since rights need to be checked. In order to be able to ' \
                      f'access the roles you need to be as well owner of the community'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)

    @stop_role.error
    async def stop_role_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            message = f"You have provided bad argument for Role parameter. Use @ infront of the role name and tag it"
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)
        elif isinstance(error, commands.CheckFailure):
            message = f'In order to be able to deactivate role you need to execute the function on public channel ' \
                      f' and be the owner of the community. Please try again and if issue persist contact staff.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)

    @start_role.error
    async def start_role_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            message = f"You have provided bad argument for Role parameter. Use @ infront of the role name and tag it"
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)
        elif isinstance(error, commands.CheckFailure):
            message = f'In order to be able to re-activate role you need to execute the function on public channel ' \
                      f' and be the owner of the community. Please try again and if issue persist contact staff.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)


def setup(bot):
    bot.add_cog(MerchantCommunityOwner(bot))
