from discord import Embed, Colour
from datetime import datetime
from cogs.utils.monetaryConversions import scientific_conversion, get_rates, rate_converter


async def new_acc_details(author, details: dict):
    new_account = Embed(title=f':white_check_mark:  Wallet Details registered in Crypto Link :white_check_mark: ',
                        description="Public level 3 wallet details, have been successfully stored in "
                                    "Crypto Link database. ",
                        colour=Colour.lighter_gray(),
                        timestamp=datetime.utcnow()
                        )
    new_account.add_field(name=f'Your discord details',
                          value=f'```{author}\n'
                                f'{author.id}```',
                          inline=True
                          )
    new_account.add_field(name=f':map: Public Address :map: ',
                          value=f'```{details["publicAddress"]}```',
                          inline=False)
    new_account.add_field(name=f':warning: Important :warning:  ',
                          value=f'Crypto Link does not store your private key, therefore it can not be recovered.'
                                f' You can update your account details with dedicated commands for 3 level.',
                          inline=False)
    new_account.add_field(name=f':exclamation: Important :exclamation:  ',
                          value=f' Make Sure that registered public address is active on Stellar Network.',
                          inline=False)
    new_account.set_footer(text='This message will self destruct in 120 seconds')

    await author.send(embed=new_account, delete_after=120)


async def third_level_acc_details(destination, details: dict):
    """
    Information to user who has registered for second level wallet
    """
    new_account = Embed(title=f':new: Level 3 Account Registration System :new:',
                        colour=Colour.lighter_gray()
                        )
    new_account.add_field(name=f':map: Public Address :map: ',
                          value=f'```{details["address"]}```',
                          inline=False)
    new_account.add_field(name=f':key: Secret :key: ',
                          value=f'```{details["secret"]}```',
                          inline=False)
    new_account.add_field(name=f':warning: Important Message :warning:',
                          value=f'Please store/backup account details somewhere safely and delete this embed on'
                                f' Discord. Exposure of Secret to any other entity or 3rd party application'
                                f' might result in loss of funds, or funds being stolen',
                          inline=False)
    new_account.set_footer(text='This message will self destruct in  360 seconds')
    await destination.send(embed=new_account, delete_after=360)


async def third_level_own_reg_info(destination):
    intro_info = Embed(title=f':three: 3nd Level Own Wallet Registration Procedure :three:',
                       description='Welcome to 3rd level wallet registration procedure on Crypto Link.'
                                   ' ',
                       colour=Colour.orange())
    intro_info.add_field(name=f':information_source: About Level 3 :information_source: ',
                         value='Level 3 wallet is fully non-custodial wallet. Responsibility for private keys '
                               'is completely on your side. Crypto Link stores only your public key (wallet address)'
                               ' under your unique Discord ID, in order to ease operations over Discord and to allow'
                               ' for interoperability. All on-chain actions are required to be signed with full'
                               ' private key through Discord Dedicated commands, our Terminal application or '
                               'any other app supporting importing of XDR.',
                         inline=False)
    intro_info.add_field(name=f':envelope: Utilizing the stellar XDR (envelope) :envelope:  ',
                         value=f'Wallet level 3 transactions/payments operate through XDR. also known as External '
                               f'Data Representation, and is used throughout the Stellar network and protocol.'
                               f' When user initiates transaction over Discord a XDR string will be returned'
                               f' which can be later imported either through additional command for signing'
                               f' or in any other app, allowing to import Transaction Envelopes (XDR). '
                               f'For further refference please se'
                               f' [about XDR](https://developers.stellar.org/docs/glossary/xdr/)'
                               f' on Stellar web page. ',
                         inline=False)
    intro_info.set_footer(text='This message will self destruct in 240 seconds')

    await destination.send(embed=intro_info)


async def third_level_account_reg_info(destination):
    """
    Registration message info on entry when user wants to register for the second level wallet
    """
    intro_info = Embed(title=f':three: 3nd Level Wallet Registration Procedure :three:',
                       description='Welcome to 3rd level wallet registration procedure on Crypto Link.'
                                   ' ',
                       colour=Colour.orange())
    intro_info.add_field(name=f':information_source: About Level 3 :information_source: ',
                         value='Level 3 wallet is fully un-custodial wallet. Responsibility for private keys '
                               'is completely on your side. Crypto Link stores only your public key (wallet address)'
                               ' under your unique Discord ID, in order to ease operations over Discord and to allow'
                               ' for interoperability. All on-chain actions are required to be signed with full'
                               ' private key through Discord Dedicated commands. Wallet can be accessed through any '
                               'other application supporting importing through private key. ',
                         inline=False)
    intro_info.add_field(name=f':envelope: Utilizing the stellar XDR (envelope) :envelope:  ',
                         value=f'Wallet level 3 transactions/payments operate through XDR. also known as External '
                               f'Data Representation, and is used throughout the Stellar network and protocol.'
                               f' When user initiates transaction over Discord a XDR string will be returned'
                               f' which can be later imported either through additional command for signing'
                               f' or in any other app, allowing to import Transaction Envelopes (XDR). '
                               f'For further refference please se [about XDR](https://developers.stellar.org/docs/glossary/xdr/)'
                               f' on Stellar web page. ',
                         inline=False)
    intro_info.add_field(name=f':exclamation: Stellar Account Merge :exclamation:  ',
                         value=f'Stellar allows as well for account merges. Since you control your private keys, '
                               f'you can merge account through other applications. If you decided to do so, please '
                               f'update the wallet public key through dedicated command.',
                         inline=False)
    intro_info.add_field(name=f':exclamation: Inactive Account :exclamation:  ',
                         value='When you will successfully complete the registration process, account will be inactive'
                               ' till minimum amount of XLM to activate account is sent to the address either by '
                               'other Discord user or by you through other application than Crypto Link')
    intro_info.add_field(name=f':exclamation: Responsibility :exclamation:  ',
                         value='Crypto Link system does not store newly generated private key of level 3 wallet.'
                               ' Therefore in order for on-chain operation of wallet level 3 you are required to '
                               'sign a transaction once XDR is successfully processed. ***Crypto Link will never '
                               'ask automatically for private key from user unless a command has been initiated '
                               ' from the user. Once registration process is successfully completed, store private'
                               ' key somewhere safe and manually delete messages from the bot from your DM.***',
                         inline=False)
    intro_info.add_field(name=f':exclamation: Private Key and CL Staff :exclamation:  ',
                         value='Crypto Link Staff will ***NEVER ASK***  you to provide them private key details. '
                               'if you see such activity please report it immediately to the staff on Crypto Link '
                               'Community so we can user in the system.',
                         inline=False)
    intro_info.set_footer(text='This message will self destruct in 240 seconds')

    await destination.send(embed=intro_info, delete_after=240)


async def send_xdr_info(ctx, request_data: dict, envelope: str, command_type: str):
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

    elif command_type == "discord":
        xdr_info.add_field(name="From Address",
                           value=f'```{request_data["fromAddr"]}```',
                           inline=False)
        xdr_info.add_field(name="To Address",
                           value=f'```{request_data["toAddress"]}```',
                           inline=False)
        xdr_info.add_field(name="Token and Amount",
                           value=f'{request_data["txTotal"]} {request_data["token"]}',
                           inline=False)

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
                       value=f'```{envelope}```',
                       inline=False)
    xdr_info.add_field(name=":warning: Note :warning:",
                       value=f'Copy the XDR envelope to application which allows __importing of '
                             f' a transaction envelope in XDR format and follow procedures there.'
                             f'If you do not have access to such application than you can use as well\n'
                             f'[Stellar Laboratory Transaction Signer]'
                             f'(https://laboratory.stellar.org/#txsigner?network=test)',
                       inline=False)

    await ctx.author.send(embed=xdr_info)


async def xdr_data_to_embed(destination, data: dict):
    xdr_nfo = Embed(title=":regional_indicator_x: :regional_indicator_d: :regional_indicator_r:",
                    description="Bellow are details from provided XDR",
                    colour=Colour.orange())
    xdr_nfo.add_field(name=f':money_with_wings: Transaction fee :money_with_wings: ',
                      value=f'`{data["fee"]} XLM`')
    xdr_nfo.add_field(name=f':abacus:  Transaction Sequence :abacus: ',
                      value=f'`{data["txSequence"]}`')
    xdr_nfo.add_field(name=f':map:  Source Account :map: ',
                      value=f'```{data["from"]}```',
                      inline=False)

    await destination.send(embed=xdr_nfo)

    for op in data["operations"]:
        op_data = Embed(title=f'{op["type"].capitalize()} operation',
                        colour=Colour.orange())
        op_data.add_field(name=f':map: Destination :map:',
                          value=f'```{op["to"]}```',
                          inline=False)
        op_data.add_field(name=f':moneybag:  Amount :moneybag: ',
                          value=f'`{op["amount"]} {op["code"]}`',
                          inline=False)
        op_data.add_field(name=f':gem: Asset :gem: ',
                          value=f':bank: Issuer :bank: :\n```{op["issuer"]}```')

        await destination.send(embed=op_data)


async def user_approval_request(destination, question: str, answers: str):
    prompt_request = Embed(title="Answer Required",
                           description="Since this command requires user approval/response"
                                       " you are required to answer on prompt bellow.",
                           colour=Colour.orange())
    prompt_request.add_field(name=f'Prompt',
                             value=f'```{question}```',
                             inline=False)
    prompt_request.add_field(name=f'Required Answers',
                             value=f'{answers}')
    prompt_request.set_footer(text='You have 15 second to answer')
    await destination.send(embed=prompt_request)


async def transaction_result(destination, result_data: dict):
    try:
        links = result_data["_links"]
        result_nfo = Embed(title=':white_check_mark: Transaction Sent Successfully :white_check_mark: ',
                           colour=Colour.green())
        result_nfo.add_field(name=':calendar: Created at :calendar: ',
                             value=f'{result_data["created_at"]}')
        result_nfo.add_field(name=':money_with_wings:  Fee Payed :money_with_wings:  ',
                             value=f'`{int(result_data["fee_charged"]) / (10 ** 7):.7f} XLM`')
        result_nfo.add_field(name=':ledger:  Ledger :ledger:  ',
                             value=f'`{result_data["ledger"]}`')
        result_nfo.add_field(name=':pencil: Memo :pencil:   ',
                             value=f'`{result_data["memo"]}`')
        result_nfo.add_field(name=':tools: Operations Count :tools:    ',
                             value=f'`{result_data["operation_count"]}`')
        result_nfo.add_field(name=':white_circle: Paging Token :white_circle: ',
                             value=f'`{result_data["paging_token"]}`')
        result_nfo.add_field(name=':map: Source Account :map: ',
                             value=f'```{result_data["source_account"]}```',
                             inline=False)
        result_nfo.add_field(name=f':sunrise: Horizon Link :sunrise: ',
                             value=f'[Account]({links["account"]["href"]})  |  '
                                   f'[Operations]({links["operations"]["href"]})  |  '
                                   f'[Self]({links["self"]["href"]})  |  '
                                   f'[Transaction]({links["transaction"]["href"]})')
        await destination.send(embed=result_nfo)
    except Exception as e:
        print(e)
        raise


async def server_error_response(destination, error, title):
    """
    Server Response Error Handler
    """
    horizon_err = Embed(title=f':exclamation: {title} :exclamation:',
                        colour=Colour.red())
    horizon_err.add_field(name=f'Error Details',
                          value=f'{error}')
    await destination.send(embed=horizon_err)


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
