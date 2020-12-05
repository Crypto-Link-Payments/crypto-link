from pycoingecko import CoinGeckoAPI

gecko = CoinGeckoAPI()


def convert_to_currency(amount, coin_name):
    """
    Function which converts fro
    :param amount:
    :param coin_name:
    :return:
    """

    data = gecko.get_price(ids=coin_name, vs_currencies='usd,eur')
    details = dict()
    if coin_name == 'stellar':
        usd_stellar = data['stellar']['usd']
        eur_stellar = data['stellar']['eur']
        details = {
            "usd": usd_stellar,
            "total": round(float(amount / usd_stellar), 3),
            'eur': eur_stellar,
            'total_eur': round(float(amount / eur_stellar), 3)
        }
    return details


def get_rates(coin_name):
    """
    Getting rates for Stellar
    """
    data = gecko.get_price(ids=coin_name, vs_currencies='usd,eur,rub,btc,eth,ltc')
    return data


def convert_to_usd(amount, coin_name):
    """
    Function converts crypto value to $ and returns the per unit and total amount
    """
    try:
        data = gecko.get_price(ids=coin_name, vs_currencies='usd')
        details = dict()
        if coin_name == 'stellar':
            usd_stellar = data['stellar']['usd']
            details = {
                "usd": usd_stellar,
                "total": round(float(amount * usd_stellar), 6)

            }
        return details
    except Exception as e:
        details = {
            "usd": '0',
            "total": f"{e}"

        }
        return details

def get_normal(value, decimal_point: int):
    """
    Converts from minor to major
    """
    s = str(value)
    if len(s) < decimal_point + 1:
        # add some trailing zeros, if needed, to have constant width
        s = '0' * (decimal_point + 1 - len(s)) + s

    idx = len(s) - decimal_point

    s = s[0:idx] + "." + s[idx:]
    return s


def rate_converter(amount, rate):
    return round(float(amount * rate), 7)
