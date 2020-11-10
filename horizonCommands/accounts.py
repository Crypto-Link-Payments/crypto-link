"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from horizonCommands.utils.horizon import server
from datetime import datetime
from cogs.utils.securityChecks import check_stellar_address
from utils.tools import Helpers
from horizonCommands.utils.customMessages import account_create_msg, send_details_for_stellar, send_details_for_asset
from backOffice.backOffice import BackOffice

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'


class HorizonAccounts(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.server = server
        self.hor_accounts = self.server.accounts()
        self.backoffice = bot.backoffice

    @commands.group()
    async def accounts(self, ctx):
        title = ':office_worker: __Horizon Accounts Queries__ :office_worker:'
        description = 'Representation of all available commands available to interact with ***Account*** Endpoint on ' \
                      'Stellar Horizon Server'
        list_of_commands = [
            {"name": f':new: Create New Account :new: ',
             "value": f'`{self.command_string}accounts create`'},
            {"name": f':mag_right: Query Account Details :mag:',
             "value": f'`{self.command_string}accounts get <Valid Stellar Address>`'}
        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @accounts.command()
    async def create(self, ctx):
        """
        Creates new in-active account on Stellar Network
        """
        # TODO fix wording before release
        details = self.backoffice.stellar_wallet.create_stellar_account()
        if details:
            await account_create_msg(destination=ctx.message.author, details=details)
        else:
            message = f'New Stellar Account could not be created. Please try again later'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)

    @accounts.command(aliases=["get", "query"])
    async def details(self, ctx, address: str):
        """
        Query details for specific public address
        """
        if check_stellar_address(address=address):
            data = self.hor_accounts.account_id(account_id=address).call()
            if data:
                for coin in reversed(data["balances"]):
                    dt_format = datetime.strptime(data["last_modified_time"], '%Y-%m-%dT%H:%M:%SZ')
                    if not coin.get('asset_code'):
                        signers_data = ', '.join(
                            [f'`{sig["key"]}`' for sig in
                             data["signers"]])

                        # Send info to user
                        await send_details_for_stellar(destination=ctx.message.author,
                                                       coin=coin,
                                                       data=data,
                                                       date=dt_format,
                                                       signers=signers_data)

                    else:
                        await send_details_for_asset(destination=ctx.message.author, coin=coin, data=data,
                                                     date=dt_format)

            else:
                message = f'Account ```{address}``` could not be queried. Either does not exist or has not been ' \
                          f'activate yet. Please try again later or in later case, ' \
                          f'use [Stellar Laboratory](https://laboratory.stellar.org/#account-creator?network=test).' \
                          f'to activate your account with test Lumens.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=CONST_ACCOUNT_ERROR)

        else:
            message = f'Address you have provided is not a valid Stellar Lumen Address. Please try again'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)

    @accounts.error
    async def asset_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to user Stellar Expert Commands you need to have wallet registered in the system!. Use' \
                      f' `{self.command_string}register`'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)


def setup(bot):
    bot.add_cog(HorizonAccounts(bot))
