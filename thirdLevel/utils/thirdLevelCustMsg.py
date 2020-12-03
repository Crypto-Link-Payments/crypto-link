from discord import Embed, Colour
from datetime import datetime


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
    xdr_info.add_field(name="From Address",
                       value=f'```{request_data["fromAddr"]}```',
                       inline=False)
    xdr_info.add_field(name="Address",
                       value=f'```{request_data["toAddr"]}```',
                       inline=False)

    if command_type == 'public':
        xdr_info.add_field(name="Token and Amount",
                           value=f'{request_data["amount"]} {request_data["token"]}',
                           inline=False)
    elif command_type == "discord":
        xdr_info.add_field(name="Transaction Net Value",
                           value=f'{request_data["txTotal"]} {request_data["token"]}',
                           inline=False)
        xdr_info.add_field(name=":hammer_pick: Dev Fee :hammer_pick: ",
                           value=f'`{request_data["devFee"]} XLM`',
                           inline=False)

    elif command_type == "activate":
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
