def scientific_conversion(value, decimals):
    """
    Converts from scientific notation to normal float
    :param value: scientific notation to be converted
    :param decimals: Amount of decimal places in scientific notation
    :return: formatted number as string
    """
    formatted = (f'%.{decimals}f' % value)
    return formatted

