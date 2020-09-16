
def scientific_conversion(value, decimals):
    """
    Converts from scientific notation to normal float
    :param value: Scintific notation to be converted
    :param decimals: Amount of decimal places in scientific notation
    :return: Formated number as string
    """
    formatted = (f'%.{decimals}f' % value)
    return formatted