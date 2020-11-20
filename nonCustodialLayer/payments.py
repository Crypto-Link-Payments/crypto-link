"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour, Member
from cogs.utils.systemMessaages import CustomMessages
from cogs.utils.securityChecks import check_stellar_address
from utils.tools import Helpers
from stellar_sdk import TransactionBuilder, Network, Server, Account, TransactionEnvelope, Transaction
from stellar_sdk.exceptions import NotFoundError

helper = Helpers()
integrated_coins = helper.read_json_file(file_name='integratedCoins.json')
custom_messages = CustomMessages()
helper = Helpers()
CONST_XDR_ERROR = ":exclamation: XDR Creation Error :exclamation: "


def check(author):
    def inner_check(message):
        """
        Check for answering the verification message on withdrawal. Author origin
        """
        if message.author.id == author.id:
            return True
        else:
            return False

    return inner_check


class Layer3AccountCommands(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.server = Server(horizon_url="https://horizon-testnet.stellar.org")
        self.supported = list(integrated_coins.keys())

    def check_address_on_server(self, address: str):
        try:
            from_account = self.server.load_account(account_id=address)
            return True
        except NotFoundError:
            return False

    async def send_xdr_info(self, ctx, request_data: dict, command_type: str):

        # Inform user
        xdr_info = Embed(title=f'Transaction as XDR',
                         description='Bellow is the XDR envelope of payment with provided details',
                         colour=Colour.magenta())
        if command_type == 'public':
            xdr_info.add_field(name="From Address",
                               value=f'```{request_data["fromAddr"]}```',
                               inline=False)
            xdr_info.add_field(name="To Address",
                               value=f'```{request_data["toAddr"]}```',
                               inline=False)
            xdr_info.add_field(name="Token and Amount",
                               value=f'{request_data["amount"]} {request_data["token"]}',
                               inline=False)

            if request_data["token"] != 'xlm':
                xdr_info.add_field(name="Asset Issuer",
                                   value=f'`{request_data["assetIssuer"]}`',
                                   inline=False)
        elif command_type == "discord":
            pass

        elif command_type == "activate":
            xdr_info.add_field(name="From Address",
                               value=f'```{request_data["fromAddr"]}```',
                               inline=False)
            xdr_info.add_field(name="Address to be activated",
                               value=f'```{request_data["toAddr"]}```',
                               inline=False)
            xdr_info.add_field(name="Total Amount to be sent",
                               value=f'`{request_data["amount"]} XLM`',
                               inline=False)

        xdr_info.add_field(name="XDR Envelope",
                           value=f'```{request_data["envelope"]}```',
                           inline=False)

        xdr_info.add_field(name=":warning: Note :warning:",
                           value=f'Copy the XDR envelope to application which allows __importing of '
                                 f' a transaction envelope in XDR format and follow procedures there.'
                                 f'If you do not have access to such application than you can use as well\n'
                                 f'[Stellar Laboratory Transaction Signer](https://laboratory.stellar.org/#txsigner?network=test)',
                           inline=False)

        await ctx.author.send(embed=xdr_info)

    @commands.group(aliases=['hot_wallet'])
    async def xdr(self, ctx):
        title = ':regional_indicator_x: :regional_indicator_d: :regional_indicator_r:  ' \
                '__Transaction Envelope Creator__ ' \
                ':regional_indicator_x: :regional_indicator_d: :regional_indicator_r: '
        description = 'Representation of all currently available commands to create and sign Transaction envelopes.'
        list_of_commands = [
            {"name": f':map: Prepare Payment Envelope for external address :map:',
             "value": f'`{self.command_string}xdr payment <amount> <token> <from address> <to address> <memo=optional>`'},
            {"name": f':mag_right: Prepare Payment for Discord User :mag:',
             "value": f'`{self.command_string}xdr discord <<amount> <token> <@discord.User>`'},
            {"name": f':pen_ballpoint: Sign Transaction XDR :pen_ballpoint: ',
             "value": f'`{self.command_string}xdr sign <Transaction XDR String>`'},
            {"name": f':arrow_forward: Activate Address XDR :arrow_forward:',
             "value": f'`{self.command_string}xdr activate <from address> <to address> <@discord.User>`\n'
                      f'**__Note:__** This command is allowed to be executed only through the public channels of '
                      f'community as it requires access to the User Tag '}

        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @xdr.command()
    async def payment(self, ctx, amount: float, token: str, from_address: str, to_address: str, memo: str = None):
        """
        Create XDR payment envelope to be used for signing to some other users than discord
        """
        amount_in_stroops = int(amount * (10 ** 7))
        final_amount = float(amount_in_stroops / (10 ** 7))
        asset_issuer = None

        if final_amount > 0.0000001:

            # Check If address exists on network
            from_status = self.check_address_on_server(address=from_address)
            to_status = self.check_address_on_server(address=to_address)

            if to_status and from_status:

                # Filter token for issuer or not
                if token != 'xlm':
                    if token not in self.supported:
                        # Ask for Asset Issuer
                        message_content = f"Asset Issuer for token {token.upper()} has not been found " \
                                          f"in Crypto Link System. Please provide Asset Issuer address"
                        issuer_request = Embed(title=f'Asset Issuer Details Request',
                                               description=message_content,
                                               colour=Colour.purple())
                        await ctx.author.send(embed=issuer_request)
                        asset_issuer_addr = await self.bot.wait_for('message', check=check(ctx.message.author))
                        print(f'User wrote {asset_issuer_addr}')

                        if check_stellar_address(address=asset_issuer_addr):
                            if self.check_address_on_server(address=asset_issuer_addr):
                                asset_issuer = asset_issuer_addr
                            else:
                                message = "Address of Asset Issuer could not be found through Horizon"
                                await custom_messages.system_message(ctx=ctx, message=message, color_code=1,
                                                                     destination=ctx.author,
                                                                     sys_msg_title=CONST_XDR_ERROR)
                                asset_issuer = False
                        else:
                            message = "You have provided a invalid Ed25519 Public Key for Asset Issuer "
                            await custom_messages.system_message(ctx=ctx, message=message, color_code=1,
                                                                 destination=ctx.author,
                                                                 sys_msg_title=CONST_XDR_ERROR)
                            asset_issuer = False
                    else:
                        asset_issuer = integrated_coins[token.lower()]["assetIssuer"]

                # If Asset Issuer is not False
                if not type(asset_issuer) is bool:  # If it is not boolean than proceed else throw  Disc error
                    loaded_from_account = self.server.load_account(account_id=from_address)
                    tx = TransactionBuilder(
                        source_account=loaded_from_account,
                        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                        base_fee=self.server.fetch_base_fee()).append_payment_op(
                        asset_issuer=asset_issuer,
                        destination=to_address, asset_code=token.upper(), amount=str(final_amount))

                    if memo:
                        tx.add_text_memo(memo_text=memo)

                    # Build and convert to xdr to be sent to user on discord
                    xdr_envelope = tx.set_timeout(360).build().to_xdr()

                    request_data = {
                        "fromAddr": from_address,
                        "toAddr": to_address,
                        "token": token.upper(),
                        "amount": final_amount,
                        "assetIssuer": asset_issuer,
                        "envelope": xdr_envelope

                    }
                    await self.send_xdr_info(ctx=ctx, request_data=request_data, command_type='public')

                else:
                    pass

            else:
                message = 'One of provided addresses does not exist or has not been activate yet:\n' \
                          f'From Address: {from_status}\n' \
                          f'To Address: {to_address}'
                await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=ctx.author,
                                                     sys_msg_title=CONST_XDR_ERROR)
        else:
            message = f'Amount of {token.upper()} must be greater than 0.0000001. '
            await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=ctx.author,
                                                 sys_msg_title=CONST_XDR_ERROR)

    @xdr.command()
    async def discord(self, ctx, amount: float, token: str, user: Member, layer: int):
        """
        Create XDR to send to user on discord
        """
        amount_in_stroops = int(amount * (10 ** 7))
        final_amount = float(amount_in_stroops / (10 ** 7))

        if final_amount >= 0.0000001:
            # Check if user has registered Account in system
            if self.backoffice.account_mng.check_user_existence(user_id=user.id):

                # TODO Check if user has 2 layer activated
                pass



            else:
                message = "User Has not been registered yet into Crypto Link System. If you would still like to send " \
                          f"user {final_amount} {token.upper()}, please contact him directly and ask him for hot wallet" \
                          f" address."
                await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=ctx.author,
                                                     sys_msg_title=CONST_XDR_ERROR)

        else:
            message = f'Amount of {token.upper()} must be greater than 0.0000001. '
            await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=ctx.author,
                                                 sys_msg_title=CONST_XDR_ERROR)

    @xdr.command()
    async def dev(self, ctx, xdr_envelope):
        """
        Modifies the transaction envelope so that another operation is getting added
        """
        pass

    @xdr.command()
    async def sign(self, ctx, xdr_envelope):
        """
        Sign XDR envelope
        """
        tx = Transaction.from_xdr(xdr=xdr_envelope)
        if isinstance(tx, Transaction):
            print(Transaction.__dict__)
        else:
            print('Not a transaction')

    @xdr.command()
    async def activate(self, ctx, from_account: str, account_to_activate: str, amount: float = None):
        """
        Make account activate
        """
        if self.check_address_on_server(address=from_account):
            source_account = self.server.load_account(account_id=from_account)
            tx = TransactionBuilder(
                source_account=source_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=self.server.fetch_base_fee()) \
                .append_create_account_op(destination="1.0", starting_balance="12.25")

            final_amount = str()
            if amount:
                amount_in_stroops = int(amount * (10 ** 7))
                final_amount = str(float(amount_in_stroops / (10 ** 7)))
                tx.append_payment_op(destination=account_to_activate, amount=final_amount, asset_code='XLM')
            else:

                total_amount_tx = 1.0 + final_amount
                xdr_envelope = tx.build().to_xdr()

            requested_data = {
                "fromAddr": from_account,
                "toAddr": account_to_activate,
                "amount": total_amount_tx,
                "envelope": xdr_envelope
            }
            await self.send_xdr_info(ctx=ctx, request_data=requested_data)

        else:
            print('From account address does not exist on the network')


def setup(bot):
    bot.add_cog(Layer3AccountCommands(bot))
