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
                      ' link to access older transactions. All transactions are returned in descending order.'
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
    async def address(self, ctx, address: str):
        if check_stellar_address(address=address):
            data = self.backoffice.stellar_wallet.get_payments_account(address=address)

            payment_details = Embed(title=':mag_right: Payments for Stellar Account :mag_right: ',
                                    colour=Colour.lighter_gray())
            payment_details.add_field(name=':map: Account Address :map: ',
                                      value=f'```{data["account_id"]}```',
                                      inline=False)
            payment_details.add_field(name=f'Complete List of Payments',
                                      value=f'{data["_links"]["self"]}')
            await ctx.author.send(embed=payment_details)

            payments = data["_embedded"]["records"]

            for p in payments:
                if p['to'] == address:
                    c = Colour.green()
                else:
                    c = Colour.red()

                payment_info = Embed(title=f'Operation Details',
                                     colour=c)
                payment_info.set_author(name=f':id: {p["id"]}')
                payment_info.add_field(name=f'Operation Type',
                                       value=f'`{p["type"]}`')
                payment_info.add_field(name=f'Date and time',
                                       value=f'`{p["created_at"]}`')
                payment_info.add_field(name=f'Paging Token',
                                       value=f'{p["paging_token"]}',
                                       inline=False)
                payment_info.add_field(name='From',
                                       value=f'```{p["from"]}```',
                                       inline=False)
                payment_info.add_field(name='To',
                                       value=f'```{p["to"]}```',
                                       inline=False)
                payment_info.add_field(name=f'Transaction Hash',
                                       value=f'`{p["transaction_hash"]}`')
                payment_info.add_field(name=f'Explorer Link',
                                       value=f'{p["_links"]["transaction"]["href"]}')

                if not p.get('asset_code'):
                    payment_info.add_field(name='Amount',
                                           value=f'```{p["amount"]} XLM```',
                                           inline=False)

                else:
                    payment_info.add_field(name='Asset Issuer',
                                           value=f'```{p["asset_issuer"]}```',
                                           inline=False)
                    payment_info.add_field(name='Amount',
                                           value=f'```{p["amount"]} {p["asset_code"]}```',
                                           inline=False)

                await ctx.author.send(embed=payment_info)
        else:
            message = f'Address you have provided is not a valid Stellar Lumen Address. Please try again'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACCOUNT_ERROR)

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
