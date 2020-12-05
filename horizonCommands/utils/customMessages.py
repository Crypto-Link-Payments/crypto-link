from discord import Embed, Colour
from re import sub

CONST_HASH = ':hash: Transaction Hash :hash:'
CONST_PAG = ':white_circle: Paging Token :white_circle: '


async def horizon_error_msg(destination, error):
    horizon_err = Embed(title=f':exclamation: Horizon API error :exclamation:',
                        colour=Colour.red())
    horizon_err.add_field(name=f'Error Details',
                          value=f'{error}')
    await destination.send(embed=horizon_err)


async def account_create_msg(destination, details):
    new_account = Embed(title=f':new: Stellar Testnet Account Created :new:',
                        description=f'You have successfully created new in-active account on {details["network"]}. Do'
                                    f' not deposit real XLM as this account has been created on testnet. '
                                    f'Head to [Stellar Laboratory](https://laboratory.stellar.org/#account-creator?network=test)'
                                    f' and use Friend bot to activate account',
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
                                f' Discord. Exposure of `Secret` :key: to any other entity or 3rd party application '
                                f'might result in loss of funds and account beeing stolen. '
                                f'Crypto Link does not store details of newly generate accounts nor can recover them.',
                          inline=False)
    await destination.send(embed=new_account, delete_after=360)


async def send_details_for_stellar(destination, coin, data, date, signers):
    acc_details = Embed(title=':mag_right: Details for Stellar Account :mag:',
                        description=f'Last Activity {date} (UTC)',
                        colour=Colour.lighter_gray())
    acc_details.add_field(name=':calendar:  Last Activity :calendar:  ',
                          value=f'`{date}`',
                          inline=False)
    acc_details.add_field(name=':map: Account Address :map: ',
                          value=f'```{data["account_id"]}```',
                          inline=False)
    acc_details.add_field(name=':pen_fountain: Account Signers :pen_fountain: ',
                          value=signers,
                          inline=False)
    acc_details.add_field(name=f' :moneybag: Balance :moneybag:',
                          value=f'`{coin["balance"]} XLM`',
                          inline=False)
    acc_details.add_field(name=' :genie: Sponsorship Activity :genie:',
                          value=f':money_mouth: {data["num_sponsored"]} (sponsored)\n'
                                f':money_with_wings: {data["num_sponsoring"]} (sponsoring) ',
                          inline=False)
    acc_details.add_field(name=f':man_judge: Liabilities :man_judge: ',
                          value=f'Buying Liabilities: {coin["buying_liabilities"]}\n'
                                f'Selling Liabilities: {coin["selling_liabilities"]}',
                          inline=False)
    acc_details.add_field(name=f':scales:  Thresholds :scales: ',
                          value=f'High: {data["thresholds"]["high_threshold"]}\n'
                                f'Medium: {data["thresholds"]["med_threshold"]}\n'
                                f'Low: {data["thresholds"]["low_threshold"]}',
                          inline=False)
    acc_details.add_field(name=f':triangular_flag_on_post: Flags :triangular_flag_on_post:',
                          value=f'Auth Required: {data["flags"]["auth_required"]}\n'
                                f'Auth Revocable: {data["flags"]["auth_revocable"]}\n'
                                f'Auth Immutable:{data["flags"]["auth_immutable"]}')
    acc_details.add_field(name=f':sunrise: Horizon Link :sunrise:',
                          value=f'[Data]({data["_links"]["data"]["href"]}) | [Offers]({data["_links"]["offers"]["href"]})\n'
                                f'[Transactions]({data["_links"]["transactions"]["href"]}) | [Effects]({data["_links"]["effects"]["href"]})\n'
                                f'[Operations]({data["_links"]["operations"]["href"]}) | [Payments]({data["_links"]["payments"]["href"]})\n'
                                f'[Trades]({data["_links"]["trades"]["href"]})',
                          inline=False)
    await destination.send(embed=acc_details)


async def send_details_for_asset(destination, coin, data, date):
    """
    Additional informational embed if account has present assets

    """
    asset_details = Embed(title=f':coin: Details for asset {coin["asset_code"]} :coin:',
                          description=f'Last Activity on {date} (UTC)'
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
    await destination.send(embed=asset_details)


async def send_asset_details(destination, data, request):
    toml_access = data['_embedded']['records'][0]['_links']['toml']['href']
    record = data['_embedded']['records'][0]

    asset_info = Embed(title=f':bank: Issuer Details :bank:',
                       description=f'Bellow is represent information for requested {request}.',
                       colour=Colour.lighter_gray())
    asset_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                         value=f'[Horizon]({data["_links"]["self"]["href"]})')

    if not toml_access:
        toml_data = None
        toml_link = 'None'
    else:
        toml_data = "Access link"
        toml_link = toml_access

    asset_info = Embed(title=" :bank: __Issuer Details__ :bank:",
                       description='Here are the details for specified Asset Query',
                       colour=Colour.lighter_gray())
    asset_info.add_field(name=f':regional_indicator_c: Asset Code :regional_indicator_c:',
                         value=f'{record["asset_code"]}')
    asset_info.add_field(name=f':gem: Asset Type :gem:',
                         value=f'{record["asset_type"]}')
    asset_info.add_field(name=f':scroll: TOML :scroll: ',
                         value=f'[{toml_data}]({toml_link})')
    asset_info.add_field(name=f':map: Asset Issuer :map: ',
                         value=f'```{record["asset_issuer"]}```',
                         inline=False)
    asset_info.add_field(name=f':moneybag: Issued Amount :moneybag: ',
                         value=f'`{record["amount"]} {record["asset_code"]}`',
                         inline=True)
    asset_info.add_field(name=f':cowboy: Account Count :cowboy: ',
                         value=f'`{record["num_accounts"]}`')
    asset_info.add_field(name=f':triangular_flag_on_post: Account Flags :triangular_flag_on_post: ',
                         value=f'Immutable: {record["flags"]["auth_immutable"]} \n'
                               f'Required:  {record["flags"]["auth_required"]}\n'
                               f'Revocable:  {record["flags"]["auth_revocable"]}\n')
    asset_info.add_field(name=f':white_circle: Paging Token :white_circle:',
                         value=f'```{record["paging_token"]}```',
                         inline=False)
    await destination.send(embed=asset_info)


async def send_multi_asset_case(destination, data, command_str):
    records = data['_embedded']['records']

    asset_info = Embed(title=f':gem: Multiple Assets Found :gem: ',
                       description=f'Please use `{command_str}assets issuer <issuer address >` to'
                                   f' obtain additional data on **asset issuer*** or ',
                       colour=Colour.lighter_gray())
    asset_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                         value=f'[Horizon]({data["_links"]["self"]["href"]})',
                         inline=False)
    asset_info.add_field(name=f' Total Found ',
                         value=f'{len(records)} assets with code {records[0]["asset_code"]}',
                         inline=False)
    asset_count = 1
    for asset in records:

        if not asset['_links']['toml']['href']:
            toml_data = None
            toml_link = ''
        else:
            toml_data = "Access link"
            toml_link = asset['_links']['toml']['href']

        asset_info.add_field(name=f'{asset_count}. Asset',
                             value=f':map: Issuer :map: \n'
                                   f'```{asset["asset_issuer"]}```\n'
                                   f':moneybag: Amount Issued :moneybag: \n'
                                   f'`{asset["amount"]} {asset["asset_code"]}`\n'
                                   f':globe_with_meridians: toml access :globe_with_meridians: \n'
                                   f'[{toml_data}]({toml_link})',
                             inline=False)
        asset_count += 1

    await destination.send(embed=asset_info)


async def tx_info_for_account(destination, record: dict, signers: str, memo, date):
    account_record = Embed(title=f':record_button: Account Transaction Record :record_button:',
                           colour=Colour.dark_orange())
    account_record.add_field(name=':ledger: Ledger :ledger: ',
                             value=f'`{record["ledger"]}`')
    account_record.add_field(name=CONST_PAG,
                             value=f'`{record["paging_token"]}`')
    account_record.add_field(name=f':calendar: Created :calendar: ',
                             value=f'`{date}`',
                             inline=True)
    account_record.add_field(name=f' :map: Source account :map: ',
                             value=f'```{record["source_account"]}```',
                             inline=False)
    account_record.add_field(name=f' :pencil: Memo :pencil:  ',
                             value=f'`{memo}`',
                             inline=False)
    account_record.add_field(name=f':pen_ballpoint: Signers :pen_ballpoint: ',
                             value=signers,
                             inline=False)
    account_record.add_field(name=CONST_HASH,
                             value=f'`{record["hash"]}`',
                             inline=False)
    account_record.add_field(name=':money_with_wings: Fee :money_with_wings: ',
                             value=f'`{round(int(record["fee_charged"]) / 10000000, 7):.7f} XLM`',
                             inline=False)
    account_record.add_field(name=f':sunrise: Horizon Link :sunrise:',
                             value=f'[Account]({record["_links"]["account"]["href"]})\n'
                                   f'[Ledger]({record["_links"]["ledger"]["href"]})\n'
                                   f'[Transactions]({record["_links"]["transaction"]["href"]})\n'
                                   f'[Effects]({record["_links"]["effects"]["href"]})\n'
                                   f'[Operations]({record["_links"]["succeeds"]["href"]})\n'
                                   f'[Succeeds]({record["_links"]["succeeds"]["href"]})\n'
                                   f'[Precedes]({record["_links"]["precedes"]["href"]})')
    await destination.send(embed=account_record)


async def tx_info_for_hash(destination, data: dict, signatures, date: str, memo):
    single_info = Embed(title=f':hash: Transaction Hash Details :hash:',
                        colour=Colour.dark_orange())
    single_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                          value=f'[Transaction Hash]({data["_links"]["self"]["href"]})')
    single_info.add_field(name=':ledger: Ledger :ledger: ',
                          value=f'`{data["ledger"]}`')
    single_info.add_field(name=CONST_PAG,
                          value=f'`{data["paging_token"]}`',
                          inline=True)
    single_info.add_field(name=f':calendar: Created :calendar: ',
                          value=f'`{data["created_at"]}`',
                          inline=False)
    single_info.add_field(name=f' :map: Source account :map: ',
                          value=f'`{data["source_account"]}`',
                          inline=False)
    single_info.add_field(name=f' :pencil:  Memo :pencil: ',
                          value=f'`{memo}`',
                          inline=False)
    single_info.add_field(name=f':pen_ballpoint: Signers :pen_ballpoint: ',
                          value=signatures,
                          inline=False)
    single_info.add_field(name=CONST_HASH,
                          value=f'`{data["hash"]}`',
                          inline=False)
    single_info.add_field(name=':money_with_wings: Fee :money_with_wings: ',
                          value=f'`{round(int(data["fee_charged"]) / 10000000, 7):.7f} XLM`',
                          inline=False)
    single_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                          value=f'[Ledger]({data["_links"]["ledger"]["href"]})\n'
                                f'[Transactions]({data["_links"]["transaction"]["href"]})\n'
                                f'[Effects]({data["_links"]["effects"]["href"]})\n'
                                f'[Operations]({data["_links"]["succeeds"]["href"]})\n'
                                f'[Succeeds]({data["_links"]["succeeds"]["href"]})\n'
                                f'[Precedes]({data["_links"]["precedes"]["href"]})')
    await destination.send(embed=single_info)


async def send_effects(destination, data, usr_query, key_query):
    horizon_query = data['_links']['self']['href']

    effects_info = Embed(title=f':fireworks: {key_query} Effects :fireworks:  ',
                         description=f'Bellow are last three effects which happened for {usr_query}',
                         colour=Colour.lighter_gray())
    effects_info.add_field(name=f':sunrise: Horizon Access :sunrise: ',
                           value=f'[{key_query} Effects]({horizon_query})')
    effects_info.add_field(name=f':three: Last Three Effects :three: ',
                           value=f':arrow_double_down: ',
                           inline=False)
    await destination.send(embed=effects_info)


async def send_effect_details(destination, effect: dict):
    effect_type = sub('[^a-zA-Z0-9\n\.]', ' ', effect["type"])
    eff_embed = Embed(title=f':fireworks: {effect_type.capitalize()} :fireworks: ',
                      colour=Colour.lighter_gray())
    eff_embed.add_field(name=f':calendar:  Created :calendar: ',
                        value=f'`{effect["created_at"]}`',
                        inline=False)
    eff_embed.add_field(name=f':white_circle: Paging Token :white_circle:',
                        value=f'`{effect["paging_token"]}`')
    eff_embed.add_field(name=f':map: Account :map:',
                        value=f'```{effect["account"]}```',
                        inline=False)
    eff_embed.add_field(name=f':id: ID :id:',
                        value=f'`{effect["id"]}`',
                        inline=False)
    eff_embed.add_field(name=f':sunrise: Horizon Link :sunrise: ',
                        value=f'[Effect Link]({effect["_links"]["operation"]["href"]})',
                        inline=False)
    await destination.send(embed=eff_embed)


async def tx_info_for_ledger(destination, ledger_id, record: dict, signatures, date):
    """
    Send transaction information based on ledger
    """
    ledger_record = Embed(title=f':record_button: Record for {ledger_id} :record_button:',
                          colour=Colour.dark_orange())
    ledger_record.add_field(name=CONST_PAG,
                            value=f'`{record["paging_token"]}`',
                            inline=False)
    ledger_record.add_field(name=f':calendar: Created :calendar: ',
                            value=f'`{date}`',
                            inline=False)
    ledger_record.add_field(name=f' :map: Source account :map: ',
                            value=f'`{record["source_account"]}`',
                            inline=False)
    ledger_record.add_field(name=f' Source account Sequence ',
                            value=f'`{record["source_account_sequence"]}`',
                            inline=False)
    ledger_record.add_field(name=f':pen_ballpoint: Signers :pen_ballpoint: ',
                            value=signatures,
                            inline=False)
    ledger_record.add_field(name=CONST_HASH,
                            value=f'`{record["hash"]}`',
                            inline=False)
    ledger_record.add_field(name=f':sunrise: Horizon Link :sunrise:',
                            value=f'[Record]({record["_links"]["self"]["href"]})\n'
                                  f'[Account]({record["_links"]["account"]["href"]})\n'
                                  f'[Ledger]({record["_links"]["ledger"]["href"]})\n'
                                  f'[Transactions]({record["_links"]["transaction"]["href"]})\n'
                                  f'[Effects]({record["_links"]["effects"]["href"]})\n'
                                  f'[Succeeds]({record["_links"]["succeeds"]["href"]})\n'
                                  f'[Precedes]({record["_links"]["precedes"]["href"]})')
    await destination.send(embed=ledger_record)


async def send_offers(destination, address, offers_link):
    address_details = Embed(title=f':clipboard: Offers By Address :clipboard: ',
                            colour=Colour.lighter_gray())
    address_details.add_field(name=f':map: Address :map:',
                              value=f'```{address}```',
                              inline=False)
    address_details.add_field(name=f':sunrise: Horizon Link :sunrise:',
                              value=f'[Offers for account]({offers_link})',
                              inline=False)
    address_details.add_field(name=f':three: Last 3 Updated Offers :three:',
                              value=f':arrow_double_down:',
                              inline=False)
    await destination.send(embed=address_details)


async def offer_details(destination, offer: dict):
    """
    Send offer details
    """
    offer_details = Embed(title=f':id: {offer["id"]} :id:',
                          colour=Colour.lighter_gray())
    offer_details.add_field(name=f':calendar: Last Modified :calendar: ',
                            value=f'{offer["last_modified_time"]}',
                            inline=False)
    offer_details.add_field(name=f':white_circle: Paging Token :white_circle:',
                            value=f'{offer["paging_token"]}',
                            inline=False)
    offer_details.add_field(name=f':map: Seller Details :map:',
                            value=f'```{offer["seller"]}```',
                            inline=False)

    # Processing offer
    selling_string = ''
    if offer["selling"]["asset_type"] != 'native':
        selling_string += f'{offer["amount"]} {offer["selling"]["asset_code"]} @ '
    else:
        selling_string += f'{offer["amount"]} XLM @ '

    if offer['buying']['asset_type'] != 'native':
        selling_string += f' {offer["price"]} {offer["buying"]["asset_code"]}'

    else:
        selling_string += f' {offer["price"]}/XLM @'

    offer_details.add_field(name=f':handshake: Offer Details :handshake: ',
                            value=f'`{selling_string}`',
                            inline=False)

    # Processing Issuers
    asset_issuers = ''
    if offer['buying']['asset_type'] != 'native':
        asset_issuers += f':gem: {offer["buying"]["asset_code"]} (Buying) :gem:\n' \
                         f'```{offer["buying"]["asset_issuer"]}```'
    else:
        asset_issuers += f':coin: XLM :coin: \n' \
                         f'```Native Currency```'

    if offer['selling']['asset_type'] != 'native':
        asset_issuers += f'\n:gem: Selling {offer["selling"]["asset_code"]} (Selling) :gem:\n' \
                         f'```{offer["selling"]["asset_issuer"]}```\n'
    else:
        asset_issuers += f':coin: XLM :coin: \n' \
                         f'```Native Currency```'

    offer_details.add_field(name=f':bank: Asset Issuers :bank:',
                            value=asset_issuers,
                            inline=False)

    offer_details.add_field(name=f':sunrise: Horizon Links :sunrise:',
                            value=f'[Offer Maker]({offer["_links"]["offer_maker"]["href"]}) \n'
                                  f'[Offer Link]({offer["_links"]["self"]["href"]})',
                            inline=False)

    await destination.send(embed=offer_details)


async def send_payments_details(destination, record, action_name):
    """
    Send payment details on query to user
    """
    ledger_record = Embed(title=f':bookmark_tabs: {action_name} :bookmark_tabs: ',
                          colour=Colour.dark_orange())
    ledger_record.add_field(name=f':calendar: Date and time :calendar: ',
                            value=f'`{record["created_at"]}`')
    ledger_record.add_field(name=CONST_PAG,
                            value=f'`{record["paging_token"]}`')
    ledger_record.add_field(name=f':map: Source account :map:',
                            value=f'```{record["source_account"]}```',
                            inline=False)
    ledger_record.add_field(name=':cowboy:  Recipient :cowboy:  ',
                            value=f'```{record["to"]}```',
                            inline=False)
    ledger_record.add_field(name=CONST_HASH,
                            value=f'`{record["transaction_hash"]}`',
                            inline=False)
    ledger_record.add_field(name=':moneybag:  Amount :moneybag:  ',
                            value=f'`{record["amount"]} {record["asset_type"]}`',
                            inline=False)
    ledger_record.add_field(name=f':person_running: Ledger Activity :person_running: ',
                            value=f'[Transactions]({record["_links"]["transaction"]["href"]})\n'
                                  f'[Effects]({record["_links"]["effects"]["href"]})\n'
                                  f'[Succeeds]({record["_links"]["succeeds"]["href"]})\n'
                                  f'[Precedes]({record["_links"]["precedes"]["href"]})')
    await destination.send(embed=ledger_record)


async def send_trades_basic_details(destination, trades_enpoint: str, query_details: dict, hrz_link: str):
    address_details = Embed(title=f':currency_exchange: Trades for {trades_enpoint.capitalize()} :currency_exchange:',
                            colour=Colour.lighter_gray())
    address_details.add_field(name=query_details["by"],
                              value=f'```{query_details["query"]}```',
                              inline=False)
    address_details.add_field(name=f':sunrise: Horizon Link :sunrise:',
                              value=f'[Trades for Account]({hrz_link})',
                              inline=False)
    address_details.add_field(name=f':three: Last 3 trades for Account :three:',
                              value=f':arrow_double_down:',
                              inline=False)
    await destination.send(embed=address_details)


async def send_trades_details(destination, trade_data: dict):
    """
    Send Messages for Trades
    """
    if trade_data["base_asset_type"] != 'native':
        base_asset = f"{trade_data['base_asset_code']}"
        base_issuer = f'{trade_data["base_asset_issuer"]}'
    else:
        base_asset = 'XLM'
        base_issuer = f'Stellar'

    if trade_data["counter_asset_type"] != 'native':
        counter_asset = f"{trade_data['counter_asset_code']}"
        counter_issuer = f'{trade_data["counter_asset_issuer"]}'
    else:
        counter_asset = 'XLM'
        counter_issuer = f'Stellar'

    trade_report = Embed(title=f':id: {trade_data["id"]}',
                         description=f'__**Base seller**__: {trade_data["base_is_seller"]}',
                         colour=Colour.lighter_gray())
    trade_report.add_field(name=f':calendar: Close Time :calendar: ',
                           value=f'`{trade_data["ledger_close_time"]}`')
    trade_report.add_field(name=f':white_circle: Paging Token :white_circle:',
                           value=f'`{trade_data["paging_token"]}`')
    trade_report.add_field(name=f':map: Offer ID :map:',
                           value=f'`{trade_data["offer_id"]}`',
                           inline=True)
    trade_report.add_field(name=f':mag_right: Trade Details :mag_right:  ',
                           value=f'`{trade_data["base_amount"]} {base_asset}` :currency_exchange: '
                                 f'`{trade_data["counter_amount"]} {counter_asset}`',
                           inline=False)
    trade_report.add_field(name=f':men_wrestling: Parties :men_wrestling:',
                           value=f'Base:\n'
                                 f'```{trade_data["base_account"]}```\n'
                                 f'Counter:\n'
                                 f'```{trade_data["counter_account"]}```',
                           inline=False)
    trade_report.add_field(name=f':gem: Asset Details :gem:',
                           value=f':bank: **__ (Base) {base_asset} Issuer Details__** :bank:\n'
                                 f'```{base_issuer}```'
                                 f':bank: **__ (Counter) {counter_asset} Issuer Details__** :bank:\n'
                                 f'```{counter_issuer}```',
                           inline=False)
    trade_report.add_field(name=f':sunrise: Horizon Links :sunrise:',
                           value=f'[Base]({trade_data["_links"]["base"]["href"]})\n'
                                 f'[Counter]({trade_data["_links"]["counter"]["href"]})\n'
                                 f'[Operation]({trade_data["_links"]["operation"]["href"]})\n')
    await destination.send(embed=trade_report)


async def send_paths_entry_details(destination, details: dict):
    query_info = Embed(title=f':mag_right: Strict {details["type"]} Payment Search :mag:',
                       description='Bellow is information for 3 results returned from network',
                       colour=Colour.lighter_gray())
    query_info.add_field(name=f':map: {details["direction"]} Address :map:',
                         value=f'```{details["address"]}```',
                         inline=False)
    query_info.add_field(name=f':moneybag: Source Asset :moneybag: ',
                         value=f'`{details["amount"]} {details["asset"].upper()}`',
                         inline=False)
    query_info.add_field(name=f':bank: Issuer :bank:',
                         value=f'```{details["issuer"]}```',
                         inline=False)
    await destination.send(embed=query_info)


async def send_paths_records_details(destination, data):
    record_info = Embed(title=':record_button: Record Info :record_button: ',
                        colour=Colour.lighter_gray())
    record_info.add_field(name=f':gem: Source Asset :gem:',
                          value=f'`{data["source_asset_code"]}`',
                          inline=False)
    record_info.add_field(name=f':gem: Destination Asset :gem:',
                          value=f'`{data["destination_asset_code"]}`',
                          inline=False)
    record_info.add_field(name=f':money_with_wings:  Destination Amount :money_with_wings: ',
                          value=f'`{data["destination_amount"]} {data["destination_asset_code"]}`')

    counter = 0

    path_str = str()
    for p in data["path"]:
        if p["asset_type"] == 'native':
            path_str += f'***{counter}.*** `XLM`\n========\n'
        else:
            path_str += f'***{counter}.*** `{p["asset_code"]}`\n ```{p["asset_issuer"]}```========\n'
        counter += 1
    record_info.add_field(name=':railway_track: Paths :railway_track: ',
                          value=path_str,
                          inline=False)
    await destination.send(embed=record_info)


async def send_operations_basic_details(destination, key_query: str, hrz_link: str):
    effects_info = Embed(title=f':wrench: {key_query} Operations :wrench:  ',
                         description=f'Bellow are last three Operations which happened for {key_query}',
                         colour=Colour.lighter_gray())
    effects_info.add_field(name=f':sunrise: Horizon Access :sunrise: ',
                           value=f'[{key_query} Operations]({hrz_link})')
    effects_info.add_field(name=f':three: Last Three Effects :three: ',
                           value=f':arrow_double_down: ',
                           inline=False)
    await destination.send(embed=effects_info)
