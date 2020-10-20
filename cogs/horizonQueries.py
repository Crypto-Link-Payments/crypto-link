"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.customCogChecks import has_wallet
from backOffice.stellarOnChainHandler import StellarWallet
from cogs.utils.systemMessaages import CustomMessages

from cogs.utils.securityChecks import check_stellar_address
from utils.tools import Helpers

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'
stellar_chain = StellarWallet()


class HorizonAccessCommands(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()

    @commands.group()
    @commands.check(has_wallet)
    async def horizon(self, ctx):
        """
        Entry point for horizon queries
        """

        title = ':sunrise: __Stellar Horizon Commands__ :sunrise: '
        description = 'Representation of all available commands available to interract with Stellar Horizon Network.'
        list_of_commands = [
            {"name": f':office_worker: Account commands :office_worker:',
             "value": f'`{self.command_string}horizon account`'},
            {"name": f':money_with_wings: Payments commands :money_with_wings:',
             "value": f'`{self.command_string}horizon payments`'}
        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands, description=description,
                                                destination=1, c=Colour.lighter_gray())

    @horizon.group(aliases=['acc'])
    async def account(self, ctx):
        title = ':office_worker: __Horizon Account Operations__ :office_worker:'
        description = 'Representation of all available commands available to interact with ***Account*** Endpoint on ' \
                      'Stellar Horizon Server'
        list_of_commands = [
            {"name": f':new: Create New Account :new: ',
             "value": f'`{self.command_string}horizon account create`'},
            {"name": f':mag_right:  Query Account Details :mag_right:  ',
             "value": f'`{self.command_string}horizon account create`'}
        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @account.command()
    async def create(self, ctx):
        """
        Creates new in-active account on Stellar Network
        """
        details = stellar_chain.create_stellar_account()
        if details:
            new_account = Embed(title=f':rocket: New Stellar Account Created :rocket:',
                                description=f'You have successfully created new account on {details["network"]} '
                                            f'network.',
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
                                        f' generate account nor can recover it. This message will self-destruct in '
                                        f' 360 seconds.',
                                  inline=False)
            await ctx.author.send(embed=new_account, delete_after=360)
        else:
            message = f'New Stellar Account could not be created at this moment. Please try again later.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)

    @account.command(aliases=["get"])
    async def details(self, ctx, address: str):
        """
        Query details for specific public address
        """

        if check_stellar_address(address=address):
            data = self.backoffice.stellar_wallet.get_account_details(address=address)

            for coin in reversed(data["balances"]):
                if not coin.get('asset_code'):
                    signers_data = ', '.join(
                        [f'`{sig["key"]}`' for sig in
                         data["signers"]])

                    acc_details = Embed(title=':mag_right: Details for Stellar Account :mag_right: ',
                                        description=f'Last Activity {data["last_modified_time"]}',
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
                                          value=f'{coin["balance"]} XLM',
                                          inline=False)
                    acc_details.add_field(name=f':man_judge: Liabilities :man_judge: ',
                                          value=f'Buying Liabilities: {coin["buying_liabilities"]}\n'
                                                f'Selling Liabilities: {coin["selling_liabilities"]}',
                                          inline=False)
                    await ctx.author.send(embed=acc_details)
                else:
                    asset_details = Embed(title=f':coin: Details for asset {coin["asset_code"]} :coin:',
                                          description=f'Last Activity on {data["last_modified_time"]}'
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
            message = f'Address you have provided is not a valid Stellar Lumen Address. Please try again'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)

    @account.group()
    async def payments(self, ctx):
        """
        End points for payments
        """
        title = ':money_with_wings:  __Horizon Payments Operations__ :money_with_wings: '
        description = 'Representation of all available commands available to interact with ***Payments*** Endpoint on ' \
                      'Stellar Horizon Server. All commands return last 3 transactions done on account, and explorer' \
                      ' link to access older transactions.'
        list_of_commands = [
            {"name": f':map: Get payments by public address :map: ',
             "value": f'`{self.command_string}horizon account payments address <address>`'},
            {"name": f':ledger:  Get payments based on ledger sequence :ledger:   ',
             "value": f'`{self.command_string}horizon account payments ledger <ledger sequence>``'},
            {"name": f':hash:  Get payments based on transaction hash :hash:',
             "value": f'`{self.command_string}horizon account payments transaction <hash of transaction>``'}
        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands, description=description,
                                                destination=1, c=Colour.lighter_gray())

    @payments.command()
    async def address(self, address: str, limit: int = None, pagging_token: int = None):
        """
        {'_embedded': {'records': [{'_links': {'effects': {'href': 'https://horizon-testnet.stellar.org/operations/5592159088562177/effects'},
                                   'precedes': {'href': 'https://horizon-testnet.stellar.org/effects?order=asc&cursor=5592159088562177'},
                                   'self': {'href': 'https://horizon-testnet.stellar.org/operations/5592159088562177'},
                                   'succeeds': {'href': 'https://horizon-testnet.stellar.org/effects?order=desc&cursor=5592159088562177'},
                                   'transaction': {'href': 'https://horizon-testnet.stellar.org/transactions/e903c3191252d87996563cd7e16f2abffda20a15945b84e9b27e783ce15b8da2'}},
                        'amount': '100.0000000',
                        'asset_code': 'CLT',
                        'asset_issuer': 'GAFYI3RFYQHCEUI73OOY5AO7CIODZ4ZEXON72THANN5M3L5CUNK24E3G',
                        'asset_type': 'credit_alphanum4',
                        'created_at': '2020-10-19T12:31:22Z',
                        'from': 'GAGJZJPP27DJ6M5T2UVZAMP3CLIZKXDCOXU7UNYWZBAX4XXR5J5DLDZO',
                        'id': '5592159088562177',
                        'paging_token': '5592159088562177',
                        'source_account': 'GAGJZJPP27DJ6M5T2UVZAMP3CLIZKXDCOXU7UNYWZBAX4XXR5J5DLDZO',
                        'to': 'GBAGTMSNZLAJJWTBAJM2EVN5BQO7YTQLYCMQWRZT2JLKKXP3OMQ36IK7',
                        'transaction_hash': 'e903c3191252d87996563cd7e16f2abffda20a15945b84e9b27e783ce15b8da2',
                        'transaction_successful': True,
                        'type': 'payment',
                        'type_i': 1}]},
'_links': {'next': {'href': 'https://horizon-testnet.stellar.org/accounts/GAGJZJPP27DJ6M5T2UVZAMP3CLIZKXDCOXU7UNYWZBAX4XXR5J5DLDZO/payments?cursor=5592159088562177&include_failed=false&limit=1&order=desc'},
        'prev': {'href': 'https://horizon-testnet.stellar.org/accounts/GAGJZJPP27DJ6M5T2UVZAMP3CLIZKXDCOXU7UNYWZBAX4XXR5J5DLDZO/payments?cursor=5592159088562177&include_failed=false&limit=1&order=asc'},
        'self': {'href': 'https://horizon-testnet.stellar.org/accounts/GAGJZJPP27DJ6M5T2UVZAMP3CLIZKXDCOXU7UNYWZBAX4XXR5J5DLDZO/payments?cursor=&include_failed=false&limit=1&order=desc'}}}
        """

        pass

    @payments.command()
    async def ledger(self, address: str, ledger: int):
        pass

    @payments.command()
    async def transaction(self, address: str, limit: int = None, transaction_hash: int = None):
        pass

    @horizon.error
    async def asset_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'In order to user Stellar Expert Commands you need to have wallet registered in the system!. Use' \
                      f' `{self.command_string}register`'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)


def setup(bot):
    bot.add_cog(HorizonAccessCommands(bot))
