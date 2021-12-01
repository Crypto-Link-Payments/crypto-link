import re
from datetime import datetime

from nextcord import Role, Embed, Color, utils
from nextcord.ext import commands
from utils.customCogChecks import is_owner, has_wallet, is_public, merchant_com_reg_stats
from cogs.utils.monetaryConversions import convert_to_currency
from cogs.utils.monetaryConversions import get_normal
from cogs.utils.systemMessaages import CustomMessages

customMessages = CustomMessages()
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_ROLE_CREATION_ERROR = "__Role creation error___"
CONST_ROLE_STATUS_CHANGE_ERROR = "__Role status change error__"
CONST_SYSTEM_ERROR = '__Merchant System Error__'
CONST_ROLE_STATUS_CHANGE = '__Role status change error__'
CONST_BAD_ARGUMENT_ROLE = "You have provided bad argument for Role parameter. Use @ in-front of " \
                          "the role name and tag it"


class MerchantCommunityOwner(commands.Cog):
    """
    Discord COGS handling commands for merchant system from community owner perspective
    """

    def __init__(self, bot):
        self.bot = bot
        self.merchant_channel_info = bot.backoffice.auto_messaging_channels["merchant"]
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.merchant = self.backoffice.merchant_manager

    @commands.command()
    @commands.check(is_owner)
    @commands.check(has_wallet)
    @commands.check(is_public)
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def merchant_initiate(self, ctx):

        """
        Command to initiate merchant setup process and register community into the Merchant system
        :param ctx:
        :return:
        """

        if not self.merchant.check_if_community_exist(community_id=ctx.message.guild.id):  # Check if not registered
            if self.merchant.register_community_wallet(community_id=ctx.message.guild.id,
                                                       community_owner_id=ctx.message.author.id,
                                                       community_name=f'{ctx.message.guild}'):  # register community wallet
                msg_title = ':rocket: __Community Wallet Registration Status___ :rocket:'
                message = f'You have successfully merchant system on ***{ctx.message.guild}***. You can proceed' \
                          f' with `{self.command_string}merchant` in order to familiarize yourself with all available' \
                          f' commands or have a look at ***merchant system manual on' \
                          f' `{self.command_string}merchant manual` '
                await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=0,
                                                    destination=1)

                merchant_notification = self.bot.get_channel(id=int(self.merchant_channel_info))
                new_merch = Embed(title=f'New Community Has registered for merchant',
                                  description=f'New community has registered for merchant service',
                                  colour=Color.purple())
                new_merch.add_field(name='Community',
                                    value=f'{ctx.guild}')

                await merchant_notification.send(embed=new_merch)

            else:
                msg_title = ':warning:  __Merchant Registration Status___ :warning: '
                message = f'There has been an issue while registering wallet into the system. Please try again later.' \
                          f' or contact one of the support staff. '
                await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=1,
                                                    destination=1)
        else:
            msg_title = ':warning:  __Community Wallet Registration Status___ :warning: '
            message = f'You have already registered {ctx.guild} for Merchant system on {self.bot.user.mention}. Proceed' \
                      f' with command ```{self.command_string}merchant``` or ```{self.command_string}```'
            await customMessages.system_message(ctx=ctx, sys_msg_title=msg_title, message=message, color_code=0,
                                                destination=1)

    @commands.group()
    @commands.check(is_public)
    @commands.check(is_owner)  # Check if author is community owner
    @commands.check(merchant_com_reg_stats)  # Check if community has been registered in the system
    @commands.check(has_wallet)  # Check if owner has community wallet
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def merchant(self, ctx):
        if ctx.invoked_subcommand is None:
            title = "💱 __Merchant System Message Setup__💱 "
            description = 'All available commands under ***merchant*** category.'
            list_of_commands = [
                {"name": f':information_source: How to Monetize Roles :information_source: ',
                 "value": f'```{self.command_string}merchant manual```'},
                {"name": f':information_source: Access Role Management sub-commands :information_source: ',
                 "value": f'```{self.command_string}merchant roles```'},
                {"name": f':moneybag: Access Merchant Wallet sub-commands :moneybag:   ',
                 "value": f'```{self.command_string}merchant wallet```'},
                {"name": f':moneybag: List Active Roles on Community :moneybag:   ',
                 "value": f'```{self.command_string}merchant active```'}

            ]
            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_commands,
                                               c=Color.purple())

    @merchant.command()
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def manual(self, ctx):
        manual = Embed(title=':convenience_store: __Merchant system manual__ :convenience_store: ',
                       colour=Color.purple())
        manual.add_field(name=':one: Create monetized roles :one:',
                         value=f'```{self.command_string}merchant role create <role name> <role value in $> '
                               f'<weeks> <days> <hours> <minutes>```\n'
                               f'\n:warning: __Required parameters__ :warning: \n'
                               f'\n'
                               f'> :white_check_mark:  No spaces in role name and max length 20 characters\n'
                               f'> :white_check_mark:  At least one of the time parameters needs to be greater than 0\n'
                               f'> :white_check_mark:  Dollar value of the role required to be greater than 0.00 $',
                         inline=False)
        manual.add_field(name=':two: Additional setup :two:',
                         value=f'> Allow role to be mentioned by everyone'
                               f'> assign rights to created role ',
                         inline=False)
        manual.add_field(name=':three: Inform members :three:',
                         value=f'Once role successfully created, it can be purchased by your members with command\n'
                               f'```{self.command_string}membership subscribe @discord.Role```',
                         inline=False)
        await ctx.channel.send(embed=manual, delete_after=600)

    @merchant.group(aliases=['role', 'r'])
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def roles(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ":man_juggling: __Merchant Role Management__ :man_juggling: "
            description = 'All available commands to manage monetized roles'
            list_of_commands = [
                {"name": f':information_source: Create new monetized role :information_source: ',
                 "value": f'```{self.command_string}merchant role create <role name> <role value in $> '
                          f'<weeks> <days> <hours> <minutes>```'},

                {"name": f':play_pause:  Stop Active Role :play_pause:  ',
                 "value": f'```{self.command_string}merchant role stop <@discord.Role>```'},

                {"name": f':arrow_forward: Re-start inactive role :arrow_forward:  ',
                 "value": f'```{self.command_string}merchant role start <@discord.Role>```'},

                {"name": f':wastebasket: Remove role from the system :wastebasket:   ',
                 "value": f'```{self.command_string}merchant role delete <@discord.Role>```'},

            ]
            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_commands,
                                               c=Color.purple())

    @roles.command(aliases=["new"])
    @commands.check(is_public)
    async def create(self, ctx, role_name: str, dollar_value: float, weeks_count: int, days_count: int,
                     hours_count: int, minutes_count: int):
        """
        Procedure to create role in the system
        :param ctx:
        :param role_name: String representation of the role
        :param dollar_value: Value in dollar
        :param weeks_count: length in weeks
        :param days_count: length in days
        :param hours_count: length in hours
        :param minutes_count: length in minutes
        :return:
        """

        in_penny = (int(dollar_value * (10 ** 2)))  # Convert to pennies
        total = weeks_count + days_count + hours_count + minutes_count

        if not (weeks_count < 0) and not (days_count < 0) and not (hours_count < 0) and not (minutes_count < 0) and (
                total > 0):

            if not re.search("[~!#$%^&*()_+{}:;\']", role_name):  # Check for special characters
                if len(role_name) <= 20:  # Check for role length
                    role = utils.get(ctx.guild.roles, name=role_name)  # Check if role present already
                    if not role:
                        if in_penny > 0:  # Checks if it is greater than 0
                            created_role = await ctx.guild.create_role(
                                name=role_name)  # Create role and return its details

                            # TO Store in database
                            new_role = {
                                "roleId": int(created_role.id),
                                "roleName": f'{created_role}',
                                "communityId": int(ctx.guild.id),
                                "pennyValues": int(in_penny),
                                "weeks": int(weeks_count),
                                "days": int(days_count),
                                "hours": int(hours_count),
                                "minutes": int(minutes_count),
                                "status": "active"
                            }

                            if self.merchant.register_role(new_role):

                                # Send the message to the owner
                                msg_title = ':convenience_store: __Merchant System Information___ :convenience_store: '
                                sys_title = f":man_juggling: ***Role successfully created*** :man_juggling: "
                                message = f'Details:\n' \
                                          f'```Role Name : {role_name}\n' \
                                          f'Role ID: {created_role.id}\n' \
                                          f'Value: {dollar_value} $\n' \
                                          f'Duration of role: \n' \
                                          f'{weeks_count} week/s, \n{days_count} day/s \n{hours_count} hour/s\n' \
                                          f'{minutes_count} minute/s```'

                                await customMessages.system_message(ctx=ctx, sys_msg_title=sys_title, message=message,
                                                                    color_code=0,
                                                                    destination=1, embed_title=msg_title)

                                message_title = ':convenience_store: __Merchant System Information___ :convenience_store: '
                                sys_title = ":mega: Time to inform your members on available role to be " \
                                            "purchased. :mega:"
                                message = f'Users can now apply for the role by executing the' \
                                          f'```command bellow: \n {self.command_string}membership subscribe ' \
                                          f'<@Discord Role>```' \
                                          f'Thank You for using Merchant System!'
                                await customMessages.system_message(ctx=ctx, sys_msg_title=sys_title, message=message,
                                                                    color_code=0,
                                                                    destination=1, embed_title=message_title)
                            else:
                                message = f'Role could not be stores into the system at this point. Please try again' \
                                          f' later. We apologize for inconvenience.'
                                await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_ROLE_CREATION_ERROR,
                                                                    message=message,
                                                                    color_code=1,
                                                                    destination=1)
                        else:
                            message = 'The amount user will have to pay for role needs to be greater than 0.00$'
                            await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_ROLE_CREATION_ERROR,
                                                                message=message,
                                                                color_code=1,
                                                                destination=1)
                    else:
                        message = f'Role with name ***{role_name}*** already exist on the community ' \
                                  f'or in the system and can not be created.'
                        await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_ROLE_CREATION_ERROR,
                                                            message=message,
                                                            color_code=1,
                                                            destination=1)
                else:
                    message = f'Role with name ***{role_name}*** is too long. Max allowed length is 10 characters'
                    await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_ROLE_CREATION_ERROR,
                                                        message=message,
                                                        color_code=1,
                                                        destination=1)
            else:
                message = f'Role with name ***{role_name}*** includes special characters which are' \
                          f' not allowed. Please repeat the process'
                await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_ROLE_CREATION_ERROR, message=message,
                                                    color_code=1,
                                                    destination=1)

        else:
            message = 'Role could not be create since the length of the role is either' \
                      ' limitless or expiration time is' \
                      ' not in future. In order to create a role data for week, days hours and minutes needs ' \
                      'to be provide as followed:\n' \
                      'week: whole number greater than 0\n' \
                      'day: whole number greater than 0\n' \
                      'hour: whole number greater than 0\n' \
                      'minute: whole number greater than 0\n' \
                      'Note: 0 is also acceptable however the sum of all variables needs to be greater than 0 at ' \
                      'the end. '
            await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_ROLE_CREATION_ERROR, message=message,
                                                color_code=1,
                                                destination=1)

    @roles.command()
    @commands.check(is_public)
    async def delete(self, ctx, discord_role: Role):
        """
        Delete monetized role from the system and community
        :param ctx:
        :param discord_role:
        :return:
        """
        if self.merchant.find_role_details(role_id=discord_role.id):
            if self.merchant.remove_monetized_role_from_system(role_id=discord_role.id,
                                                               community_id=ctx.message.guild.id):
                await discord_role.delete()
                title = ':convenience_store: Merchant System Notification__:convenience_store: '
                message = f'Monetized role has been successfully removed from the Crypto Link Merchant System, ' \
                          f'{ctx.guild} and from all the users who has obtained it.'
                await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=0,
                                                    destination=1)
            else:
                message = 'Role could not be removed from the Merchant System. Please contact the team with details.'
                await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_SYSTEM_ERROR, message=message,
                                                    color_code=0,
                                                    destination=1)
        else:
            message = 'This Role could not be removed as it is not registered in the merchant system'
            await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_SYSTEM_ERROR, message=message,
                                                color_code=0,
                                                destination=1)

    @roles.command()
    async def stop(self, ctx, role: Role):
        """
        Command used to change activity status of the role
        """

        role_details = self.merchant.find_role_details(role_id=role.id)
        if role_details:
            if role_details['status'] == 'active':
                role_details['status'] = 'inactive'
                if self.merchant.change_role_details(role_data=role_details):
                    title = '__Role status change notification__'
                    message = f'Role has been deactivated successfully. in order to re-activate it and make it ' \
                              f'available to users again, use command' \
                              f' `{self.command_string}monetize start_role <@discord.Role>`'
                    await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=0,
                                                        destination=1)
                else:
                    message = 'Role could not be deactivated, please try again later. Please try again. If the issue ' \
                              'persists, contact one staff. '
                    await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_ROLE_STATUS_CHANGE_ERROR,
                                                        message=message, color_code=1,
                                                        destination=1)

            else:
                message = f'Role {role} has been already deactivate. '
                await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_ROLE_STATUS_CHANGE_ERROR,
                                                    message=message, color_code=1,
                                                    destination=1)
        else:
            message = f'Role {role} does either not exist in the system or has not been created. Please use ' \
                      f'`{self.command_string} monetize community_roles` to obtain all roles on the community'
            await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_ROLE_STATUS_CHANGE_ERROR, message=message,
                                                color_code=1,
                                                destination=1)

    @roles.command()
    async def start(self, ctx, role: Role):
        """
        Change status of the role
        :param ctx: Discord Context
        :param role:
        :return:
        """

        role_details = self.merchant.find_role_details(role_id=role.id)
        if role_details:
            if role_details['status'] == 'inactive':
                role_details['status'] = 'active'
                if self.merchant.change_role_details(role_data=role_details):
                    title = '__Role status change notification__'
                    message = f'Role {role} has been re-activate successfully.'
                    await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=0,
                                                        destination=1)
                else:
                    message = 'Role could not be re-activated, please try again later. Please try again. If the ' \
                              'issue persists, contact one staff. '
                    await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_ROLE_STATUS_CHANGE,
                                                        message=message, color_code=1,
                                                        destination=1)
            else:
                message = f'Role {role} is already active. '
                await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_ROLE_STATUS_CHANGE, message=message,
                                                    color_code=1,
                                                    destination=1)
        else:
            message = f'Role {role} does either not exist in the system or has not been created. Please use ' \
                      f'`{self.command_string}` monetize community_roles to obtain all roles on the community'
            await customMessages.system_message(ctx=ctx, sys_msg_title=CONST_ROLE_STATUS_CHANGE, message=message,
                                                color_code=1,
                                                destination=1)

    @merchant.command()
    @commands.check(is_owner)
    @commands.check(is_public)
    async def active(self, ctx):
        """
        Return all the community roles from the system
        :param ctx:
        :return:
        """

        roles = self.merchant.get_all_roles_community(community_id=ctx.message.guild.id)
        title = f':circus_tent: __Available Roles on Community {ctx.message.guild}__ :circus_tent: '
        description = 'Details on monetized role.'
        if roles:
            for role in roles:
                dollar_value = float(role["pennyValues"] / 100)
                values = [{"name": ':person_juggling: Role Name :person_juggling: ',
                           "value": f'```{role["roleName"]} (ID: {role["roleId"]})```'},
                          {"name": ':vertical_traffic_light: Status :vertical_traffic_light:',
                           "value": f'```{role["status"]}```'},
                          {"name": ':dollar: Price :dollar: ', "value": f"```${dollar_value}```"},
                          {"name": ':timer: Role Length :timer:',
                           "value": f"```{role['weeks']} week/s \n{role['days']} day/s \n{role['hours']} "
                                    f"hour/s \n{role['minutes']} minute/s```"}]
                await customMessages.embed_builder(ctx=ctx, title=title, description=description, destination=1,
                                                   data=values, thumbnail=self.bot.user.avatar.url, c=Color.blue())
        else:
            title1 = "__Merchant System notification__"
            message = "Currently you have no monetized roles. "
            await customMessages.system_message(ctx=ctx, sys_msg_title=title1, message=message, color_code=1,
                                                destination=1)

    @merchant.group(aliases=['w', 'acc', 'account'])
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def wallet(self, ctx):
        if ctx.invoked_subcommand is None:
            title = "💱 __Merchant Wallet Commands__💱 "
            description = 'All available commands to operate with merchant wallet of the community.'
            list_of_commands = [
                {"name": f':moneybag: Get Balance Status :moneybag:  ',
                 "value": f'```{self.command_string}merchant wallet balance```\n'
                          f'`Aliases: bal`'},
                {"name": f':broom: Withdraw funds to your personal account :broom: ',
                 "value": f'```{self.command_string}merchant wallet sweep```\n'
                          f'`Aliases: withdraw`'},
            ]
            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_commands,
                                               c=Color.purple())

    @wallet.command(aliases=['bal'])
    @commands.check(is_owner)
    async def balance(self, ctx):
        """
        Returns the current value of the community wallet iin stellar
        :param ctx:
        :return:
        """
        data = self.merchant.get_wallet_balance(community_id=ctx.message.guild.id)

        if data:
            stellar_balance = data['xlm']
            stellar_real = get_normal(value=str(stellar_balance), decimal_point=7)

            wallet_details = Embed(title=' :bank: __Merchant Wallet Balance__ :bank:',
                                   description=f"Current balance of the ***{ctx.guild}*** wallet",
                                   colour=Color.gold())
            wallet_details.add_field(name=f':moneybag:  Stellar Lumen :moneybag: ',
                                     value=f"```{stellar_real} XLM```",
                                     inline=False)
            wallet_details.add_field(name=f':warning: Withdrawal from merchant wallet :warning: ',
                                     value=f"Please use command ```{self.command_string}merchant wallet sweep``` to withdraw all"
                                           f" available funds to your personal wallet. Withdrawing is allowed only"
                                           f" for the owner of the ***{ctx.guild}***",
                                     inline=False)
            await ctx.author.send(embed=wallet_details)

        else:
            title = '__Balance Check Error__'
            message = 'There has been an issue while obtaining community balance. Please try again later and if the ' \
                      'issue persists contact the team. '
            await customMessages.system_message(ctx=ctx, sys_msg_title=title, message=message, color_code=1,
                                                destination=1)

    @wallet.command(aliases=["withdraw"])
    @commands.check(is_owner)
    async def sweep(self, ctx):
        """
        Transfers Stellar from Merchant corp wallet to community owner's own wallet
        :param ctx:
        :return:
        """
        ticker = 'xlm'

        # Details of the author
        current_time = datetime.utcnow()

        # Fee limits on Crypto Link system for merchant
        withdrawal_min = self.backoffice.bot_manager.get_fees_by_category(key='merchant_min')  # Minimum withdrawal in $
        withdrawal_min_dollar = withdrawal_min['fee']

        min_in_xlm = convert_to_currency(withdrawal_min_dollar,
                                         coin_name='stellar')  # Returns dict of usd and total stroop

        # Checks if conversion rates obtained
        conversion_rates_obtained = False
        if not min_in_xlm.get("error"):
            conversion_rates_obtained = True

        # Check if conversion obtained from the coingecko
        if conversion_rates_obtained:  # Check if conversion rates obtained
            withdrawal_limit_stroops = min_in_xlm['total']  # Stroop value of minimal withdrawal limit

            # community wallet balance in stroops
            com_balance_stroops = self.merchant.get_balance_based_on_ticker(community_id=ctx.message.guild.id,
                                                                            ticker=ticker)  # Stroops returned

            # balance of community needs to be greater than final withdrawal limit and final fee stroops
            if com_balance_stroops >= withdrawal_limit_stroops:

                wallet_transfer_fee = self.backoffice.bot_manager.get_fees_by_category(
                    key='wallet_transfer')  # Percentage as INT

                fee_perc = wallet_transfer_fee['fee']  # Atomic representation of fees
                fee_as_dec = fee_perc / (10 ** 2)  # 1% get converted to 0,01
                cl_earnings = int(com_balance_stroops * fee_as_dec)  # Earning for the system
                net_owner = com_balance_stroops - cl_earnings  #

                # Empty the community wallet
                if self.merchant.modify_funds_in_community_merchant_wallet(direction=1,
                                                                           community_id=ctx.message.guild.id,
                                                                           wallet_tick='xlm',
                                                                           amount=com_balance_stroops):

                    # Notification channel
                    notification_channel = self.bot.get_channel(id=int(self.merchant_channel_info))
                    # credit fee to launch pad investment wallet

                    if self.backoffice.bot_manager.update_cl_wallet_balance(to_update={"balance": cl_earnings},
                                                                            ticker='xlm'):

                        # Append withdrawal amount to the community owner personal wallet
                        if self.backoffice.account_mng.update_user_wallet_balance(discord_id=ctx.author.id,
                                                                                  ticker='xlm',
                                                                                  direction=0,
                                                                                  amount=net_owner):

                            info_embed = Embed(
                                title=' :money_with_wings: __Community account Transaction details__  '
                                      ':money_with_wings:',
                                description="Here are the details on withdrawal from Merchant "
                                            "Community Account to your personal account.",
                                colour=Color.purple())
                            info_embed.add_field(name=':clock: Time of withdrawal :clock: ',
                                                 value=f"```{current_time} (UTC)```",
                                                 inline=False)
                            info_embed.add_field(name=":moneybag: Wallet Balance Before Withdrawal :moneybag: ",
                                                 value=f"```{com_balance_stroops / (10 ** 7)} XLM```",
                                                 inline=False)

                            # Info according to has license or does not have license
                            info_embed.add_field(name=":atm: Final Withdrawal Amount :atm: ",
                                                 value=f'```Total: {com_balance_stroops / (10 ** 7)} XLM\n'
                                                       f'\n'
                                                       f'Merchant Fee: {cl_earnings / (10 ** 7)} XLM\n'
                                                       f'------------------------\n'
                                                       f'Net: {net_owner / (10 ** 7)} {CONST_STELLAR_EMOJI}```',
                                                 inline=False)

                            await ctx.author.send(embed=info_embed)

                            # Send information to crypto link staff sys channel on incoming funds
                            corp_info = Embed(
                                title=":convenience_store: __ Merchant withdrawal fee incoming to Corp"
                                      " Wallet__ :convenience_store:",
                                description="This message was sent from the system, to inform you,"
                                            "that additional funds have been transferred and credited"
                                            " to Crypto Link Corporate wallet",
                                colour=Color.green()
                            )
                            corp_info.add_field(name=':clock: Time of initiated withdrawal :clock:',
                                                value=f"```{current_time} UTC```",
                                                inline=False)
                            corp_info.add_field(name=" :bank: Merchant Corp Account :bank:",
                                                value=f"```{ctx.message.guild}```",
                                                inline=False)
                            corp_info.add_field(name=":crown: Guild Owner :crown: ",
                                                value=f"```{ctx.message.author}```",
                                                inline=False)
                            corp_info.add_field(name=":money_mouth: Income amount to corporate wallet :money_mouth: ",
                                                value=f"```Amount: {cl_earnings / (10 ** 7)} XLM```",
                                                inline=False)
                            corp_info.add_field(name=":receipt: Transaction Slip :receipt: ",
                                                value=f"```:moneybag: balance:{com_balance_stroops / (10 ** 7)} "
                                                      f"{CONST_STELLAR_EMOJI}\n:atm: Net withdrawal:"
                                                      f" {net_owner / (10 ** 7)} {CONST_STELLAR_EMOJI}```",
                                                inline=False)
                            await notification_channel.send(embed=corp_info)

                            await self.backoffice.stats_manager.update_cl_earnings(amount=cl_earnings,
                                                                                   system='merchant',
                                                                                   token='xlm',
                                                                                   time=current_time,
                                                                                   user=f'{ctx.author}',
                                                                                   user_id=int(ctx.author.id))
                        else:
                            sys_msg_title = '__System Withdrawal error__'
                            message = 'There has been an issue with withdrawal from Merchant Corporate ' \
                                      'account to your personal wallet. Please try again later, or contact' \
                                      ' the staff members. '
                            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                                sys_msg_title=sys_msg_title)
                    else:
                        merch_fee = Embed(title="__Merchant Transfer error__",
                                          description='This is error notification as funds from '
                                                      'corporate Merchant wallet could not be transferred to'
                                                      'Crypto Link wallet. Details bellow ',
                                          colour=Color.red())
                        merch_fee.set_footer(text=f"{current_time}")
                        merch_fee.add_field(name='Discord Details',
                                            value=f"Guild: {ctx.message.guild}\n"
                                                  f"ID: {ctx.message.guild.id}\n"
                                                  f"Owner:{ctx.message.author}\n"
                                                  f"ID: {ctx.message.author.id}")
                        merch_fee.add_field(name='Command',
                                            value=f"{self.command_string}corp transfer_xlm",
                                            inline=False)
                        merch_fee.add_field(name='Error details',
                                            value='Could not apply fees from transaction to Launch Pad Investment Corp'
                                                  'wallet.',
                                            inline=False)
                        merch_fee.add_field(name='Details',
                                            value=f"To Withdraw: {com_balance_stroops / (10 ** 7)} {CONST_STELLAR_EMOJI}\n"
                                                  f"Fees: {cl_earnings / (10 ** 7)}{CONST_STELLAR_EMOJI}\n"
                                                  f"To owner: {net_owner / (10 ** 7)}{CONST_STELLAR_EMOJI}",
                                            inline=False)
                        merch_fee.add_field(name='Action Required',
                                            value='Try Again later')
                        await notification_channel.send(embed=merch_fee)

                        sys_msg_title = '__System Withdrawal error__'
                        message = 'There has been an issue with withdrawal from Merchant Corporate account to your ' \
                                  'personal wallet. Please try again later, or contact the staff members. '
                        await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                            sys_msg_title=sys_msg_title)
                else:
                    message = 'There has been an internal error while trying to withdraw total balance from Stellar ' \
                              'Merchant Community Wallet. Please try again later and if the issue persists' \
                              ' contact support staff.'
                    await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                        sys_msg_title=CONST_SYSTEM_ERROR)
            else:
                message = f'Minimum withdrawal requirements not met. Current minimum balance for withdrawal is set to ' \
                          f'{withdrawal_limit_stroops / (10 ** 7)}' \
                          f' XLM and your balance is {com_balance_stroops / (10 ** 7)}XLM'
                await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                    sys_msg_title=CONST_SYSTEM_ERROR)
        else:
            message = f'Withdrawal could not be processed at this moment, as live conversion rates from Coingecko' \
                      f' could not be obtained. Please try again later. Thank you for your understanding.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=CONST_SYSTEM_ERROR)

    @create.error
    async def create_role_on_error(self, ctx, error):

        """
        Custom error handlers for role creation procedure
        :param ctx:
        :param error:
        :return:
        """
        if isinstance(error, commands.MissingRequiredArgument):
            message = f'You have not provide some of the arguments. Command structure is:\n' \
                      f'{self.command_string}merchant monetize create_role <dollar value> <length in weeks as ' \
                      f'integer> <length in days as integer>  <length in hours as integer>'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title="__Role creation error___")
        elif isinstance(error, commands.BadArgument):
            message = f'You have not provide some of the arguments. Command structure is:\n' \
                      f'{self.command_string}merchant monetize create_role <dollar value $> <length in weeks ' \
                      f'as integer> <length in days as integer>  <length in hours as integer>\n' \
                      f'dollar value => float number with tvo decimals, where decimals are indicated with .\n' \
                      f'length in weeks => Integer\n' \
                      f'length in days => Integer\n' \
                      f'length in hours => Integer\n' \
                      f'Note: all values for duration accept 0 as property which indicates that duration for' \
                      f' calculation ' \
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
        if isinstance(error, commands.BotMissingPermissions):
            message = f'{self.bot.user.mention} ***_{error}_***'
            title = "Bot missing required permissions for Merchant System"
            await ctx.channel.send(content=f'{ctx.author.mention}')
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)

        elif isinstance(error, commands.CheckFailure):
            message = 'Something went wrong while trying to access **merchant platform**:\n' \
                      '\n' \
                      'All checks need to be met in order for access to be granted:\n' \
                      ' > - You need to be the owner of community \n' \
                      ' > - You need to have personal discord wallet  \n' \
                      ' > - Community needs to be registered in the system \n' \
                      ' > -  Command needs to be executed on public channel \n' \
                      'If issue persists please contact staff.'
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
            message = 'Something went wrong while trying to register for merchant service:\n' \
                      'All checks need to be met in order to be successful:\n' \
                      '--> You need to be the owner :white_check_mark: \n' \
                      '--> You need to have personal discord wallet :white_check_mark: \n' \
                      '--> Command needs to be executed on public channel :white_check_mark:\n' \
                      '__If issue persists please contact staff.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)
        elif isinstance(error, commands.BotMissingPermissions):
            message = f'You can not register {ctx.guild} into the system because {self.bot.user} does not have ' \
                      f' ***Manage Role*** permission which is required for bot to function optimally.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)

    @create.error
    async def create_role_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to be able to create role on {ctx.message.guild} you need to execute command on one ' \
                      f'of the public channels of the community you are owner off.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)
        elif isinstance(error, commands.BadArgument):
            message = f'You have provided wrong command arguments. Appropriate command structure is:\n' \
                      f'**{self.command_string}merchant monetize create_role <role name> <dollar value> <week amount> ' \
                      f'<day amount> <hour amount> <minute amount>.\n' \
                      f'__Note__: duration amount need to be given as integer.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)
        elif isinstance(error, commands.MissingRequiredArgument):
            message = f'You forgot to provide required variables to be able to create monetized role:\n' \
                      f'**{self.command_string}merchant monetize create_role <role name> <dollar value> <week amount> ' \
                      f'<day amount> <hour amount> <minute amount>.\n' \
                      f'__Note__: duration amount need to be given as integer.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)

    @delete.error
    async def delete_role_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            message = "In order for system to be able to delete role, bot requires **manage role** permission"
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)
        elif isinstance(error, commands.BadArgument):
            await customMessages.system_message(ctx=ctx, color_code=1, message=CONST_BAD_ARGUMENT_ROLE, destination=0)

        elif isinstance(error, commands.CheckFailure):
            message = 'In order to be able to check all monetized roles on community, please execute the function' \
                      ' on one of the channels on community since rights need to be checked. In order to be able to ' \
                      'access the roles you need to be as well owner of the community'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)

    @stop.error
    async def stop_role_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await customMessages.system_message(ctx=ctx, color_code=1, message=CONST_BAD_ARGUMENT_ROLE, destination=0)
        elif isinstance(error, commands.CheckFailure):
            message = 'In order to be able to deactivate role you need to execute the function on public channel ' \
                      ' and be the owner of the community. Please try again and if issue persist contact staff.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)

    @start.error
    async def start_role_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await customMessages.system_message(ctx=ctx, color_code=1, message=CONST_BAD_ARGUMENT_ROLE, destination=0)
        elif isinstance(error, commands.CheckFailure):
            message = 'In order to be able to re-activate role you need to execute the function on public channel ' \
                      ' and be the owner of the community. Please try again and if issue persist contact staff.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0)


def setup(bot):
    bot.add_cog(MerchantCommunityOwner(bot))
