from discord import Embed, Colour
from datetime import datetime
from cogs.utils.monetaryConversions import scientific_conversion, get_rates, rate_converter
from stellar_sdk import TransactionEnvelope, Payment, Asset, CreateAccount


async def account_layer_selection_message(destination, level: int):
    """
    Error message when user selects wrong account level
    """
    wallet_selection_info = Embed(title=":interrobang: Account Level Selection Error :interrobang: ",
                                  color=Colour.red())
    wallet_selection_info.add_field(name=f':warning: Wrong Level Selected :warning:',
                                    value=f'You have selected wallet level {level}. Only two available options'
                                          f' are :arrow_double_down:  ',
                                    inline=False)
    wallet_selection_info.add_field(name=f':one: Level 1 User Wallet by __Memo__ :one:',
                                    value=f'By selecting level 1, you will be making transaction to users wallet '
                                          f'which is identified in Crypto Link by the unique MEMO provided for user '
                                          f'upon registration. Wallet is fully custodial',
                                    inline=False)
    wallet_selection_info.add_field(name=f':two: Level 2 Custodial User Wallet __Public Address__ :two:',
                                    value=f'By selecting level 2, transaction will be done to users personal hot wallet '
                                          f' connected with the Crypto Link Wallet system',
                                    inline=False)
    await destination.send(embed=wallet_selection_info)


async def dev_fee_option_notification(destination):
    """
    Prompt user if he is willing to give dev fee
    """
    dev_fee_info = Embed(title=":robot: Optional Dev Fee for Crypto Link Team:robot: ",
                         color=Colour.lighter_gray())
    dev_fee_info.add_field(name=f':money_with_wings: Dev fee :money_with_wings: ',
                           value=f'If you would like to support us in what we are doing please answer with'
                                 f'***__Yes__*** and system will ask you for custom amount.'
                                 f'If you choose **__No__** than dev fee will be skipped.',
                           inline=False)
    await destination.send(embed=dev_fee_info)


async def ask_for_dev_fee_amount(destination):
    """
    Prompt to user to provide dev fee
    """
    dev_fee_info = Embed(title=":robot: Dev Fee Amount/Value :robot: ",
                         color=Colour.lighter_gray())
    dev_fee_info.add_field(name=f':money_with_wings: Value :money_with_wings: ',
                           value=f'Please provide amount in format 0.0000000 you are willing to contribute to '
                                 f'development. Crypto Link will than automatically append Payment operation to the '
                                 f'current transactions.',
                           inline=False)
    await destination.send(embed=dev_fee_info)


async def send_user_account_info(ctx, data, bot_avatar_url):
    """
    Send user account details from network for Layer 2
    """
    signers = " ".join(
        [f':map:`{signer["key"]}`\n:key:`{signer["type"]}` | :scales:`{signer["weight"]}`\n================' for
         signer in data["signers"]])
    dt_format = datetime.strptime(data["last_modified_time"], '%Y-%m-%dT%H:%M:%SZ')
    account_info = Embed(title=f':office_worker: 2 Level Wallet Information :office_worker:',
                         description="Bellow is up to date information on your 2 Level Wallet state",
                         colour=Colour.dark_blue(),
                         timestamp=datetime.utcnow())
    account_info.set_author(name=f'{ctx.message.author} (ID: {ctx.message.author.id})',
                            icon_url=bot_avatar_url,
                            url=data["_links"]["self"]['href'])
    account_info.set_thumbnail(url=ctx.message.author.avatar_url)
    account_info.add_field(name=":map: Account Address :map:",
                           value=f'```{data["account_id"]}```',
                           inline=False)
    account_info.add_field(name=":calendar: Last Updated :calendar: ",
                           value=f'`{dt_format}`',
                           inline=True)
    account_info.add_field(name=":ledger: Last Ledger :ledger:",
                           value=f'`{data["last_modified_ledger"]}`',
                           inline=True)
    account_info.add_field(name="Thresholds",
                           value=f'High: `{data["thresholds"]["high_threshold"]}`\n'
                                 f'Medium: `{data["thresholds"]["med_threshold"]}`\n'
                                 f'Low: `{data["thresholds"]["low_threshold"]}`')
    account_info.add_field(name=":money_with_wings: Sponsorship :money_with_wings: ",
                           value=f'Sponsored: `{data["num_sponsored"]}`\n'
                                 f'Sponsoring: `{data["num_sponsoring"]}`')
    account_info.add_field(name=":triangular_flag_on_post:  Flags :triangular_flag_on_post: ",
                           value=f'Immutable: `{data["flags"]["auth_immutable"]}`\n'
                                 f'Required: `{data["flags"]["auth_required"]}`\n'
                                 f'Revocable: `{data["flags"]["auth_revocable"]}`\n')
    account_info.add_field(name=f':pen_ballpoint: Account Signers :pen_ballpoint: ',
                           value=signers,
                           inline=False)
    account_info.add_field(name=f':sunrise:  Horizon Access :sunrise: ',
                           value=f'[Effects]({data["_links"]["effects"]["href"]}) | '
                                 f'[Offers]({data["_links"]["offers"]["href"]}) | '
                                 f'[Operations]({data["_links"]["operations"]["href"]}) | '
                                 f'[Payments]({data["_links"]["payments"]["href"]}) | '
                                 f'[Trades]({data["_links"]["payments"]["href"]}) | '
                                 f'[Transactions]({data["_links"]["transactions"]["href"]})',
                           inline=False)
    await ctx.author.send(embed=account_info)

    gems_nfo = Embed(title=f'Account balances',
                     color=Colour.dark_blue())
    for coin in data["balances"]:
        if not coin.get('asset_code'):
            cn = 'XLM'
        else:
            cn = coin["asset_code"]

        if cn == "XLM":
            rates = get_rates(coin_name=f'stellar')
            in_eur = rate_converter(float(coin['balance']), rates["stellar"]["eur"])
            in_usd = rate_converter(float(coin['balance']), rates["stellar"]["usd"])
            in_btc = rate_converter(float(coin['balance']), rates["stellar"]["btc"])
            in_eth = rate_converter(float(coin['balance']), rates["stellar"]["eth"])
            in_rub = rate_converter(float(coin['balance']), rates["stellar"]["rub"])
            in_ltc = rate_converter(float(coin['balance']), rates["stellar"]["ltc"])

            xlm_nfo = Embed(title=f'XLM Wallet Balance Details',
                            description=f'```{coin["balance"]} XLM```',
                            color=Colour.dark_blue())
            xlm_nfo.add_field(name=f':flag_us: USA',
                              value=f'$ {scientific_conversion(in_usd, 4)}')
            xlm_nfo.add_field(name=f':flag_eu: EUR',
                              value=f'€ {scientific_conversion(in_eur, 4)}')
            xlm_nfo.add_field(name=f':flag_ru:  RUB',
                              value=f'₽ {scientific_conversion(in_rub, 4)}')
            xlm_nfo.add_field(name=f'BTC',
                              value=f'₿ {scientific_conversion(in_btc, 8)}')
            xlm_nfo.add_field(name=f'ETH',
                              value=f'Ξ {scientific_conversion(in_eth, 8)}')
            xlm_nfo.add_field(name=f'LTC',
                              value=f'Ł {scientific_conversion(in_ltc, 8)}')
            xlm_nfo.set_footer(text='Conversion rates provided by CoinGecko',
                               icon_url="https://static.coingecko.com/s/thumbnail-007177f3eca19695592f0b8b0eabbdae282b54154e1be912285c9034ea6cbaf2.png")
            await ctx.author.send(embed=xlm_nfo)

        else:
            gems_nfo.add_field(name=f':gem: {cn} :gem:',
                               value=f"{coin['balance']}")


async def send_new_account_information(ctx, details: dict):
    """
    Information to user who has registered for second level wallet
    """
    new_account = Embed(title=f':new: Layer 2 Account Registration System :new:',
                        colour=Colour.lighter_gray()
                        )
    new_account.add_field(name=f':map: Public Address :map: ',
                          value=f'```{details["address"]}```',
                          inline=False)
    new_account.add_field(name=f':key: Secret :key: ',
                          value=f'```{details["secret"]}```',
                          inline=False)
    new_account.add_field(name=f':robot: Discord Sign Key for level 2 wallet to complete the signature :robot: ',
                          value=f'```{details["userHalf"]}```',
                          inline=False)
    new_account.add_field(name=f':warning: Important Message :warning:',
                          value=f'Please store/backup account details somewhere safe and delete this embed on'
                                f' Discord. Exposure of Secret to any other entity or 3rd party application'
                                f' might result in loss of funds, or funds being stolen. In order to complete'
                                f' registration for Second Layer please proceed to next step '
                                f':arrow_double_down: ',
                          inline=False)
    await ctx.author.send(embed=new_account, delete_after=360)


async def second_level_account_reg_info(destination):
    """
    Registration message info on entry when user wants to register for the second level wallet
    """
    intro_info = Embed(title=f':two: 2nd Level Wallet Registration Procedure :two:',
                       description='Welcome to interactive registration procedure to register second level wallet '
                                   'into Crypto Link system. Please follow the guidelines provided to you, '
                                   'in order for registration to be successful and **__READ OTHER DETAILS BELLOW__**.',
                       colour=Colour.orange())
    intro_info.add_field(name=f':information_source: Layer 2 wallet :information_source: ',
                         value='Level 2 Discord Wallet commands requires you to sign any wallet on-chain activity '
                               'which has been initiated from Discord. '
                               'Upon successful registration, system will securely store encrypted half of the private '
                               'key into database. Throughout the registration process, full private key will be sent '
                               'to your DM as well,  which you can utilize to access wallet also through other'
                               ' applications.',
                         inline=False)
    intro_info.add_field(name=f':exclamation: Stellar Account Merge :exclamation:  ',
                         value='Stellar allows as well for account merges. Since you control your private keys, '
                               'you can merge account through other applications. if Discord level 2 wallet '
                               ' will be used as a source account in Stellar Account Merge process, level 2 commands'
                               ' over Discord will stop working and become unavailable. ',
                         inline=False)
    intro_info.add_field(name=f':exclamation: Inactive Account :exclamation:  ',
                         value='When you will successfully complete the registration process, account will be inactive'
                               ' till minimum amount of XLM to activate account is sent to the address either by '
                               'other Discord user or by you through other application than Crypto Link')
    intro_info.add_field(name=f':exclamation: Responsibility :exclamation:  ',
                         value='Crypto Link system does not store private key in full. This means that in order for '
                               'operation of level 2 to be executed, you will be required to provide details uppon'
                               ' Crypto Link request through DM only. ***Crypto Link will never ask automatically '
                               ' for private key from user unless a command has been initiated from the user. '
                               'Once registration process is successfully completed, store private key somewhere safe'
                               ' and manually delete messages from the bot from your DM.***',
                         inline=False)
    intro_info.add_field(name=f':timer:  Responsibility  :timer: ',
                         value='Wallet level 2 commands are timed, which means that you have certain amount of seconds'
                               'in which you are required to respond to the prompt. Crypto Link will let you know when'
                               ' time expires.',
                         inline=False)
    intro_info.add_field(name=f':exclamation: Private Key and CL Staff :exclamation:  ',
                         value='Crypto Link Staff will ***NEVER ASK***  you to provide them private key details. '
                               'if you see such activity please report it immediately to the staff on Crypto Link '
                               'Community so we can user in the system.',
                         inline=False)
    intro_info.add_field(name=f':bellhop: YES/NO :bellhop: ',
                         value="Answer with ***YES/Y*** if you have read and understood instructions.",
                         inline=False)
    intro_info.set_footer(text='Timer= 180 seconds')

    await destination.send(embed=intro_info)


async def verification_request_explanation(destination):
    """
    Message which prompts user to verify private key uppon account registration process
    """
    verify_embed = Embed(title=":warning: Verification Required :warning:",
                         description="Please verify private key by "
                                     "re-type provided ***Discord Sign Key for level 2 wallet***",
                         color=Colour.orange())
    verify_embed.add_field(name=f':warning: Time limit :warning: ',
                           value=f'You have 60 seconds to provide an answer, otherwise the registration'
                                 f' will be cancelled and you will be required to repeat the process all over again.')
    verify_embed.set_footer(text="Timer: 60 Seconds")
    await destination.send(embed=verify_embed)


async def sign_message_information(destination, transaction_details: dict, layer: int = None, recipient=None):
    """
    Message prompting user to check details and sign transaction
    """
    sign_message = Embed(title=f':warning: Check Details and sign :warning:',
                         color=Colour.orange(),
                         timestamp=datetime.utcnow())
    sign_message.set_thumbnail(url=recipient.avatar_url)
    if layer:
        sign_message.add_field(name=f'Recipient Wallet Level',
                               value=f'{layer}',
                               inline=False)
    sign_message.add_field(name=f':cowboy: Recipient Details :cowboy:',
                           value=f"```{transaction_details['recipient']}```",
                           inline=False)
    sign_message.add_field(name=f'User Memo',
                           value=f'```{transaction_details["memo"]}```',
                           inline=False)
    sign_message.add_field(name=f'Wallet address',
                           value=f'```{transaction_details["toAddress"]}```',
                           inline=False)
    sign_message.add_field(name=f':money_with_wings: Transaction Values :money_with_wings: ',
                           value=f'```Total: {transaction_details["txTotal"]:.7f} XLM\n'
                                 f'===============================\n'
                                 f'Net Value: {transaction_details["netValue"]:.7f} XLM\n'
                                 f'Dev Fee: {transaction_details["devFee"]:.7f} XLM\n'
                                 f'Network fee: {transaction_details["networkFee"]:.7f} XLM```',
                           inline=False)
    sign_message.add_field(name=f':pen_ballpoint: Signature Required :pen_ballpoint:',
                           value='If you agree with transactions details please answer with ***__sign__*** and you '
                                 'will be asked for ***1/2*** of private key provided to you when you registered '
                                 'for level 2 wallet. If you would like to cancel transaction'
                                 ' please write ***__cancel__***',
                           inline=False)
    sign_message.add_field(name=f':timer: Signature Required :timer: ',
                           value='You have 40 seconds time to sign transactions, or else it will '
                                 'be cancelled automatically',
                           inline=False)
    await destination.send(embed=sign_message)


async def send_transaction_report(destination, response: dict):
    """
    Send basic transaction details once transaction successfully processed
    """
    tx_report = Embed(
        title=f':white_check_mark: Transactions Successfully Completed :white_check_mark:',
        description=f"Paging Token {response['paging_token']}",
        color=Colour.orange(),
        timestamp=datetime.utcnow())
    tx_report.add_field(name=f':calendar: Created At :calendar: ',
                        value=f'`{response["created_at"]}`')
    tx_report.add_field(name=f':ledger: Ledger :ledger: ',
                        value=f'`{response["ledger"]}`')
    tx_report.add_field(name=f':compass: Memo Details :compass:',
                        value=f'`{response["memo"]}`')
    tx_report.add_field(name=f':money_with_wings:  Network Fee Charged :money_with_wings: ',
                        value=f"{int(response['fee_charged']) / (10 ** 7):7f} XLM")
    tx_report.add_field(name=f':hash: Transaction Hash :hash:',
                        value=f'```{response["hash"]}```',
                        inline=False)
    tx_report.add_field(name=f':wrench: Operation Count :wrench:',
                        value=f'`{response["operation_count"]}`',
                        inline=False)
    tx_report.add_field(name=f':sunrise: Horizon Links :sunrise:',
                        value=f'[Transaction]({response["_links"]["self"]["href"]})\n'
                              f'[Operations]({response["_links"]["operations"]["href"]})\n'
                              f'[Effects]({response["_links"]["effects"]["href"]})\n')
    await destination.send(embed=tx_report)


async def send_operation_details(destination, envelope: str, network_type):
    """
    Send information to sender on operations inside transaction
    """
    data = TransactionEnvelope.from_xdr(envelope, network_type)
    operations = data.transaction.operations

    count = 1
    for op in operations:
        op_info = Embed(title=f'Operation No.{count}',
                        colour=Colour.green())
        if isinstance(op, Payment):
            print("++++++++++++++++++++++")
            op_info.add_field(name=f'Payment To:',
                              value=f'```{op.destination}```',
                              inline=False)
            if isinstance(op.asset, Asset):
                op_info.add_field(name=f'Payment Value',
                                  value=f'`{op.amount} {op.asset.code}`')

        elif isinstance(op, CreateAccount):
            op_info.add_field(name=f'Create Account for',
                              value=f'{op.destination}')
            op_info.add_field(name=f'Starting Balance',
                              value=f'{op.starting_balance}')

        await destination.send(embed=op_info)
        count += 1


async def recipient_incoming_notification(recipient, sender, wallet_level, data: dict, response: dict):
    """
    Notification for recipient when payment has been sent by the recipient to the Level 1 and Level 2
    account.
    """
    recipient_notify = Embed(title=f"Incoming Funds",
                             description="You have received this notification because someone made transaction "
                                         "to your wallet ",
                             colour=Colour.green(), timestamp=datetime.utcnow())
    recipient_notify.add_field(name=f'Deposit Wallet Level',
                               value=f'{wallet_level}', )
    recipient_notify.add_field(name=f'Memo',
                               value=f'{response["memo"]}', )
    recipient_notify.add_field(name=f'Sender',
                               value=f'{sender} \n'
                                     f'({sender.id})')
    recipient_notify.add_field(name=f':hash: Transaction Hash :hash:',
                               value=f'```{response["hash"]}```',
                               inline=False)
    recipient_notify.add_field(name=f'Payment Value',
                               value=f'{data["netValue"]} {data["token"]}')
    recipient_notify.add_field(name=":mega: Note :mega:",
                               value=f'If wallet level 1 was used as destination, Crypto Link '
                                     f'will notify you once deposit has been successfully processed.'
                                     f' For level wallet 2 you can use commands dedicated to ***Horizon***'
                                     f' queries. Be sure to say __Thank You___ to sender.')
    recipient_notify.add_field(name=f':sunrise: Horizon Links :sunrise:',
                               value=f'[Transaction]({response["_links"]["self"]["href"]})\n'
                                     f'[Operations]({response["_links"]["operations"]["href"]})\n'
                                     f'[Effects]({response["_links"]["effects"]["href"]})')

    try:
        await recipient.send(embed=recipient_notify)
    except Exception:
        pass


async def server_error_response(destination, error, title):
    """
    Server Response Error Handler
    """
    horizon_err = Embed(title=f':exclamation: {title} :exclamation:',
                        colour=Colour.red())
    horizon_err.add_field(name=f'Error Details',
                          value=f'{error}')
    await destination.send(embed=horizon_err)
