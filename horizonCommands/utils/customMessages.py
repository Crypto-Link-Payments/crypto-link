from discord import Embed, Colour


async def account_create_msg(destination, details):
    new_account = Embed(title=f':new: Stellar Testnet Account Created :new:',
                        description=f'You have successfully created new account on {details["network"]}. Do'
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
                                f' Discord. Exposure of Secret to any other entity or 3rd party application '
                                f'might result in loss of funds. Crypto Link does not store details of newly'
                                f' generate accounts nor can recover them.',
                          inline=False)
    await destination.send(embed=new_account, delete_after=360)


async def send_details_for_stellar(destination, coin, data, date, signers):
    acc_details = Embed(title=':mag_right: Details for Stellar Account :mag:',
                        description=f'Last Activity {date} (UTC)',
                        colour=Colour.lighter_gray())
    acc_details.add_field(name=':map: Account Address :map: ',
                          value=f'```{data["account_id"]}```',
                          inline=False)
    acc_details.add_field(name=':pen_fountain: Account Signers :pen_fountain: ',
                          value=signers,
                          inline=False)
    acc_details.add_field(name=' :genie: Sponsorship Activity :genie:',
                          value=f':money_mouth: {data["num_sponsored"]} (sponsored)\n'
                                f':money_with_wings: {data["num_sponsoring"]} (sponsoring) ',
                          inline=False)
    acc_details.add_field(name=f' :moneybag: Balance :moneybag:',
                          value=f'`{coin["balance"]} XLM`',
                          inline=False)
    acc_details.add_field(name=f':man_judge: Liabilities :man_judge: ',
                          value=f'Buying Liabilities: {coin["buying_liabilities"]}\n'
                                f'Selling Liabilities: {coin["selling_liabilities"]}',
                          inline=False)
    acc_details.add_field(name=f':triangular_flag_on_post: Flags :triangular_flag_on_post:',
                          value=f'Auth Required: {data["flags"]["auth_required"]}\n'
                                f'Auth Revocable: {data["flags"]["auth_revocable"]}\n'
                                f'Auth Immutable:{data["flags"]["auth_immutable"]}')
    await destination.send(embed=acc_details)


async def send_details_for_asset(destination, coin, data, date):
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


async def send_asset_details(destination, data, request, ):
    toml_access = data['_embedded']['records'][0]['_links']['toml']['href']
    record = data['_embedded']['records'][0]

    asset_info = Embed(title=f':bank: Issuer Details :bank:',
                       description=f'Bellow is represent information for requested {request}.',
                       colour=Colour.lighter_gray())
    asset_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                         value=f'[Horizon]({data["_links"]["self"]["href"]})')

    if not toml_access:
        toml_data = None
        toml_link = ''
    else:
        toml_data = "Access link"
        toml_link = toml_access

    asset_info = Embed(title=" :bank: __Issuer Details__ :bank:",
                       description=f'TOML access: [{toml_data}]({toml_link})',
                       colour=Colour.lighter_gray())
    asset_info.add_field(name=f':regional_indicator_c: Asset Code :regional_indicator_c:',
                         value=f'{record["asset_code"]}',
                         inline=False)
    asset_info.add_field(name=f':gem: Asset Type :gem:',
                         value=f'{record["asset_type"]}',
                         inline=False)
    asset_info.add_field(name=f':map: Issuing Account :map: ',
                         value=f'```{record["asset_issuer"]}```',
                         inline=False)
    asset_info.add_field(name=f':moneybag: Issued Amount :moneybag: ',
                         value=f'`{record["amount"]} {record["asset_code"]}`',
                         inline=False)
    asset_info.add_field(name=f':cowboy: Account Count :cowboy: ',
                         value=f'`{record["num_accounts"]}`',
                         inline=False)
    asset_info.add_field(name=f':triangular_flag_on_post: Account Flags :triangular_flag_on_post: ',
                         value=f'Immutable: {record["flags"]["auth_immutable"]} \n'
                               f'Required:  {record["flags"]["auth_required"]}\n'
                               f'Revocable:  {record["flags"]["auth_revocable"]}\n',
                         inline=False)
    asset_info.add_field(name=f':white_circle: Paging Token :white_circle:',
                         value=f'```{record["paging_token"]}```',
                         inline=False)
    await destination.send(embed=asset_info)


async def send_multi_asset_case(destination, data, command_str):
    records = data['_embedded']['records']

    asset_info = Embed(title=f':gem: Multiple Assets Found :gem: ',
                       description=f'Please use `{command_str}assets issuer <issuer address >` to'
                                   f' obtain full details',
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
