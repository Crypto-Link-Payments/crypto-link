"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

import re
import asyncio
from discord.ext import commands
from discord import Colour, Member, Embed
from cogs.utils.systemMessaages import CustomMessages
from cogs.utils.customCogChecks import user_has_third_level, user_has_no_third_level, user_has_second_level
from cogs.utils.securityChecks import check_stellar_address
from utils.customMessages import user_account_info, dev_fee_option_notification, ask_for_dev_fee_amount

from utils.tools import Helpers
from stellar_sdk import TransactionBuilder, Network, Account, TransactionEnvelope, Asset, Payment, \
    parse_transaction_envelope_from_xdr, Keypair
from stellar_sdk.exceptions import NotFoundError, Ed25519PublicKeyInvalidError, Ed25519SecretSeedInvalidError, \
    BadRequestError, BadResponseError, ConnectionError
from thirdLevel.utils.thirdLevelCustMsg import third_level_acc_details, new_acc_details, \
    third_level_account_reg_info, third_level_own_reg_info, send_xdr_info, xdr_data_to_embed, user_approval_request, \
    transaction_result, server_error_response

helper = Helpers()
integrated_coins = helper.read_json_file(file_name='integratedCoins.json')
custom_messages = CustomMessages()
helper = Helpers()
CONST_XDR_ERROR = ":exclamation: XDR Creation Error :exclamation: "
CONST_REG_ERROR_TITLE = "3. level wallet registration error"
CONST_REG_ERROR = "Account could not be registered into Crypto Link system. Please try again later."
CONST_DEV_ACTIVATED = True
CONST_DEV_FEE = '0.0010000'


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


class LevelThreeAccountCommands(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.server = self.backoffice.stellar_wallet.server
        self.acc_mng_rd_lvl = self.backoffice.third_level_manager
        self.supported = list(integrated_coins.keys())
        self.available_levels = [1, 2, 3]

    @staticmethod
    async def show_typing(ctx):
        """
        Shows typing on Discord so user knows that something is happening in the background
        """
        async with ctx.author.typing():
            await asyncio.sleep(5)

    async def uplink_notification(self, message: str):
        """
        Dispatch informational embeds to sender and Crypto Link Upling
        """
        # Send notification on transaciton to Crypto Link Uplink
        load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                         self.backoffice.guild_profiles.get_all_explorer_applied_channels()]
        for dest in load_channels:
            await dest.send(content=message)

    def check_user_wallet_layer_level(self, layer, user_id):
        """
        Check if user has registered account under selected wallet level
        """
        if layer == 1:
            return self.backoffice.account_mng.check_user_existence(user_id=user_id)
        elif layer == 2:
            return self.backoffice.second_level_manager.second_level_user_reg_status(user_id=user_id)
        elif layer == 3:
            return self.backoffice.third_level_manager.third_level_user_reg_status(user_id=user_id)

    def get_recipient_details_based_on_layer(self, layer: int, user_id: int):
        """
        Produce destination from the database
        """
        if layer == 1:
            # Details for transaction to level 1 wallet
            user_data = {
                "address": self.backoffice.stellar_wallet.public_key,
                "memo": self.backoffice.account_mng.get_user_memo(user_id=user_id)["stellarDepositId"]
            }
            return user_data
        elif layer == 2:
            # Details for transaction to level 2 wallet

            user_data = {
                "address": self.backoffice.second_level_manager.get_custodial_hot_wallet_addr(user_id=user_id),
                "memo": self.backoffice.account_mng.get_user_memo(user_id=user_id)["stellarDepositId"]
            }
            return user_data

        elif layer == 3:
            user_data = {
                "address": self.acc_mng_rd_lvl.get_third_hot_wallet_addr(user_id=int(user_id)),
                "memo": None
            }
            return user_data

    def check_if_acc_is_live(self, address: str):
        try:
            self.server.load_account(account_id=address)
            return True
        except NotFoundError:
            return False
        except Ed25519PublicKeyInvalidError:
            return False

    def public_addr_struct_check(self, public_address: str):
        """
        Check the public key address
        """
        try:
            Account(account_id=public_address, sequence=0)
            return True
        except Ed25519PublicKeyInvalidError:
            return False

    def check_private_key(self, private_key: str):
        """
        Check if private key constructed matches criteria
        """
        try:
            Keypair.from_secret(private_key)
            return True
        except Ed25519SecretSeedInvalidError:
            return False

    def process_operations(self, operations: list):
        """
        Process operations from XDR envelope to make it human readable dict
        """
        process_op = [
        ]
        for op in operations:
            if isinstance(op, Payment):
                destination = op.destination
                amount = op.amount
                asset = op.asset
                if isinstance(asset, Asset):
                    code = asset.code
                    issuer = asset.issuer
                    asset_type = asset.type
                payment = {
                    "type": "payment",
                    "to": destination,
                    "amount": amount,
                    "code": code,
                    "issuer": issuer,
                    "assetType": asset_type,

                }
                process_op.append(payment)
        return process_op

    def produce_envelope(self, tx_data: dict, dev_fee_status: bool):
        """
        Returns Transaction as envelope
        """
        source_account = self.server.load_account(tx_data["fromAddr"])
        tx_build = TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=self.server.fetch_base_fee()

        ).append_payment_op(
            destination=tx_data["toAddr"],
            asset_code="XLM",
            amount=tx_data["netValue"]).add_text_memo(memo_text=tx_data["memo"])

        # Append Dev fee if selected
        if dev_fee_status:
            p = Payment(destination=self.backoffice.stellar_wallet.dev_key, asset=Asset.native(),
                        amount=tx_data["devFee"])
            tx_build.append_operation(operation=p)

        envelope = tx_build.set_timeout(240).build()
        return envelope.to_xdr()

    def stream_transaction_from_envelope(self, xdr_string: str, private_key: str):
        envelope = TransactionEnvelope.from_xdr(xdr_string, network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE)
        envelope.sign(signer=private_key)

        try:
            result = self.server.submit_transaction(envelope)
            result.pop("envelope_xdr")
            result.pop("fee_meta_xdr")
            result.pop("result_meta_xdr")
            return True, result
        except NotFoundError as e:
            return False, e
        except BadRequestError as e:
            return False, e
        except BadResponseError as e:
            return False, e
        except ConnectionError as e:
            return False, e

    @commands.group(aliases=['3', 'rd'])
    @commands.check(user_has_second_level)
    async def three(self, ctx):
        """
        3rd level account entry point
        """
        if ctx.invoked_subcommand is None:
            title = ':regional_indicator_x: :regional_indicator_d: :regional_indicator_r:  ' \
                    '__Welcome to level 3 wallet system__ ' \
                    ':regional_indicator_x: :regional_indicator_d: :regional_indicator_r: '
            description = "***Level 3*** wallet provides user full control of the private keys. Unlike in __Level 2__," \
                          " Crypto Link stores upon registration only Discord Username details and " \
                          "public wallet key address. Both are required to make wallet levels interoperable and allows " \
                          " for execution of the transactions with ease."
            list_of_commands = [
                {"name": f':new: Register/Update 3 level wallet :new:',
                 "value": f'```{self.command_string}3 register```\n'
                          f'`Aliases: get, n, reg, r `'},
                {"name": f':cowboy: Account Information :cowboy:  ',
                 "value": f'```{self.command_string}3 account```\n'
                          f'`Aliases: wallet, acc, a, w`'},
                {"name": f':incoming_envelope:  Prepare Payments/Transactions :incoming_envelope: ',
                 "value": f'```{self.command_string}3 payment```\n'
                          f'`Aliases: tx, t, p, transaction, pay`'},
                {
                    "name": f':regional_indicator_x: :regional_indicator_d: :regional_indicator_r:'
                            f' view and sign transaction'
                            f' :regional_indicator_x: :regional_indicator_d: :regional_indicator_r: ',
                    "value": f'```{self.command_string}3 xdr```\n'
                             f'`Aliases: envelope, env`'}

            ]

            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @three.group(aliases=['reg', 'r', 'get', 'n'])
    async def register(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':new: 3 level wallet registration commands :new: '
            description = ""
            list_of_commands = [
                {"name": f':mag_right: Register new in-active wallet level 3 :mag:',
                 "value": f'```{self.command_string}3 register new ```\n'
                          f'`Aliases: n`'},

                {"name": f':mag_right: Register Own Public Address :mag:',
                 "value": f'```{self.command_string}3 register own <Valid Public Address>```\n'
                          f'`Aliases: o, my`'},

                {"name": f':mag_right: Update Own Public Address :mag:',
                 "value": f'```{self.command_string}3 register update <Valid Public Address> ```\n'
                          f'`Aliases: u`'}
            ]
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @register.command(aliases=["n"])
    @commands.check(user_has_no_third_level)
    async def new(self, ctx):
        """
        Registers new 3rd level wallet in the system
        """

        # Send welcome message
        await third_level_account_reg_info(destination=ctx.author)

        # Prompt for response
        await ctx.author.send(content=f'{ctx.author.mention} Would you like to proceed (yes/no)')
        # Wait for answer 180 seconds
        welcome_verification = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=180)
        # Verify user answer
        if welcome_verification.content.upper() in ["YES", "Y"]:
            # Get details on new in-active account
            details = self.backoffice.stellar_wallet.create_stellar_account()
            if details:
                # Send details of new in-active account
                await third_level_acc_details(destination=ctx.author, details=details)

                await ctx.author.send(content='When you have safely stored account details, please answer with '
                                              '***done***. You have 120 seconds to respond otherwise, you will'
                                              'need to register again')
                # Wait for answer
                done_answer = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=180)

                if done_answer.content.upper() in ["DONE"]:
                    # Wallet details to store
                    details = {
                        "userId": int(ctx.message.author.id),
                        "publicAddress": details["address"]
                    }
                    if self.acc_mng_rd_lvl.register_rd_level_wallet(data_to_store=details):
                        await new_acc_details(author=ctx.author, details=details)
                        msg = ':new: User register wallet level 3. :rocket: '
                        await self.uplink_notification(message=msg)
                    else:
                        await custom_messages.system_message(ctx=ctx, message=CONST_REG_ERROR, color_code=1,
                                                             destination=0,
                                                             sys_msg_title=CONST_REG_ERROR_TITLE)

                else:
                    message = "Registration process has been cancelled."
                    await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=0,
                                                         sys_msg_title=CONST_REG_ERROR_TITLE)
            else:
                message = "Account could not be created. Please try again later. If issue persists. Please contact" \
                          " Crypto Link team."
                await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=0,
                                                     sys_msg_title=CONST_REG_ERROR_TITLE)
        else:
            message = "You have cancelled the registration process for level 3 wallet."
            await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=0,
                                                 sys_msg_title=CONST_REG_ERROR_TITLE)

    @register.command(aliases=["o", "my"])
    @commands.check(user_has_no_third_level)
    async def own(self, ctx, public_address: str):
        # Check if correct address provided
        if check_stellar_address(address=public_address):

            if public_address not in [self.bot.backoffice.stellar_wallet.public_key,
                                      self.bot.backoffice.stellar_wallet.dev_key]:
                await third_level_own_reg_info(destination=ctx.author)

                # Prompt for response
                await ctx.author.send(content=f'Are you sure you would like to register `{public_address}`'
                                              f' into the system? (yes/y, no/n)')
                # Wait for answer 180 seconds
                welcome_verification = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=60)
                # Verify user answer
                if welcome_verification.content.upper() in ["YES", "Y"]:
                    details = {
                        "userId": int(ctx.message.author.id),
                        "publicAddress": str(public_address)
                    }

                    if self.acc_mng_rd_lvl.register_rd_level_wallet(data_to_store=details):
                        await new_acc_details(author=ctx.author, details=details)
                        msg = ':new: User register wallet level 3. :rocket: '
                        await self.uplink_notification(message=msg)
                    else:
                        await custom_messages.system_message(ctx=ctx, message=CONST_REG_ERROR, color_code=1,
                                                             destination=0,
                                                             sys_msg_title=CONST_REG_ERROR_TITLE)

                else:
                    message = "You have cancelled the registration process for level 3 wallet."
                    await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=0,
                                                         sys_msg_title=CONST_REG_ERROR_TITLE)
            else:
                message = f"Wallet address `{public_address}` is owned by Crypto Link and can not be used as your " \
                          f"personal wallet."
                await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=0,
                                                     sys_msg_title=CONST_REG_ERROR_TITLE)
        else:
            title = "Public address Error"
            message = f"Address `{public_address}` is not a valid Stellar Public Address. Please check provided " \
                      f"details again"
            await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=0,
                                                 sys_msg_title=title)

    @register.command(aliases=["u"])
    @commands.check(user_has_third_level)
    async def update(self, ctx, public_address: str):
        if check_stellar_address(address=public_address):
            if public_address not in [self.bot.backoffice.stellar_wallet.public_key,
                                      self.bot.backoffice.stellar_wallet.dev_key]:
                await ctx.author.send(f'Are you sure you would like update your 3rd level wallet address to '
                                      f'{public_address}? yes/y or no/n')

                verification = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=60)
                if verification.content.upper() in ["YES", "Y"]:
                    details = {
                        "userId": int(ctx.message.author.id),
                        "publicAddress": str(public_address)
                    }

                    if self.acc_mng_rd_lvl.update_public_address(user_id=ctx.author.id, pub_address=public_address):
                        await new_acc_details(author=ctx.author, details=details)
                    else:
                        await custom_messages.system_message(ctx=ctx, message=CONST_REG_ERROR, color_code=1,
                                                             destination=0,
                                                             sys_msg_title=CONST_REG_ERROR_TITLE)
                else:
                    title = f':exclamation: __Address Update Cancelled__ :exclamation: '
                    message = f'You have canceled level 3 wallet address update.'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                         sys_msg_title=title)
            else:
                message = f"Wallet address `{public_address}` is owned by Crypto Link and can not be used as your " \
                          f"personal wallet."
                await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=0,
                                                     sys_msg_title=CONST_REG_ERROR_TITLE)
        else:
            title = f':exclamation: __Wrong Public Address__ :exclamation: '
            message = f'Address `{public_address}` is not a valid Stellar Public Address'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @three.group(aliases=["acc", "a", "wallet", "w"])
    @commands.check(user_has_third_level)
    async def account(self, ctx):
        """
        Entry point for account sub-commands
        """
        if ctx.invoked_subcommand is None:
            title = ':regional_indicator_x: :regional_indicator_d: :regional_indicator_r:  ' \
                    '__Welcome to level 3 wallet system__ ' \
                    ':regional_indicator_x: :regional_indicator_d: :regional_indicator_r: '
            description = "All commands available to operate with wallet level 3.\n" \
                          "`Aliases: acc, a"
            list_of_commands = [
                {"name": f':information_source: Account Status :information_source: ',
                 "value": f'```{self.command_string}3 account info```\n'
                          f'`Aliases: n, nfo`'},
                {"name": f':octagonal_sign: Remove account from Crypto Link :octagonal_sign:  ',
                 "value": f'```{self.command_string}3 account remove```\n'
                          f'`Aliases: delete, r`'},
            ]

            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @account.command(aliases=["delete", "r"])
    async def remove(self, ctx):
        removal_info = Embed(title=f':octagonal_sign:  Account Removal Process :octagonal_sign:  ',
                             description="You have initiated account removal procedure from the Crypto Link System",
                             color=Colour.orange())
        removal_info.add_field(name=":warning: Read Carefully :warning: ",
                               value="Wallet address registered under the wallet level 3 will be removed from Crypto "
                                     "Link system however can be still accessible through other applications as you"
                                     " hold private keys. In order to re-register same public address please use"
                                     f" `{self.command_string}3 register own`")
        await ctx.author.send(embed=removal_info)

        await ctx.author.send(f'Are you sure you would like to delete wallet from 3rd level wallets? yes/y or no/n')

        verification = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=60)

        if verification.content.upper() in ["YES", "Y"]:
            if self.acc_mng_rd_lvl.remove_account(user_id=ctx.author.id):
                sys_msg_title = 'Wallet level 3 removed from system'
                message = 'You have successfully removed wallet from the Crypto Link system.'
                await custom_messages.system_message(ctx=ctx, color_code=Colour.green(), message=message, destination=0,
                                                     sys_msg_title=sys_msg_title)
            else:
                sys_msg_title = 'Wallet removal issue'
                message = 'Wallet could not be removed from the system. Please try again later or contact Crypto ' \
                          'Link staff. '
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=sys_msg_title)
        else:
            sys_msg_title = 'Removal cancelled'
            message = 'You have successfully canceled wallet removal procedure.'
            await custom_messages.system_message(ctx=ctx, color_code=Colour.green, message=message, destination=0,
                                                 sys_msg_title=sys_msg_title)

    @account.command(aliases=["nfo", "i"])
    async def info(self, ctx):

        user_public = self.backoffice.third_level_manager.get_third_hot_wallet_addr(user_id=ctx.author.id)
        try:
            data = self.server.accounts().account_id(account_id=user_public).call()
            if data and 'status' not in data:
                # Send user account info
                await user_account_info(ctx=ctx, data=data, bot_avatar_url=self.bot.user.avatar_url)

            else:
                sys_msg_title = 'Stellar Wallet Query Server error'
                message = 'Status of the wallet could not be obtained at this moment'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=sys_msg_title)

        except NotFoundError:
            await server_error_response(destination=ctx.message.author,
                                        title=":exclamation: Account Not Activated :exclamation: ",
                                        error=f'Account has not been activated yet'
                                              f' Please activate it by depositing at least 2 XLM to '
                                              f'```{user_public}```')

    @three.group(aliases=["payment", "t", "p", "transaction", "pay"])
    @commands.check(user_has_third_level)
    async def tx(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':incoming_envelope: Payment/Transaction commands for level 3:incoming_envelope: '
            description = "List of sub-commands to handle payments and transactions for 3. level wallet"
            list_of_commands = [
                {"name": f':map: Prepare Payment Envelope for external address :map:',
                 "value": f'```{self.command_string}3 tx user <@discord.User> <wallet level> <amount XLM>```\n'
                          f'`Aliases: p, pay, tx, transaction`'},
                {"name": f':mag_right: Prepare Payment for Discord User :mag:',
                 "value": f'```{self.command_string}3 tx address <public address> <amount XLM>```'}
            ]
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @tx.command(aliases=["usr", "u"])
    async def user(self, ctx, recipient: Member, wallet_level: int, amount: float):
        """
        Create XDR payment envelope to be used for signing to some other users than discord
        """
        fee_atomic = 0
        dev_fee_activated = False

        atomic_amount = int(amount * (10 ** 7))
        recipient_check = ctx.message.author.id != recipient.id  # Boolean
        wallet_level_check = ctx.message.author.id == recipient.id and wallet_level != 3

        if wallet_level in self.available_levels:  # Check if user selected availabale level
            if recipient_check or wallet_level_check:
                if atomic_amount >= 100:
                    # Does recipient have registered selected wallet
                    if self.check_user_wallet_layer_level(layer=wallet_level, user_id=recipient.id):

                        # Get data of the user
                        recipient_data = self.get_recipient_details_based_on_layer(layer=wallet_level,
                                                                                   user_id=recipient.id)

                        # Check if account is live on network
                        if self.check_if_acc_is_live(address=recipient_data["address"]):
                            # get sender details
                            sender = self.acc_mng_rd_lvl.get_third_hot_wallet_addr(user_id=int(ctx.author.id))

                            await dev_fee_option_notification(destination=ctx.message.author)

                            verification_msg = await self.bot.wait_for('message', check=check(ctx.message.author),
                                                                       timeout=30)

                            if verification_msg.content.upper() in ["YES", "Y"]:
                                # Ask user with embed
                                await ask_for_dev_fee_amount(destination=ctx.message.author)

                                try:
                                    dev_fee_answ = await self.bot.wait_for('message', check=check(ctx.message.author),
                                                                           timeout=30)
                                    fee_selected = dev_fee_answ.content
                                    fee_number = float(fee_selected)
                                    fee_atomic = int(fee_number * (10 ** 7))
                                    if fee_atomic > 0:
                                        # Convert to atomic
                                        dev_fee_activated = True
                                    else:
                                        message = f'Dev fee is not allowed to be less than 0 or 0. It will be skipped.'
                                        await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                             destination=0,
                                                                             sys_msg_title=':warning: Dev Fee Error :warning:')

                                except ValueError:
                                    message = f'{dev_fee_answ} could not be converted to number and will therefore be skipped'
                                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                         destination=0,
                                                                         sys_msg_title=':warning: Dev Fee Error :warning:')
                            else:
                                message = f'Dev Fee will not be appended to transaction. '
                                await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                     destination=0,
                                                                     sys_msg_title=':robot:  Dev Fee Status :robot: ')

                            network_fee = 100  # Stroops
                            total_for_transaction = atomic_amount + network_fee + fee_atomic
                            requested_amount = total_for_transaction / (10 ** 7)
                            dev_fee_normal = fee_atomic / (10 ** 7)
                            fee_normal = network_fee / (10 ** 7)
                            net_amount = atomic_amount / (10 ** 7)

                            request_data = {"fromAddr": sender,
                                            "txTotal": f'{requested_amount:.7f}',
                                            "netValue": f'{net_amount:.7f}',
                                            "devFee": f'{dev_fee_normal:.7f}',
                                            "token": "XLM",
                                            "networkFee": f'{fee_normal:.7f}',
                                            "recipient": f"{ctx.author}",
                                            "toAddr": recipient_data["address"],
                                            "memo": recipient_data["memo"],
                                            "walletLevel": f"{wallet_level}"
                                            }
                            xdr_envelope = self.produce_envelope(tx_data=request_data,
                                                                 dev_fee_status=dev_fee_activated)

                            message = f":new::envelope: Has been created for Discord Transaction to wallet level {wallet_level} " \
                                      f" in value of ***{request_data['txTotal']} {request_data['token']}*** :rocket: "
                            await self.uplink_notification(message=message)
                            # Send details to sender on produced envelope
                            await send_xdr_info(ctx=ctx, request_data=request_data, envelope=xdr_envelope,
                                                command_type='discord')
                        else:
                            message = f'Registered Address `{recipient_data["address"]}` for recipient {recipient} has not' \
                                      f' been found on the network. Mostlikelly account has not been activate yet.'
                            await custom_messages.system_message(ctx=ctx, message=message, color_code=1,
                                                                 destination=ctx.author,
                                                                 sys_msg_title=CONST_XDR_ERROR)
                    else:
                        message = f'User {recipient} does not have wallet level {wallet_level} registered.'
                        await custom_messages.system_message(ctx=ctx, message=message, color_code=1,
                                                             destination=ctx.author,
                                                             sys_msg_title=CONST_XDR_ERROR)
                else:
                    message = f'Amount needs to be greater than  0.0000001. '
                    await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=ctx.author,
                                                         sys_msg_title=CONST_XDR_ERROR)

            else:
                message = f'Why would you want to send funds to your 3rd level wallet.'
                await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=ctx.author,
                                                     sys_msg_title=CONST_XDR_ERROR)

        else:
            message = f'Payment to wallet level {wallet_level} is not available at this moment.'
            await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=ctx.author,
                                                 sys_msg_title=CONST_XDR_ERROR)

    @tx.command(aliases=["addr", "a"])
    async def address(self, ctx, public_address: str, amount: float):
        """
        Create XDR to send to user on discord
        """
        """
        Create XDR payment envelope to be used for signing to some other users than discord
        """
        fee_atomic = 0
        atomic_amount = int(amount * (10 ** 7))
        dev_fee_activated = False

        if atomic_amount >= 100:
            # Get sender hot wallet
            if check_stellar_address(address=public_address):
                if self.check_if_acc_is_live(address=public_address):
                    user_address = self.acc_mng_rd_lvl.get_third_hot_wallet_addr(user_id=int(ctx.author.id))
                    if public_address != user_address:
                        if public_address != self.bot.backoffice.stellar_wallet.public_key:
                            request_data = {"fromAddr": user_address,
                                            "txTotal": f'{atomic_amount / (10 ** 7):.7f}',
                                            "netValue": f'{atomic_amount / (10 ** 7):.7f}',
                                            "devFee": CONST_DEV_FEE,
                                            "token": "XLM",
                                            "networkFee": f'0.0000100',
                                            "recipient": f"External Wallet",
                                            "toAddr": public_address,
                                            "memo": "From Discord",
                                            "walletLevel": f"External Wallet"
                                            }

                            xdr_envelope = self.produce_envelope(tx_data=request_data,
                                                                 dev_fee_status=CONST_DEV_ACTIVATED)

                            # Send details to sender on produced envelope
                            await send_xdr_info(ctx=ctx, request_data=request_data, envelope=xdr_envelope,
                                                command_type='discord')

                            message = f":new::envelope: has been created for external address in value of " \
                                      f"***{request_data['txTotal']} {request_data['token']}*** :rocket: "
                            await self.uplink_notification(message=message)

                        else:
                            message = f"You re trying to send funds to the Crypto Link hot wallet which is used for "
                            f" level 1 wallet hot wallet address. Funds might not come through as MEMO is "
                            f"required. If you wish to send it to your Level 1 wallet please "
                            f"use `{self.command_string}3 tx user `"
                            await custom_messages.system_message(ctx=ctx, message=message, color_code=1,
                                                                 destination=ctx.author,
                                                                 sys_msg_title=CONST_XDR_ERROR)
                    else:
                        message = 'No need to send it to yourself to 3 level'
                        await custom_messages.system_message(ctx=ctx, message=message, color_code=1,
                                                             destination=ctx.author,
                                                             sys_msg_title=CONST_XDR_ERROR)
                else:
                    message = f'Address `{public_address}` has not been activated yet.'
                    await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=ctx.author,
                                                         sys_msg_title=CONST_XDR_ERROR)
            else:
                message = f'Destination Address is not valid Stellar Public address'
                await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=ctx.author,
                                                     sys_msg_title=CONST_XDR_ERROR)
        else:
            message = f'Amount needs to be greater than 0.0000100 XLM'
            await custom_messages.system_message(ctx=ctx, message=message, color_code=1, destination=ctx.author,
                                                 sys_msg_title=CONST_XDR_ERROR)

    @three.group(aliases=["envelope", "env"])
    async def xdr(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':incoming_envelope: Transaction Signing and information :incoming_envelope: '
            description = "List of sub-commands to handle payments and transactions for 3. level wallet"
            list_of_commands = [
                {"name": f':pen_ballpoint: Sign Transaction envelope (XDR) :pen_ballpoint: ',
                 "value": f'```{self.command_string}3 xdr sign <Transaction XDR String>```\n'
                          f'`Aliases: s`'},

                {"name": f':arrow_forward: Check Envelope Details :arrow_forward:',
                 "value": f'```{self.command_string}3 xdr check <Transaction XDR String>```\n'
                          f'`Aliases: view, c `'}

            ]
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @xdr.command(aliases=["s"])
    async def sign(self, ctx, xdr_envelope: str):
        """
        Sign XDR envelope
        """

        imported = parse_transaction_envelope_from_xdr(xdr_envelope,
                                                       network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE)
        if isinstance(imported, TransactionEnvelope):
            details_to_sign = {
                "from": imported.transaction.source.public_key,
                "fee": f'{imported.transaction.fee / (10 ** 7):.7f}',
                "txSequence": imported.transaction.sequence,
                "operations": self.process_operations(imported.transaction.operations)
            }

            await xdr_data_to_embed(destination=ctx.author, data=details_to_sign)

            q = "Would you like to sign imported envelope and stream transaction to the network?"
            a = "```yes/y ==> Continue to signing with private key \nno/n ==> cancel request```"
            await user_approval_request(destination=ctx.author, question=q, answers=a)
            signature_approval = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=180)

            if signature_approval.content.upper() in ["YES", "Y"]:
                await ctx.author.send(content=f'{ctx.author.mention} Please provide private key :arrow_down:. you have '
                                              f'30 seconds to answer.')
                # Gets private key from user response
                private_key_response = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=30)
                private_key = private_key_response.content.upper()
                if self.check_private_key(private_key=private_key) and not re.search("[~!#$%^&*()_+{}:;\']",
                                                                                     private_key):
                    await self.show_typing(ctx)

                    result = self.stream_transaction_from_envelope(private_key=private_key, xdr_string=xdr_envelope)
                    if result[0]:
                        result_data = result[1]

                        await transaction_result(destination=ctx.message.author, result_data=result_data)
                        message = f":regional_indicator_x: :regional_indicator_d: :regional_indicator_r: Signed and " \
                                  f"dispatched :rocket: "
                        await self.uplink_notification(message=message)
                    else:
                        error = result[1]
                        title = f':exclamation: __Transaction Failed __ :exclamation: '
                        message = f'{error}'
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                             sys_msg_title=title)
                else:
                    title = f':exclamation: __ Private Key Error__ :exclamation: '
                    message = f'You have provided wrong private key `{private_key}`'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                         sys_msg_title=title)
            else:
                title = f':exclamation: __Transaction Cancelled__ :exclamation: '
                message = f'You have cancelled transaction successfully.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=title)

    @xdr.command(aliases=["c", "view"])
    async def check(self, ctx, xdr_envelope: str):
        """
        Sign XDR envelope
        """

        try:
            imported = parse_transaction_envelope_from_xdr(xdr_envelope,
                                                           network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE)
            if isinstance(imported, TransactionEnvelope):
                details_to_sign = {
                    "from": imported.transaction.source.public_key,
                    "fee": f'{imported.transaction.fee / (10 ** 7):.7f}',
                    "txSequence": imported.transaction.sequence,
                    "operations": self.process_operations(imported.transaction.operations)
                }

                await xdr_data_to_embed(destination=ctx.author, data=details_to_sign)
        except Exception:
            title = f':exclamation: __XDR import error__ :exclamation: '
            message = f'Provided string is not XDR envelope'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @three.error
    async def three_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'Requirements missing'
            message = f'In order to be able to access wallet level 3 you need to first register yourself in wallet ' \
                      f'level 2 with `{self.command_string}2 register`'
            await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_green, message=message, destination=0,
                                                 sys_msg_title=title)

    @new.error
    async def new_err(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'Registration status'
            message = f'You have already registered for a wallet of 3rd level. Use `{self.command_string}3` to' \
                      f'familiarize yourself with available commands.'
            await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_green, message=message, destination=0,
                                                 sys_msg_title=title)

        elif TimeoutError:
            title = f'__Time Run Out__'
            message = f'Your time to respond to bots request has expired and process has been therefore cancelled.' \
                      f' Please re-initiate the account registration process.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @own.error
    async def own_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'Registration status'
            message = f'You have already registered for a wallet of 3rd level. Use `{self.command_string}3` to' \
                      f'familiarize yourself with available commands. If you would like to update your wallet with' \
                      f' new address please use `{self.command_string}3 register update`.'
            await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_green, message=message, destination=0,
                                                 sys_msg_title=title)

        elif TimeoutError:
            title = f'__Time Run Out__'
            message = f'Your time to respond to bots request has expired and process has been therefore cancelled.' \
                      f' Please re-initiate the account registration process.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

        elif isinstance(error, commands.MissingRequiredArgument):
            title = f'__Missing Required argument__'
            message = f'You forgot to provide required argument `public address`. Please re-initiate the process and ' \
                      f'provide a Stellar valid public key/address.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @update.error
    async def update_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'3 level wallet not registered'
            message = f'You can not update the wallet address as you have not registered yourself yet to wallet level ' \
                      f'3 system. Please use first `{self.command_string}3 register new` or `{self.command_string}3 ' \
                      f'register own`'
            await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_green, message=message, destination=0,
                                                 sys_msg_title=title)

        elif TimeoutError:
            title = f'__Time Run Out__'
            message = f'Your time to respond to bots request has expired and process has been therefore cancelled.' \
                      f' Please re-initiate the account update process.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

        elif isinstance(error, commands.MissingRequiredArgument):
            title = f'__Missing Required argument__'
            message = f'You forgot to provide required argument `public address`. Please re-initiate the process and ' \
                      f'provide a Stellar valid public key/address.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @sign.error
    async def sign_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            title = f'__Missing Envelope__'
            message = f'You are required to provide XDR envelope to be able to sign it.  '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)
        elif TimeoutError:
            title = f'__Time Run Out__'
            message = f'Your time to respond to bots request has expired and process has been therefore cancelled.' \
                      f' Please re-initiate it '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @register.error
    async def reg_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'Requirements not met'
            message = 'In order to be eligible for wallet level 3 system please register first 2nd level wallet.'
            await custom_messages.system_message(ctx=ctx, color_code=Colour.red, message=message, destination=0,
                                                 sys_msg_title=title)
        elif TimeoutError:
            title = f'__Transaction Request Expired__'
            message = f'It took you to long to provide requested answer. Please try again or follow ' \
                      f'guidelines further from the Crypto Link. '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @account.error
    async def acc_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'Registration status'
            message = 'You can not access this command as you have not registered yet into the 3 level wallet system.' \
                      f' Please use first `{self.command_string}3 register` before you can query account details '
            await custom_messages.system_message(ctx=ctx, color_code=Colour.red, message=message, destination=0,
                                                 sys_msg_title=title)

    @tx.error
    async def t_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'Registration status'
            message = 'You can not access this command as you have not registered yet into the 3 level wallet system.' \
                      f' Please use first `{self.command_string}3 register` before you can create transactions/payments '
            await custom_messages.system_message(ctx=ctx, color_code=Colour.red, message=message, destination=0,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(LevelThreeAccountCommands(bot))
