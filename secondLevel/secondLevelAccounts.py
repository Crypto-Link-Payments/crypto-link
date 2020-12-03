"""
Discord Commands dedicated to 2 wallet level system
"""
import asyncio

from stellar_sdk import Keypair, TransactionBuilder, Network, Payment, Asset
from stellar_sdk.exceptions import BadRequestError, MemoInvalidException, BadResponseError, \
    NotFoundError
from discord import Colour, Member
from discord.ext import commands
from utils.customCogChecks import has_wallet, user_has_second_level , is_dm, is_public, user_has_no_second
from cogs.utils.systemMessaages import CustomMessages
from utils.securityManager import SecurityManager
from utils.customMessages import user_account_info, dev_fee_option_notification, ask_for_dev_fee_amount
from secondLevel.utils.secondLevelCustMsg import account_layer_selection_message, sign_message_information, \
    send_transaction_report, \
    send_new_account_information, verification_request_explanation, second_level_account_reg_info, \
    server_error_response, send_operation_details, recipient_incoming_notification, send_uplink_message

security_manager = SecurityManager()
custom_messages = CustomMessages()


def check(author):
    """
    Check for author
    """

    def inner_check(message):
        """
        Check for answering the verification message on withdrawal. Author origin
        """
        if message.author.id == author.id:
            return True
        else:
            return False

    return inner_check


class LevelTwoAccountCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.server = self.backoffice.stellar_wallet.server
        self.available_layers = [1, 2, 3]
        self.network_type = Network.TESTNET_NETWORK_PASSPHRASE
        self.help_functions = self.backoffice.helper

    async def transaction_report_dispatcher(self, ctx, result: dict, data: dict = None):
        """
        Dispatch informational embeds to sender and Crypto Link Upling
        """
        # Send notification to user on transaction details
        await send_transaction_report(destination=ctx.message.author, response=result)
        # Send notification to user on types of operations in transaction
        await send_operation_details(destination=ctx.message.author,
                                     envelope=result['envelope_xdr'],
                                     network_type=self.network_type)

        # Send notification on transaction to Crypto Link Uplink
        load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                         self.backoffice.guild_profiles.get_all_explorer_applied_channels()]

        message = f":two::dollar: {data['netValue']} {data['token']} sent to ***{data['walletLevel']}***"
        await send_uplink_message(destinations=load_channels, message=message)

    @staticmethod
    async def show_typing(ctx):
        """
        Shows typing on Discord so user knows that something is happening in the background
        """
        async with ctx.author.typing():
            await asyncio.sleep(5)

    @staticmethod
    def process_error(error):
        """
        Convert error to user understandable string
        """
        err = ''
        if isinstance(error, BadRequestError):
            # Process errors
            for error in error.extras["result_codes"]["operations"]:
                if error == "op_underfunded":
                    err += "Insufficient Funds\n"
                elif error == "op_no_destination":
                    err += "Destination address does not exist or has not been activate yet"
        else:
            pass
        return err

    def check_user_wallet_layer_level(self, layer, user_id):
        """
        Check if user has registered account under selected wallet level
        """
        if layer == 1:
            return self.backoffice.account_mng.check_user_existence(user_id=user_id)
        elif layer == 2:
            return self.backoffice.second_level_manager.second_level_user_reg_status(user_id=user_id)
        elif layer == 3:
            return self.backoffice.second_level_manager.second_level_user_reg_status(user_id=user_id)

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
        elif layer == 2:
            # Details for transaction to level 2 wallet
            user_data = {
                "address": self.backoffice.second_level_manager.get_custodial_hot_wallet_addr(user_id=user_id),
                "memo": self.backoffice.account_mng.get_user_memo(user_id=user_id)["stellarDepositId"]
            }
            return user_data

    def stream_transaction_to_network(self, private_key: str, amount: str, tx_data: dict,
                                      dev_fee_status: bool = None):
        """
        Place Transaction on the network
        """
        net_value = tx_data["netValue"]
        key_pair = Keypair.from_secret(private_key)
        source_account = self.backoffice.stellar_wallet.server.load_account(key_pair.public_key)
        tx = TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=self.server.fetch_base_fee()

        ).append_payment_op(
            destination=tx_data["toAddress"],
            asset_code="XLM",
            amount=tx_data["netValue"]).add_text_memo(memo_text=tx_data["memo"])

        # Append Dev fee if selected
        if dev_fee_status:
            p = Payment(destination=self.backoffice.stellar_wallet.dev_key, asset=Asset.native(),
                        amount=tx_data["devFee"])
            tx.append_operation(operation=p)

        new_tx = tx.set_timeout(10).build()
        new_tx.sign(signer=private_key)

        try:
            # Sign Submit transaction to server
            result = self.server.submit_transaction(new_tx)

            return True, result
        except BadRequestError as e:
            print(f'Bad request {e}')
            return False, e
        except BadResponseError as e:
            print(f'Bad response {e}')
            return False, e
        except MemoInvalidException as e:
            print(f'Invalid memo {e}')
            return False, e
        except Exception as e:
            print(f'Else: {e}')
            return False, e

    @commands.group(aliases=["nd", '2', 'custodial'])
    @commands.check(has_wallet)
    async def two(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':wave:  __Welcome to Level 2 wallet system__ :wave:  '
            description = "Unlike Wallet __Level 1 system__, ***Level 2*** allows for full control of your" \
                          " ***private keys*** and with it, ability to import Discord wallet into other applications." \
                          " Upon successful registration and key verification, Crypto Link Stores and safely " \
                          "encrypts part of your private key. When executing on-chain actions for wallet over Discord," \
                          " you will be required to provide second part of the private key (sign) before action can be " \
                          " streamed to the Stellar network\n" \
                          "`Aliases: cust, c, 2`"
            list_of_values = [{"name": ":new: Register for in-active wallet :new: ",
                               "value": f"```{self.command_string}two register```\n"
                                        f"`Aliases: get, new. reg`"},
                              {"name": ":joystick: Group of commands to obtain info on Layer two Account :joystick: ",
                               "value": f"```{self.command_string}two account```\n"
                                        f"`Aliases: acc, a`"},
                              {
                                  "name": ":money_with_wings: Group of commands to create various transactions "
                                          ":money_with_wings:",
                                  "value": f"```{self.command_string}two payment```\n"
                                           f"`Aliases: pay, p, tx, transactions`"}
                              ]
            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.dark_orange())

    @two.command(aliases=["reg", "new", 'get'])
    @commands.check(is_dm)
    @commands.check(user_has_no_second)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def register(self, ctx):
        """
        Interactive registration procedure for second wallet level
        """
        # Entry message for the user
        await second_level_account_reg_info(destination=ctx.author)

        # Wait for answer
        welcome_verification = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=180)
        # Verify user answer
        if welcome_verification.content.upper() in ["YES", "Y"]:
            # Get private and public key
            details = self.backoffice.stellar_wallet.create_stellar_account()
            # Check if details returned
            if details:
                # User half of the key
                details["userHalf"] = details["secret"][:len(details["secret"]) // 2]

                # Send information with details of new account
                await send_new_account_information(ctx=ctx, details=details)

                # Message on explanation about verification
                await verification_request_explanation(destination=ctx.message.author)

                # Wait for user response
                verification_msg = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=60)

                if verification_msg.content.upper() == details["userHalf"]:
                    system_half = details["secret"][len(details["secret"]) // 2:]  # Second half of private key

                    # getting encrypted version of the key
                    encrypted_key = security_manager.encrypt(private_key=bytes(system_half, 'utf-8'))

                    # Producing data to be stored
                    data_to_store = {
                        "userId": int(ctx.author.id),
                        "publicAddress": details["address"],
                        "privateKey": encrypted_key
                    }

                    # Storing data
                    if self.backoffice.second_level_manager.create_user_wallet(data_to_store=data_to_store):
                        message = f"You have successfully verified your secret key and registered level 2 account" \
                                  f" into Crypto Link system. Public address and 1/2 of private" \
                                  f" key have been securely stored under your Discord User ID {ctx.author.id}. I" \
                                  f"n order for account to become active, you are required to activate it through " \
                                  f"on-chain deposit to address provided to you in previous steps"

                        await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_green(), destination=0,
                                                             sys_msg_title=':white_check_mark: Second Level Account'
                                                                           ' Created :white_check_mark:',
                                                             message=message)

                        load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                                         self.backoffice.guild_profiles.get_all_explorer_applied_channels()]
                        msg = ':new: User register for wallet level 2. :rocket: '
                        await send_uplink_message(destinations=load_channels, message=msg)

                    else:
                        message = 'There has been an issue while storing data into the system. Please re-initiate the' \
                                  ' whole process. If issue persists, contact Crypto Link Staff'
                        await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_red(), destination=0,
                                                             sys_msg_title=':exclamation: Second level wallet '
                                                                           'registration error :exclamation: ',
                                                             message=message)
                else:
                    message = 'You have provided wrong 1/2 of the key which resulted in private key mismatch.' \
                              ' Please re-initiate the registration process again'
                    await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_red(), destination=0,
                                                         sys_msg_title=':exclamation: Key verification Error'
                                                                       ' :exclamation: ',
                                                         message=message)
            else:
                message = 'There has been an issue while trying to create 2 level wallet. Please try again later.' \
                          ' If the issue persists please contact staff of the Crypto Link team.'
                await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_red(), destination=0,
                                                     sys_msg_title=':exclamation: Account Creation Error'
                                                                   ' :exclamation: ',
                                                     message=message)
        else:
            message = 'You have successfully cancelled second level wallet registration procedure.'
            await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_red(), destination=0,
                                                 sys_msg_title=':exclamation: Registration Cancelled'
                                                               ' :exclamation: ',
                                                 message=message)

    @two.group(aliases=["acc", "a"])
    @commands.check(user_has_second_level)
    async def account(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':joystick: __Available Custodial Account Commands__ :joystick: '
            description = "All commands available to operate with wallet level 2"
            list_of_values = [{"name": ":information_source: Get Account Details :information_source: ",
                               "value": f"```{self.command_string}custodial account info```\n"
                                        f"`Aliases: nfo`"}]
            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=0, c=Colour.dark_orange())

    @account.command(aliases=['nfo'])
    async def info(self, ctx):
        # Get address from database
        user_public = self.backoffice.second_level_manager.get_custodial_hot_wallet_addr(user_id=ctx.message.author.id)
        # Getting data from server for account
        try:
            data = self.server.accounts().account_id(account_id=user_public).call()
            if data and 'status' not in data:
                # Send user account info
                await user_account_info(ctx=ctx, data=data, bot_avatar_url=self.bot.user.avatar_url)

            else:
                sys_msg_title = 'Stellar Wallet Query Server error'
                message = 'Status of the wallet could not be obtained at this moment'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                     sys_msg_title=sys_msg_title)

        except NotFoundError:
            await server_error_response(destination=ctx.message.author,
                                        title=":exclamation: Account Not Activated :exclamation: ",
                                        error=f'Account has not been activated yet'
                                              f' Please activate it by depositing at least 2 XLM to '
                                              f'```{user_public}```')

    @two.group(aliases=["transaction", "tx", "pay", "p"])
    @commands.check(user_has_second_level)
    async def payment(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':incoming_envelope:  __Available Transaction Commands__ :incoming_envelope:  '
            description = "Commands dedicated to execution of transactions/payments"
            list_of_values = [{"name": ":cowboy: XLM Discord related payments  :cowboy:",
                               "value": f"```{self.command_string}2 tx user <@discord.Member> "
                                        f"<wallet level:int> <amount>```\n"
                                        f"**__Wallet Levels__**\n"
                                        f":one: => Transaction to 1st level Discord wallet based on MEMO\n"
                                        f":two: => Transaction to 2nd level Discord wallet owned by user over Discord\n"
                                        f"***Note***: All data is automatically obtained from the CL system once "
                                        f"recipient selected."
                                        f"\n`Aliases: usr, u`"},
                              {"name": ":map: XLM Non-Discord related recipients :map:",
                               "value": f"```{self.command_string}2 tx address <address> <amount>"
                                        f" <memo=optional>```\n"
                                        f"`Aliases: addr, a, add`"}
                              ]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.dark_orange())

    @payment.command(aliases=["usr", "u"])
    @commands.check(is_public)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def user(self, ctx, recipient: Member, wallet_level: int, amount: float):

        """
        Create Transaction To User on Discord
        """
        dev_fee_atomic = 0
        atomic_amount = int(amount * (10 ** 7))
        dev_fee_activated = False

        recipient_check = ctx.message.author.id != recipient.id  # Boolean
        wallet_level_check = ctx.message.author.id == recipient.id and wallet_level != 2

        # Check for allowed transaction channels
        if recipient_check or wallet_level_check:
            # Check if wallet level available
            if wallet_level in self.available_layers:
                # Check for minimum requirements to be met
                if atomic_amount >= 100:
                    # 3. Check if user has registered wallet level where user is planning to send funds
                    if self.check_user_wallet_layer_level(layer=wallet_level, user_id=recipient.id):
                        # DEV FEE Procedure
                        # Send notification to user about dev fee
                        await dev_fee_option_notification(destination=ctx.message.author)

                        # Ask for response
                        verification_msg = await self.bot.wait_for('message', check=check(ctx.message.author),
                                                                   timeout=30)

                        # Check verification whats going on
                        if verification_msg.content.upper() in ["YES", "Y"]:
                            # Ask user with embed
                            await ask_for_dev_fee_amount(destination=ctx.message.author)

                            try:
                                dev_fee_answ = await self.bot.wait_for('message', check=check(ctx.message.author),
                                                                       timeout=30)
                                fee_selected = dev_fee_answ.content
                                fee_number = float(fee_selected)
                                dev_fee_atomic = int(fee_number * (10 ** 7))
                                if dev_fee_atomic > 0:
                                    # Convert to atomic
                                    dev_fee_activated = True
                                else:
                                    message = f'Dev fee is not allowed to be less than 0 or 0. It will be skipped.'
                                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                         destination=0,
                                                                         sys_msg_title=':warning: Dev Fee Error '
                                                                                       ':warning:')
                            except ValueError:
                                message = f'{dev_fee_answ} could not be converted to number and will therefore be ' \
                                          f'skipped.'
                                await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                     destination=0,
                                                                     sys_msg_title=':warning: Dev Fee Error :warning:')
                        else:
                            message = f'Dev Fee will not be appended to transaction. '
                            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                                 sys_msg_title=':robot:  Dev Fee Status :robot: ')

                        # Calculations
                        network_fee = 100
                        total_for_transaction = atomic_amount + network_fee + dev_fee_atomic
                        requested_amount = total_for_transaction / (10 ** 7)
                        dev_fee_normal = dev_fee_atomic / (10 ** 7)
                        fee_normal = network_fee / (10 ** 7)
                        net_amount = atomic_amount / (10 ** 7)

                        # 3. Send information to the user to verify transaction with an answer with request to sign
                        recipient_details = self.get_recipient_details_based_on_layer(layer=wallet_level,
                                                                                      user_id=recipient.id)
                        data = {"txTotal": f'{requested_amount:.7f}',
                                "netValue": f'{net_amount:.7f}',
                                "devFee": f'{dev_fee_normal:.7f}',
                                "token": "XLM",
                                "networkFee": f'{fee_normal:.7f}',
                                "recipient": f"Discord User: {recipient}\n"
                                             f"User ID: {recipient.id}\n"
                                             f"Wallet Level: {wallet_level}",
                                "toAddress": recipient_details["address"],
                                "memo": recipient_details["memo"],
                                "walletLevel": f"Level {wallet_level} wallet"
                                }

                        await sign_message_information(destination=ctx.author,
                                                       transaction_details=data,
                                                       recipient=ctx.message.author, layer=None)

                        sign_transaction_answer = await self.bot.wait_for('message', check=check(ctx.message.author),
                                                                          timeout=10)

                        if sign_transaction_answer.content.upper() == "SIGN":
                            await ctx.author.send(
                                content=':robot: Please provide partial (1/2) private key bellow to sign '
                                        'transaction request.')

                            first_half_of_key = await self.bot.wait_for('message', check=check(ctx.message.author),
                                                                        timeout=80)
                            # DB 1/2 Private key
                            private_encrypted = self.backoffice.second_level_manager.get_private_key(
                                user_id=int(ctx.author.id))

                            second_half_of_key = security_manager.decrypt(token=private_encrypted["privateKey"]).decode(
                                'utf-8')
                            private_full = first_half_of_key.content + second_half_of_key

                            if self.help_functions.check_private_key(private_key=private_full):
                                await ctx.author.send(content='Transactions is being streamed to network. '
                                                              'Please wait few moments till its '
                                                              'completed and response received from Crypto Link')
                                await self.show_typing(ctx=ctx)

                                # Initiate transaction stream
                                result = self.stream_transaction_to_network(private_key=private_full,
                                                                            amount=net_amount,
                                                                            dev_fee_status=dev_fee_activated,
                                                                            tx_data=data)

                                # Process result returned from stream
                                if result[0]:
                                    if wallet_level == 1 and ctx.message.author.id != recipient:
                                        await recipient_incoming_notification(recipient=recipient,
                                                                              sender=ctx.message.author,
                                                                              wallet_level=wallet_level, data=data,
                                                                              response=result[1])

                                    elif wallet_level == 2 and ctx.message.author.id != recipient:
                                        await recipient_incoming_notification(recipient=recipient,
                                                                              sender=ctx.message.author,
                                                                              wallet_level=wallet_level, data=data,
                                                                              response=result[1])

                                    # Dispatch reports to recipient, sender and uplink
                                    await self.transaction_report_dispatcher(ctx=ctx, result=result[1], data=data)

                                else:
                                    hor_error = self.process_error(error=result[1])
                                    title = f':exclamation: __Transaction Stream Error__ :exclamation: '
                                    message = f'There has been an error in transaction: ```{hor_error}```'
                                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                         destination=0,
                                                                         sys_msg_title=title)
                            else:
                                title = f':exclamation: __Private Key Error__ :exclamation: '
                                message = f'Invalid Ed25519 Secret Seed provided. Please re-initiate the transaction' \
                                          f' request'
                                await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                     destination=1,
                                                                     sys_msg_title=title)

                    else:
                        title = f':exclamation: __Transaction Cancelled __ :exclamation: '
                        message = f'User {recipient} does not have active ***{wallet_level}. ' \
                                  f'Layer wallet***. Therefore transaction has been cancelled '
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                             sys_msg_title=title)
                else:
                    title = f':exclamation: __Transaction Amount Error __ :exclamation: '
                    message = f'Amount you are able to send needs to be greater than 0.0000001 XLM. You have selected' \
                              f' {atomic_amount / (10 ** 7):.7f} XLM'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                         sys_msg_title=title)
            else:
                await account_layer_selection_message(destination=ctx.message.author, level=wallet_level)
        else:
            title = f':exclamation: Destination error :exclamation: '
            message = f'There would be no point of sending yourself funds from wallet level 2 to wallet ' \
                      f'level 2. Only routes which are possible are: send funds to your wallet level 1' \
                      f' or than to another user wallet level 1 or 2'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)

    @payment.command(aliases=['addr', 'a', 'add'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def address(self, ctx, to_address: str, amount: float, memo: str = None):
        """
        Send to external Address from second level wallet
        """
        fee_atomic = 0
        atomic_amount = int(amount * (10 ** 7))
        dev_fee_activated = False

        if not memo:
            memo = 'None'

        if atomic_amount >= 100:
            if self.help_functions.check_memo(memo) and self.help_functions.check_public_key(address=to_address):

                # DEV FEE INTEGRATION PROCESS
                # Send notification to user about dev fee
                await dev_fee_option_notification(destination=ctx.message.author)

                # Ask for response
                verification_msg = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=30)

                # Check verification whats going on
                if verification_msg.content.upper() in ["YES", "Y"]:
                    # Ask user with embed
                    await ask_for_dev_fee_amount(destination=ctx.message.author)

                    try:
                        dev_fee_answ = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=30)
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
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                             sys_msg_title=':warning: Dev Fee Error :warning:')
                else:
                    message = f'Dev Fee will not be appended to transaction. '
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                         sys_msg_title=':robot:  Dev Fee Status :robot: ')

                # ############################## MAKE CALCULATIONS ###############################
                network_fee = 100  # Stroops
                total_for_transaction = atomic_amount + network_fee + fee_atomic  # Dev fee based on selected
                requested_amount = total_for_transaction / (10 ** 7)
                dev_fee_normal = fee_atomic / (10 ** 7)
                fee_normal = network_fee / (10 ** 7)
                net_amount = atomic_amount / (10 ** 7)

                # MAKING TRANSACTIONS
                # 3. Send information to the user to verify transaction with an answer with request to sign
                data = {"txTotal": f'{requested_amount:.7f}',
                        "netValue": f'{net_amount:.7f}',
                        "devFee": f'{dev_fee_normal:.7f}',
                        "token": "XLM",
                        "networkFee": f'{fee_normal:.7f}',
                        "recipient": f"{to_address}",
                        "toAddress": to_address,
                        "memo": memo,
                        "walletLevel": "External Wallet"
                        }

                await sign_message_information(destination=ctx.author,
                                               transaction_details=data,
                                               recipient=ctx.message.author, layer=None)
                sign_transaction_answer = await self.bot.wait_for('message', check=check(ctx.message.author),
                                                                  timeout=40)
                if sign_transaction_answer.content.upper() == "SIGN":
                    await ctx.author.send(
                        content=':robot: Please provide partial (1/2) private key bellow to sign '
                                'transaction request.')

                    first_half_of_key = await self.bot.wait_for('message', check=check(ctx.message.author),
                                                                timeout=80)

                    # DB 1/2 Private key
                    private_encrypted = self.backoffice.second_level_manager.get_private_key(
                        user_id=int(ctx.author.id))

                    # decipher secret key and use it for transaction stream
                    second_half_of_key = security_manager.decrypt(token=private_encrypted["privateKey"]).decode('utf-8')
                    private_full = first_half_of_key.content + second_half_of_key

                    if self.help_functions.check_private_key(private_key=private_full):
                        await ctx.author.send(content='Transactions is being sent to network. '
                                                      'Please wait few moments till its '
                                                      'completed')
                        await self.show_typing(
                            ctx=ctx)  # Shows the typing on discord so user knows that something is going on

                        # Stream tx and return tuple (Boolean , dict response)
                        result = self.stream_transaction_to_network(private_key=private_full,
                                                                    amount=net_amount,
                                                                    dev_fee_status=dev_fee_activated,
                                                                    tx_data=data)
                        if result[0]:
                            await self.transaction_report_dispatcher(ctx=ctx, result=result[1], data=data)
                        else:
                            hor_error = self.process_error(error=result[1])

                            title = f':exclamation: __Transaction Dispatch Error__ :exclamation: '
                            message = f'There has been an error in transaction: ```{hor_error}```'
                            await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                 destination=0,
                                                                 sys_msg_title=title)
                    else:
                        title = f':exclamation: __Private Key Error__ :exclamation: '
                        message = f'Invalid Ed25519 Secret Seed provided. Please try again fromm scratch'
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                             destination=0,
                                                             sys_msg_title=title)

                else:
                    title = f':exclamation: __Transaction Cancelled __ :exclamation: '
                    message = f'You have successfully cancelled transaction.'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                         sys_msg_title=title)

            else:
                title = f':exclamation: __ Wrong Details Provided__ :exclamation: '
                message = f'Either address, memo or both are invalid. Please try again.\n' \
                          f'```MEMO = allowed string encoded using either ASCII or UTF-8, up to 28-bytes long.\n' \
                          f'ADDRESS =  Valid Ed25519 Public Key Address supported by Stellar network.```'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=title)
        else:
            title = f':exclamation: __Transaction Amount Error __ :exclamation: '
            message = f'Amount you are able to send needs to be greater than 0.0000100 XLM. You have selected' \
                      f' {atomic_amount / (10 ** 7):.7f} XLM'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @two.error
    async def cust_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f"{error},In order to be able to use wallet of level 2, please register first into the " \
                      f"Crypto Link wallet level 1 system with  `{self.command_string}register`"
            title = f'**__User not found__** :clipboard:'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @account.error
    async def acc_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f"In order to be able to access commands under command group" \
                      f" `{self.command_string}custodial account` " \
                      f" user is required to:\n" \
                      f"- have registered custodial wallet into the system\n" \
                      f"- use command through DM with the Crypto Link"
            title = f'**__{self.command_string} custodial account error__**'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @register.error
    async def reg_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f"In order to be able to register, command needs to be executed over DM. If you have executed" \
                      f" it over DM and this error still pops up, than it most likely means that you have already " \
                      f"successfully registered 2 level account into Crypto Link system. Proceed with " \
                      f"`{self.command_string}custodial account`"
            title = f'**__Command check errors__**'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)
        elif TimeoutError:
            title = f'__Transaction Request Expired__'
            message = f'It took you to long to provide requested answer. Please try again or follow ' \
                      f'guidelines further from the Crypto Link. '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @user.error
    async def user_tx_error(self, ctx, error):
        print(error)
        if isinstance(error, commands.BadArgument):
            title = f'__Bad Argument Provided __'
            message = f'`{error}`'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)
        elif isinstance(error, commands.MissingRequiredArgument):
            title = f'__Missing Required Argument__'
            message = f'`{error}` Command structure is ```{self.command_string}custodial tx user  <@discord.User> ' \
                      f'<amount> <wallet level>```'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

        elif isinstance(error, commands.CheckFailure):
            title = f'__DM Lockdown__'
            message = f'This command needs to be initiated on one of the community channels where ' \
                      f'Crypto Link is present. This allows system to obtain recipient wallet details.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

        elif isinstance(error, AssertionError):
            title = f'__Wrong Amount Provided __'
            message = f'You have provided wrong details:' \
                      f'`{error}`'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)
        elif TimeoutError:
            title = f'__Transaction Request Expired__'
            message = f'It took you to long to provide requested answer. Please try again or follow ' \
                      f'guidelines further from the Crypto Link. '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @address.error
    async def addr_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            title = f'__Bad Argument Provided __'
            message = f'`{error}`'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)
        elif isinstance(error, AssertionError):
            title = f'__Wrong Amount Provided __'
            message = f'You have provided wrong amount for transaction amount:' \
                      f'`{error}`'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)
        elif isinstance(error,TimeoutError):
            title = f':timer: __Transaction Request Expired__ :timer: '
            message = f'It took you to long to answer. Please try again, follow guidelines and stay inside ' \
                      f'time-limits'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)
        else:
            print(error)


def setup(bot):
    bot.add_cog(LevelTwoAccountCommands(bot))
