from pycoingecko import CoinGeckoAPI

gecko = CoinGeckoAPI()


def convert_to_currency(amount, coin_name):
    """
    Converts the amount to specific currency
    """
    try:
        data = gecko.get_price(ids=coin_name, vs_currencies='usd')
        if coin_name == 'stellar':
            usd_stellar = data['stellar']['usd']
            conversion_to_xlm = amount / usd_stellar
            xlm_to_stroops = int(conversion_to_xlm * (10 ** 7))
            details = {
                "usd": usd_stellar,
                "total": xlm_to_stroops
            }
            return details
    except Exception:
        return {"error", "Some error with api"}


def get_rates(coin_name):
    """
    Getting rates for Stellar
    """
    try:
        data = gecko.get_price(ids=coin_name, vs_currencies='usd,eur,rub,btc,eth,ltc')
        return data
    except Exception:
        return {}


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
