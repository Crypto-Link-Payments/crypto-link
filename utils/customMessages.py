from discord import Embed, Colour
from datetime import datetime
from cogs.utils.monetaryConversions import scientific_conversion, get_rates, rate_converter


async def user_account_info(ctx, data, bot_avatar_url):
    """
    Send user account details from network for Layer 2
    """
    signers = " ".join(
        [f':map:`{signer["key"]}`\n:key:`{signer["type"]}` | :scales:`{signer["weight"]}`\n================' for
         signer in data["signers"]])
    dt_format = datetime.strptime(data["last_modified_time"], '%Y-%m-%dT%H:%M:%SZ')
    account_info = Embed(title=f':office_worker: Current On-Chain Wallet State :office_worker:',
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
            await ctx.author.send(embed=gems_nfo)


async def dev_fee_option_notification(destination):
    """
    Prompt user if he is willing to give dev fee
    """
    dev_fee_info = Embed(title=":robot: Optional Dev Fee for Crypto Link Team:robot: ",
                         color=Colour.lighter_gray())
    dev_fee_info.add_field(name=f':money_with_wings: Dev fee :money_with_wings: ',
                           value=f'If you would like to support us in what we are doing please answer with'
                                 f'***__Yes__*** and system will ask you for custom amount you are willing to donate'
                                 f' for Crypto Link development..'
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
