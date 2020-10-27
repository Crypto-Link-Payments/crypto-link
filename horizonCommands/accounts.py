"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from horizonCommands.horizonAccess.horizon import server
from datetime import datetime
from cogs.utils.securityChecks import check_stellar_address
from utils.tools import Helpers
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
        details = self.backoffice.stellar_wallet.create_stellar_account()
        if details:
            new_account = Embed(title=f':new: Stellar Testnet Account Created :new:',
                                description=f'You have successfully created new account on {details["network"]}. Do'
                                            f' not deposit real XLM as this account has been created on testnet. '
                                            f'Head to [Stellar Laboratory](https://laboratory.stellar.org/#account-creator?network=test)'
                                            f' and use Friend bot to activate account',
                                colour=Colour.lighter_gray()
                                )
            new_account.add_field(name=f':map: Public Address :map: ',
                                  value=f'```{details["address"]}```',
                                  inline=False)
            new_account.add_field(name=f':key: Secret :key: ',
                                  value=f'```{details["secret"]}```',
                                  inline=False)
            new_account.add_field(name=f':warning: Important Message:warning:',
                                  value=f'Please store/backup account details somewhere safe and delete this embed on'
                                        f' Discord. Exposure of Secret to any other entity or 3rd party application'
                                        f'might result in loss of funds. Crypto Link does not store details of newly'
                                        f' generate accounts nor can recover it.',
                                  inline=False)
            await ctx.author.send(embed=new_account, delete_after=360)
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

                        acc_details = Embed(title=':mag_right: Details for Stellar Account :mag:',
                                            description=f'Last Activity {dt_format} (UTC)',
                                            colour=Colour.lighter_gray())
                        acc_details.add_field(name=':map: Account Address :map: ',
                                              value=f'```{data["account_id"]}```',
                                              inline=False)
                        acc_details.add_field(name=':pen_fountain: Account Signers :pen_fountain: ',
                                              value=signers_data,
                                              inline=False)
                        acc_details.add_field(name=' :genie: Sponsorship Activity :genie:',
                                              value=f':money_mouth: {data["num_sponsored"]} (sponsored)\n'
                                                    f':money_with_wings: {data["num_sponsoring"]} (sponsoring) ',
                                              inline=False)
                        acc_details.add_field(name=f' :moneybag: Balance :moneybag:',
                                              value=f'`{coin["balance"]} XLM`',
                                              inline=False)
                        acc_details.add_field(name=f':man_judge: Liabilities :man_judge: ',
                                              value=f'Buying Liabilities: {coin["buying_liabilities"]}\n'
                                                    f'Selling Liabilities: {coin["selling_liabilities"]}',
                                              inline=False)
                        acc_details.add_field(name=f':triangular_flag_on_post: Flags :triangular_flag_on_post:',
                                              value=f'Auth Required: {data["flags"]["auth_required"]}\n'
                                                    f'Auth Revocable: {data["flags"]["auth_revocable"]}\n'
                                                    f'Auth Immutable:{data["flags"]["auth_immutable"]}')
                        await ctx.author.send(embed=acc_details)
                    else:
                        asset_details = Embed(title=f':coin: Details for asset {coin["asset_code"]} :coin:',
                                              description=f'Last Activity on {dt_format} (UTC)'
                                                          f' (Ledger:{data["last_modified_ledger"]}',
                                              colour=Colour.lighter_gray())
                        asset_details.add_field(name=f':map: Issuer Address :map: ',
                                                value=f'```{coin["asset_issuer"]}```',
                                                inline=False)
                        asset_details.add_field(name=f' :moneybag: Balance :moneybag:',
                                                value=f'`{coin["balance"]} {coin["asset_code"]}`',
                                                inline=False)
                        asset_details.add_field(name=f':handshake: Trustline Status :handshake: ',
                                                value=f'Authorizer: {coin["is_authorized"]}\n'
                                                      f'Maintain Liabilities: {coin["is_authorized_to_maintain_liabilities"]}',
                                                inline=False)
                        asset_details.add_field(name=f':man_judge: Liabilities :man_judge: ',
                                                value=f'Buying Liabilities: {coin["buying_liabilities"]}\n'
                                                      f'Selling Liabilities: {coin["selling_liabilities"]}',
                                                inline=False)
                        asset_details.add_field(name=':chains: Trustline links :chains: ',
                                                value=f'[Issuer Details](https://stellar.expert/explorer/testnet/account/{coin["asset_issuer"]}?order=desc)\n'
                                                      f'[Asset Details](https://stellar.expert/explorer/testnet/asset/{coin["asset_code"]}-{coin["asset_issuer"]}?order=desc)')
                        await ctx.author.send(embed=asset_details)

            else:
                message = f'Account ```{address}``` could not be queried. Either does not exist or has not been activate ' \
                          f'yet. Please try again later or in later case, ' \
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
