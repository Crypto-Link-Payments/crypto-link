from discord import Embed, Colour, Member
from discord.ext import commands
from cogs.utils.customCogChecks import user_has_wallet, user_has_custodial, is_dm
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers
from utils.securityManager import SecurityManager

from custodialLayer.utils.custodialMessages import account_layer_selection_message, dev_fee_option_notification, \
    ask_for_dev_fee_amount, send_user_account_info, sign_message_information, send_transaction_report, \
    send_new_account_information, verification_request_explanation, second_level_account_reg_info

from stellar_sdk import Keypair, TransactionBuilder, Network, TransactionEnvelope, Payment, CreateAccount, \
    Asset
from stellar_sdk.exceptions import ConnectionError, BadRequestError, MemoInvalidException, BadResponseError, \
    UnknownRequestError, NotFoundError, Ed25519SecretSeedInvalidError

helper = Helpers()
security_manager = SecurityManager()
custom_messages = CustomMessages()
hot_wallets = helper.read_json_file(file_name='hotWallets.json')
integrated_coins = helper.read_json_file(file_name='integratedCoins.json')
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_ACC_REG_STATUS = '__Account registration status__'
ACCOUNT_MINIMUM_ATOMIC = 1


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


class CustodialAccounts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.list_of_coins = list(integrated_coins.keys())
        self.backoffice = bot.backoffice
        self.server = self.backoffice.stellar_wallet.server
        self.bot_hot_wallet = hot_wallets["xlm"]
        self.available_layers = [1, 2]
        self.network_type = Network.TESTNET_NETWORK_PASSPHRASE

    def get_network_base_fee(self):
        """
        Get network fee and handle error if error
        """
        try:
            return self.server.fetch_base_fee()
        except ConnectionError:
            return 0.0000001
        except NotFoundError:
            return 0.0000001
        except BadRequestError:
            return 0.0000001
        except BadResponseError:
            return 0.0000001
        except UnknownRequestError:
            return 0.0000001

    def get_network_acc_balance(self, data: dict):
        """
        Get balance of the account from network
        """
        if data:
            for coin in data["balances"]:
                if not coin.get('asset_code'):
                    return float(coin["balance"])
        else:
            return None

    def check_if_sufficient_balance(self, total_for_tx: int, sender_addr: str):
        """
        Check the balance of the account from server
        """
        try:
            sender_data = self.server.accounts.account_id(account_id=sender_addr).call()
            sender_balance = self.get_network_acc_balance(data=sender_data)
            if sender_balance and sender_balance >= total_for_tx:
                return True
            else:
                return False
        except Exception:
            return False

    def check_user_wallet_layer_level(self, layer, user_id):
        """
        Check if user has activate layer level
        """
        if layer == 1:
            return self.backoffice.account_mng.check_user_existence(user_id=user_id)
        elif layer == 2:
            self.backoffice.custodial_manager.second_level_user_reg_status(user_id=user_id)

    def check_private_key(self, private_key: str):
        """
        Check if private key constructed matches criteria
        """
        try:
            Keypair.from_secret(private_key)
            return True
        except Ed25519SecretSeedInvalidError:
            return False
        pass

    def get_recipient_details_based_on_layer(self, layer: int, user_id: int):
        """
        Get recipient details based on layer selected from database
        """
        if layer == 1:
            # Transaction will be done to user on custodial wallet where ID of wallet is based on MEMO
            user_data = {
                "address": self.bot_hot_wallet,
                "memo": self.backoffice.account_mng.get_user_memo(user_id=user_id)["stellarDepositId"]
            }
            return user_data
        elif layer == 2:
            # Transaction will be done to user hot wallet address where memo is represented from the one from DB
            user_data = {
                "address": self.backoffice.custodial_manager.get_custodial_hot_wallet_addr(user_id=user_id),
                "memo": self.backoffice.account_mng.get_user_memo
            }
            return user_data

    def stream_transaction(self, token, private_key: str, from_address, amount, recipient: dict,
                           dev_fee_status: bool = None,
                           dev_fee_amount: float = None):
        """
        Build Transaction
        """

        source_account = self.server.load_account(from_address)
        tx = TransactionBuilder(
            source_account=source_account,
            network_passphrase=self.network_type,
            base_fee=self.server.fetch_base_fee()).append_payment_op(destination=recipient["address"],
                                                                     asset_code="XLM",
                                                                     amount=amount).add_text_memo(
            memo_text=recipient["memo"])

        if dev_fee_status:
            tx.append_payment_op(destination=self.bot_hot_wallet,
                                 asset_code='XLM',
                                 amount=str(dev_fee_amount))

        # Build and sign
        tx.set_timeout(360).build().sign(signer=private_key)

        try:
            # Sign Submit transaction to server
            result = self.server.submit_transaction(tx)
            return True, result
        except MemoInvalidException:
            error = {
                "error": "Invalid Memo Provided"
            }
            return False, error

    async def send_operation_details(self, destination, envelope: str):
        """
        Breaks down all operations from envelope and send information
        """
        data = TransactionEnvelope.from_xdr(envelope, self.network_type)
        operations = data.transaction.operations

        count = 1
        for op in operations:
            op_info = Embed(title=f'Operation No.{count}',
                            colour=Colour.green())
            if isinstance(op, Payment):
                op_info.add_field(name=f'From',
                                  value=f'```{op.source}```',
                                  inline=False)
                op_info.add_field(name=f'To',
                                  value=f'```{op.destination}```',
                                  inline=False)
                if isinstance(op.asset, Asset):
                    op_info.add_field(name=f'Payment Value',
                                      value=f'{op.amount} {op.asset.code}')

            elif isinstance(op, CreateAccount):
                op_info.add_field(name=f'Create Account for',
                                  value=f'{op.destination}')
                op_info.add_field(name=f'Starting Balance',
                                  value=f'{op.starting_balance}')

            await destination.send(embed=op_info)
            count += 1

    @commands.group(aliases=['cust', 'c'])
    @commands.check(user_has_wallet)
    async def custodial(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':joystick: __Available Custodial Wallet Commands__ :joystick: '
            description = "All commands to operate with custodial wallet system (Layer 2) in Crypto Link"
            list_of_values = [{"name": "Register for In-active Custodial Wallet ",
                               "value": f"`{self.command_string}custodial register`"},
                              {"name": "Group of commands to obtain info on Layer two Account",
                               "value": f"`{self.command_string}custodial account`"},
                              {"name": "Group of commands to create various transactions",
                               "value": f"`{self.command_string}custodial account`"}
                              ]
            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.dark_orange())

    @custodial.command()
    @commands.check(is_dm)
    async def register(self, ctx):
        """
        Interactive registration procedure for second wallet level
        """
        # Check if custodial level is not registered yet
        if not self.backoffice.custodial_manager.second_level_user_reg_status(user_id=ctx.author.id):

            # Get public and private key from the sdk
            await second_level_account_reg_info(destination=ctx.author)

            # Wait for answer
            welcome_verification = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=180)

            # Verify user answer
            if welcome_verification.contet.upper() in ["YES", "Y"]:
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
                        if self.backoffice.custodial_manager.create_user_wallet(data_to_store=data_to_store):
                            message = "You have successfully verified your secret key and registered level 2 account" \
                                      " into Crypto Link System. Public address and 1/2 of private" \
                                      " key have been stored. In order for account to become " \
                                      "active, you are required to activate it through on-chain deposit to address " \
                                      "provided to you in previous steps"
                            await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_green(), destination=0,
                                                                 sys_msg_title=':white_check_mark: Second Layer Account'
                                                                               ' Create :white_check_mark:',
                                                                 message=message)

                        else:
                            message = 'There has been an issue while storing data into the system. Please re-initiate '
                            await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_red(), destination=0,
                                                                 sys_msg_title=':white_check_mark: Second Layer '
                                                                               'Account Created :white_check_mark:',
                                                                 message=message)
                    else:
                        message = 'Account could not be verified as the Signature key provided for Discord activity is' \
                                  ' not the same as provided to you above. Please initiate registration process again.'
                        await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_red(), destination=0,
                                                             sys_msg_title=':exclamation: Key verification error'
                                                                           ' :exclamation: ',
                                                             message=message)
                else:
                    message = 'There has been an issue while trying to create in-active account. Please try again later.'
                    await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_red(), destination=0,
                                                         sys_msg_title=':exclamation: Account Creation Error'
                                                                       ' :exclamation: ',
                                                         message=message)
            else:
                message = 'You have successfully cancelled second level wallet registration system.'
                await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_red(), destination=0,
                                                     sys_msg_title=':exclamation: Registration Cancelled'
                                                                   ' :exclamation: ',
                                                     message=message)
        else:
            message = f'You have already registered your second level account. To check account details please use ' \
                      f'`{self.command_string}custodial account`.'
            await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_red(), destination=0,
                                                 sys_msg_title=':exclamation: Second Level Account Already Registered'
                                                               ' :exclamation: ',
                                                 message=message)

    @custodial.group()
    @commands.check(user_has_custodial)
    @commands.check(is_dm)
    async def account(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':joystick: __Available Custodial Account Commands__ :joystick: '
            description = "All commands to operate with custodial wallet system (Layer 2) in Crypto Link"
            list_of_values = [{"name": "Get Account Details",
                               "value": f"`{self.command_string}custodial account info`"}]
            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.dark_orange())

    @account.command()
    async def info(self, ctx):
        # Get address from database
        user_public = self.backoffice.custodial_manager.get_custodial_hot_wallet_addr(user_id=ctx.message.author)
        # Getting data from server for account
        data = self.server.accounts().account_id(account_id=user_public).call()
        if data and 'status' not in data:
            # Send user account info
            await send_user_account_info(ctx=ctx, data=data, bot_avatar_url=self.bot.user.avatar_url)

        else:
            sys_msg_title = 'Stellar Wallet Query Server error'
            message = 'Status of the wallet could not be obtained at this moment'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=sys_msg_title)

    @custodial.group()
    @commands.check(user_has_custodial)
    async def tx(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':joystick: __Available Transaction Commands__ :joystick: '
            description = "All commands to operate with custodial wallet system (Layer 2) in Crypto Link"
            list_of_values = [{"name": "Discord related payments",
                               "value": f"`{self.command_string}custodial tx user <amount> <@discord.Member> <wallet level:int>`\n"
                                        f"**__Wallet Levels__**\n"
                                        f":one: => tx to custodial wallet based on MEMO\n"
                                        f":two: => tx to non custodial wallet owned by user over Discord"},
                              {"name": "Non-Discord related payments",
                               "value": f"`{self.command_string}custodial tx address <amount> <token> "
                                        f"<to_address> <memo = Optional>`"}
                              ]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.dark_orange())

    @tx.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def user(self, ctx, amount: float, recipient: Member, layer: int):
        """
        Create Transaction To User on Discord
        """
        dev_fee = 0
        atomic = amount * (10 ** 7)
        dev_fee_activated = False

        # 1. Check if layer where user wants to send money exists
        if layer in self.available_layers:
            # 2. Check if amount selected is greater than 0.0000100 XLM
            if atomic >= 100:
                # 3. Check if user has registered layer and layer in available options
                if self.check_user_wallet_layer_level(layer=layer, user_id=recipient.id):

                    ############################### DEV FEE ADDITION #############################
                    # Send notification to user about dev fee
                    await dev_fee_option_notification(destination=ctx.message.author)

                    # Ask for response
                    verification_msg = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=30)

                    # Check verification whats going on
                    if verification_msg.content.upper() in ["YES", "Y"]:
                        # Ask user with embed
                        await ask_for_dev_fee_amount(destination=ctx.message.author)

                        try:
                            dev_fee_answ = float(
                                await self.bot.wait_for('message', check=check(ctx.message.author), timeout=30))
                            if isinstance(dev_fee_answ, float):
                                if dev_fee_answ > 0:
                                    # Convert to atomic
                                    dev_fee = dev_fee_answ * (10 ** 7)
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
                        print('Dev fee not Selected skipp')

                    ############################ CALCULATE TOTAL ##############################
                    # Calculate Totals
                    total_for_transaction = atomic + dev_fee
                    total_with_minimum = total_for_transaction + ACCOUNT_MINIMUM_ATOMIC
                    fee = self.get_network_base_fee()
                    total_with_network_fee = total_with_minimum + fee

                    requested_amount = atomic / (10 ** 7)
                    dev_fee_normal = dev_fee / (10 ** 7)
                    account_minimum = ACCOUNT_MINIMUM_ATOMIC / (10 ** 7)
                    fee_normal = self.get_network_base_fee() / (10 ** 7)

                    ############################ START MAKING TRANSACTION ##############################

                    # 1. Check if user has sufficient balance
                    user_public = self.backoffice.custodial_manager.get_custodial_hot_wallet_addr(
                        user_id=ctx.message.author)

                    if self.check_if_sufficient_balance(sender_addr=user_public,
                                                        total_for_tx=total_with_network_fee):

                        # 2. Returned memo and address
                        recipient_data = self.get_recipient_details_based_on_layer(layer=layer, user_id=recipient.id)

                        # 3. Send information to the user to verify transaction with an answer with request to sign
                        recipient_data["transaction_details"] = {"requested": requested_amount,
                                                                 "devFee": dev_fee_normal,
                                                                 "networkFee": fee_normal}
                        await sign_message_information(destination=ctx.author,
                                                       transaction_details=recipient_data,
                                                       recipient=recipient, layer=layer)

                        sign_transaction_answer = await self.bot.wait_for('message', check=check(ctx.message.author),
                                                                          timeout=10)

                        if sign_transaction_answer.upper() == "SIGN":
                            await ctx.author.send(
                                content=':robot: Please provide partial (1/2) private key bellow to sign '
                                        'transaction request.')

                            first_half_of_key = await self.bot.wait_for('message', check=check(ctx.message.author),
                                                                        timeout=80)

                            # DB 1/2 Private key
                            private_encrypted = self.backoffice.custodial_manager.get_private_key(
                                user_id=int(ctx.author.id))

                            # decypher secret key and use it for transaction stream

                            second_half_of_key = security_manager.decrypt(token=private_encrypted)
                            private_full = first_half_of_key + second_half_of_key

                            if self.check_private_key(private_key=private_full):
                                result = self.stream_transaction(token='XLM', private_key=private_full,
                                                                 from_address=user_public,
                                                                 amount="total to send",
                                                                 recipient=recipient_data,
                                                                 dev_fee_status=dev_fee_activated,
                                                                 dev_fee_amount=dev_fee)

                                if result[0]:
                                    # If result was successfull than make info
                                    response = result[1]

                                    # Send notification to user on transaction details
                                    await send_transaction_report(destination=ctx.message.author, response=response)
                                    # Send notification to user on types of operations in transaction
                                    await self.send_operation_details(destination=ctx.message.author,
                                                                      envelope=response['envelope_xdr'])

                                else:
                                    title = f':exclamation: __Transaction Error__ :exclamation: '
                                    message = f'Transaction could not be completed. Please try again later.' \
                                              f'Error: ```{result[1]["error"]}```'
                                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                         destination=1,
                                                                         sys_msg_title=title)
                            else:
                                title = f':exclamation: __Private Key Error__ :exclamation: '
                                message = f'Invalid Ed25519 Secret Seed provided. Please try again fromm scratch'
                                await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                     destination=1,
                                                                     sys_msg_title=title)
                        else:
                            title = f':exclamation: __Transaction Cancelled __ :exclamation: '
                            message = f'You have successfully cancelled transaction.'
                            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                                 sys_msg_title=title)

                    else:
                        title = f':exclamation: Insufficient Amount __ :exclamation: '
                        message = f' You have insufficient balance in your hot wallet ' \
                                  f'({total_with_network_fee / (10 ** 7)} XLM) or there has been network error while' \
                                  f'trying to check your balance.\n' \
                                  f'===============================\n' \
                                  f'Transaction Value Breakdown:\n' \
                                  f'===============================\n' \
                                  f'For Transfer: `{requested_amount} XLM`\n' \
                                  f'Dev Fee:`{dev_fee_normal}XLM`\n' \
                                  f'Network Fee: `{fee_normal} XLM`\n' \
                                  f'Account Min: `{account_minimum} XLM'
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                             sys_msg_title=title)
                else:
                    title = f':exclamation: __Transaction Cancelled __ :exclamation: '
                    message = f'User {recipient} does not have active ***{layer}. Layer wallet***. Therefore transaction' \
                              f' has been cancelled '
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                         sys_msg_title=title)
            else:
                title = f':exclamation: __Transaction Amount Error __ :exclamation: '
                message = f'Amount you are able to send needs to be greater than 0.0000001 XLM. You have selected' \
                          f' {atomic / (10 ** 7):.7f} XLM'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                     sys_msg_title=title)
        else:
            await account_layer_selection_message(destination=ctx.message.author, layer=layer)

    @tx.command(aliases=['addr'])
    async def address(self, ctx, amount, token, to_address, memo: str = None):
        """
        Send to external Address
        """
        pass

    @custodial.error
    async def cust_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f"In order to be able to use custodial wallet (Layer 2 wallet) please register first into the " \
                      f"Crypto Link system with {self.command_string}register"
            title = f'**__User not found__** :clipboard:'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @account.error
    async def acc_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            print(error)
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
            message = f"You are allowed to register for Second Layer account only through the **direct message**" \
                      f" with Crypto Link."
            title = f'**__Wrong Channel Type__**'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @user.error
    async def user_tx_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            title = f'__Bad Argument Provided __'
            message = f'`{error}`'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)
        elif isinstance(error, AssertionError):
            title = f'__Wrong Amount Provided __'
            message = f'You have provided wrong amount for transaction amount:' \
                      f'`{error}`'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)
        elif TimeoutError:
            title = f'__Transaction Request Expired__'
            message = f'It took you to long to provide requested answer. Please try again or follow ' \
                      f'guidliness further from the Crypto Link. '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(CustodialAccounts(bot))
