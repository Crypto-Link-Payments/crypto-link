"""
COGS which handle explanation  on commands available to communicate with the Horizon Endpoints from Discord
"""

from discord.ext import commands
from discord import Colour
from cogs.utils.systemMessaages import CustomMessages
from cogs.utils.securityChecks import check_stellar_address
from stellar_sdk.exceptions import BadRequestError, NotFoundError
from horizonCommands.utils.tools import format_date
from horizonCommands.utils.customMessages import account_create_msg, send_details_for_stellar, send_details_for_asset, \
    horizon_error_msg

custom_messages = CustomMessages()

CONST_ACCOUNT_ERROR = '__Account Not Registered__'


class HorizonAccounts(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.command_string = bot.get_command_str()
        self.hor_accounts = self.bot.backoffice.stellar_wallet.server.accounts()

    @commands.group(aliases=["account", "acc"])
    async def accounts(self, ctx):
        title = ':office_worker: __Horizon Accounts Queries__ :office_worker:'
        description = 'Representation of all available commands available to interact with ***Account*** Endpoint on ' \
                      'Stellar Horizon Server. Commands can be used 1/30 seconds/ per user.\n' \
                      '`Aliases: account,acc`'
        list_of_commands = [
            {"name": f':new: Create New Account :new: ',
             "value": f'```{self.command_string}accounts create```\n'
                      f'`aliases: new`'},
            {"name": f':mag_right: Query Account Details :mag:',
             "value": f'```{self.command_string}accounts get <Valid Stellar Address>```\n'
                      f'`aliases: details,query,find`'}
        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @accounts.command(aliases=['new'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def create(self, ctx):
        """
        Creates new in-active account on Stellar Network
        """
        try:
            details = self.bot.backoffice.stellar_wallet.create_stellar_account()
            if details:
                await account_create_msg(destination=ctx.message.author, details=details)
            else:
                message = f'New Stellar Account could not be created at this moment. Please try again later'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=CONST_ACCOUNT_ERROR)
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @accounts.command(aliases=["get", "query", "find"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def details(self, ctx, address: str):
        """
        Query details for specific public address
        """
        if check_stellar_address(address=address):
            try:
                data = self.hor_accounts.account_id(account_id=address).call()
                if data:
                    for coin in reversed(data["balances"]):
                        date_fm = format_date(data["last_modified_time"])
                        if not coin.get('asset_code'):
                            signers_data = ', '.join(
                                [f'`{sig["key"]}`' for sig in
                                 data["signers"]])

                            # Send info to user
                            await send_details_for_stellar(destination=ctx.message.author,
                                                           coin=coin,
                                                           data=data,
                                                           date=date_fm,
                                                           signers=signers_data)

                        else:
                            await send_details_for_asset(destination=ctx.message.author, coin=coin, data=data,
                                                         date=date_fm)

                else:
                    message = f'Account ```{address}``` could not be queried. Either does not exist or has not been ' \
                              f'activate yet. Please try again later or in later case, ' \
                              f'use [Stellar Laboratory](https://laboratory.stellar.org/#account-creator?network=test).' \
                              f'to activate your account with test Lumens.'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                         sys_msg_title=CONST_ACCOUNT_ERROR)
            except BadRequestError as e:
                extras = e.extras
                await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

            except NotFoundError:
                message = f'Account with address `{address}` could not be found/does not exist.'
                await horizon_error_msg(destination=ctx.message.author, error=message)

        else:
            message = f'Address `{address}` is not valid Stellar Address. Please recheck provided data and try again'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)


def setup(bot):
    bot.add_cog(HorizonAccounts(bot))
