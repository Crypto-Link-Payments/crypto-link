"""
Used for converting crypto numbers to minimal units
"""

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
            'eur':eur_stellar,
            'total_eur':round(float(amount/eur_stellar),3)
        }
    return details

def get_rates(coin_name):
    """
    Getting rates for Stellar 
    """
    data = gecko.get_price(ids=coin_name, vs_currencies='usd,eur')
    return data


def convert_to_usd(amount, coin_name):
    """
    Function converts crypto value to $ and returns the per unit and total amount
    """

    data = gecko.get_price(ids=coin_name, vs_currencies='usd')
    details = dict()
    if coin_name == 'stellar':
        usd_stellar = data['stellar']['usd']
        details = {
            "usd": usd_stellar,
            "total": round(float(amount * usd_stellar), 6)

        }
    return details


def get_decimal_point(symbol):
    """
    Get decimal points based on symbol
    """
    if symbol == 'xlm':
        return 7


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


def get_in_micro(size, decimal_point: int):
    """
    Converts from major units to minor
    """
    str_amount = str(size)
    fraction_size = 0

    if '.' in str_amount:

        point_index = str_amount.index('.')

        fraction_size = len(str_amount) - point_index - 1

        while fraction_size < decimal_point and '0' == str_amount[-1]:
            str_amount = str_amount[:-1]
            fraction_size = fraction_size - 1

        if decimal_point < fraction_size:
            return False

        str_amount = str_amount[:point_index] + str_amount[point_index + 1:]

    if not str_amount:
        return False

    if fraction_size < decimal_point:
        str_amount = str_amount + '0' * (decimal_point - fraction_size)

    return str_amount


conversion = convert_to_currency(amount=1, coin_name='stellar')
print(conversion)