from discord import Embed, Colour
from datetime import datetime
from cogs.utils.monetaryConversions import scientific_conversion, get_rates, rate_converter


async def account_layer_selection_message(destination, layer: int):
    wallet_selection_info = Embed(title=":interrobang: Account Layer Selection Error :interrobang: ",
                                  color=Colour.red())
    wallet_selection_info.add_field(name=f':warning: Wrong Layer Selection :warning:',
                                    value=f'You have selected wallet layer number {layer}. Only two available options'
                                          f' are :arrow_double_down:  ',
                                    inline=False)
    wallet_selection_info.add_field(name=f':one: Layer Custodial User Wallet by Memo',
                                    value=f'By selecting layer 1, you will be making transaction to users wallet '
                                          f'which is identified in the system by unique MEMO given for the user uppon'
                                          f' registration with the Crypto Link System.',
                                    inline=False)
    wallet_selection_info.add_field(name=f':two: Layer Custodial User Wallet by Public Address',
                                    value=f'By selecting layer 2, transaction will be done to users personal hot wallet '
                                          f'managed by the Crypto Link System which was created throughout the process'
                                          f' of registering custodial wallet.',
                                    inline=False)
    await destination.send(embed=wallet_selection_info)


async def dev_fee_option_notification(destination):
    dev_fee_info = Embed(title=":robot: Optional Dev Fee for Crypto Link Team:robot: ",
                         color=Colour.lighter_gray())
    dev_fee_info.add_field(name=f':money_with_wings: Dev fee :money_with_wings: ',
                           value=f'If you would like to support us in what we are doing please answer with'
                                 f'***__Yes__*** and system will ask you for custom amount.'
                                 f'If you choose **__No__** than dev fee will be skipped.',
                           inline=False)
    await destination.send(embed=dev_fee_info)


async def ask_for_dev_fee_amount(destination):
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
    account_info = Embed(title=f':office_worker: Account Information :office_worker:',
                         description="Bellow is up to date information on your custodial account state",
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
    Information for second level account registration. First embed shown to user on command .custodial register
    """
    intro_info = Embed(title=f':two: 2nd level wallet registration procedure :two:',
                       description='Welcome to interactive registration procedure to register second level wallet '
                                   'into Crypto Link system. Please follow the guidelines provided to you, '
                                   'in order for registration to be successful and **__READ OTHER DETAILS BELLOW__**.',
                       colour=Colour.orange())
    intro_info.add_field(name=f':information_source: Layer 2 wallet :information_source: ',
                         value='Level 2 Discord Wallet commands requires you to sign any wallet on-chain activity '
                               'which has been initiated from Discord. '
                               'Upon successful registration, system will securely store encrypted half of the private '
                               'key into database. '
                               'Throughout the registration process, full private key will be sent to your DM as well,'
                               ' which you can utilize to access wallet also through other applications.',
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
    intro_info.add_field(name=f':exclamation: Responsibility :exclamation:  ',
                         value='Crypto Link Staff will ***NEVER ASK***  you to provide them private key details. '
                               'if you see such activity please report it immediately to the staff on Crypto Link '
                               'Community so we can user in the system.',
                         inline=False)
    intro_info.add_field(name=f'YES/NO',
                         value="Answer with YES/Y if you have read, and understood instructions",
                         inline=False)

    await destination.send(embed=intro_info)


async def verification_request_explanation(destination):
    """
    Verification instruction
    """
    verify_embed = Embed(title=":warning: Verification Required :warning:",
                         description="Please verify private key by "
                                     "re-type provided ***Discord Sign Key for level 2 wallet***",
                         color=Colour.orange())
    verify_embed.add_field(name=f':warning: Time limit :warning: ',
                           value=f'You have 60 seconds to provide an answer, otherwise the registration'
                                 f' will be cancelled and you will be required to repeat the process all over again.')
    await destination.send(embed=verify_embed)


async def sign_message_information(destination, transaction_details: dict, layer: int = None, recipient=None):
    sign_message = Embed(title=f':warning: Check Details and sign :warning:',
                         color=Colour.orange(),
                         timestamp=datetime.utcnow())
    sign_message.set_thumbnail(url=recipient.avatar_url)
    sign_message.add_field(name=f'Chosen Wallet Level',
                           value=f'f{layer}',
                           inline=False)
    sign_message.add_field(name=f'Recipient',
                           value=f'f{recipient} (ID:{recipient.id}',
                           inline=False)
    sign_message.add_field(name=f'User Memo',
                           value=f'f{transaction_details["memo"]}',
                           inline=False)
    sign_message.add_field(name=f'Wallet address',
                           value=f'{transaction_details["address"]}',
                           inline=False)
    sign_message.add_field(name=f':pen_ballpoint: Signature Required :pen_ballpoint:',
                           value='If you agree with transactions details please answer with ***__sign__*** and you '
                                 'will be asked for 1/2 of private key provided to when you registered for wallet of '
                                 'level 2. If you would like to cancel transaction'
                                 ' please write ***__cancel__***')
    sign_message.add_field(name=f':timer: Signature Required :timer: ',
                           value='You have 120 seconds time to sign transactions, or else it will '
                                 'be cancelles automatically')
    await destination.send(embed=sign_message)


async def send_transaction_report(destination, response: dict):
    """
    Transaction report to sender
    """
    signers_data = ', '.join(
        [f'```{sig["key"]}```' for sig in
         response["signers"]])
    tx_report = Embed(
        title=f':white_check_mark: Transactions Successfully Completed :white_check_mark:',
        description=f"Paging Token {response['paging_token']}",
        color=Colour.orange(),
        timestamp=datetime.utcnow())
    tx_report.add_field(name=f':ledger: Ledger :ledger: ',
                        value=f'{response["ledger"]}')
    tx_report.add_field(name=f'Memo Details',
                        value=f'{response["memo"]} {response["memo_type"]}')
    tx_report.add_field(name=f':calendar: Created At :calendar: ',
                        value=f'{response["created_at"]}')
    tx_report.add_field(name=f':hash: Transaction Hash :hash:',
                        value=f'```{response["hash"]}```',
                        inline=False)
    tx_report.add_field(name=f':wrench: Operation Count :wrench:',
                        value=f'`{response["operation_count"]}`',
                        inline=False)
    tx_report.add_field(name=f':hash: Signers :hash:',
                        value=signers_data,
                        inline=False)
    tx_report.add_field(name=f':sunrise: Horizon Links :sunrise:',
                        value=f'[Transaction]({response["_links"]["self"]["href"]})\n'
                              f'[Operations]({response["_links"]["operations"]["href"]})\n'
                              f'[Effects]({response["_links"]["effects"]["href"]})\n')
    tx_report.add_field(name=f':sunrise: Network Fee :sunrise:',
                        value=f"{response['fee_charged'] * (10 ** 7)} XLM")
    await destination(embed=tx_report)


async def transaction_report_recipient(sender, recipient, amount, token, response: dict=None):
    """
    Transaction report to recipient of second level done to Discord Account
    """
    tx_report = Embed(
        title=f':inbox_tray: Incoming Payment :inbox_tray: ',
        description=f"You have received this notification because someone sent you payment through Crypto"
                    f" Link to one of the wallet levels. Please check details bellow.",
        color=Colour.green(),
        timestamp=datetime.utcnow())
    tx_report.add_field(name=f':calendar: Payment Date :calendar: ',
                        value=f'{response["created_at"]}',
                        inline=False)
    tx_report.add_field(name=f':cowboy: Sender Details :cowboy: ',
                        value=f'{sender} (ID:{sender.id})',
                        inline=False)
    tx_report.add_field(name=f':money_mouth: Payment Value :money_mouth:',
                        value=f'{amount} {token}',
                        inline=False)
    tx_report.set_thumbnail(url=sender.avatar_url)
    tx_report.add_field(name=f'Memo Details',
                        value=f'{response["memo"]}',
                        inline=False)
    tx_report.add_field(name=f':hash: Transaction Hash :hash:',
                        value=f'```{response["hash"]}```',
                        inline=False)
    tx_report.add_field(name=f':sunrise: Horizon Links :sunrise:',
                        value=f'[Transaction]({response["_links"]["self"]["href"]})\n'
                              f'[Operations]({response["_links"]["operations"]["href"]})\n'
                              f'[Effects]({response["_links"]["effects"]["href"]})\n',
                        inline=False)
    await recipient.send(embed=tx_report)
