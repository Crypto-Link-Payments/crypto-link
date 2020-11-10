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

