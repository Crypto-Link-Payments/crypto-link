def convert_list_to_string(values: list):
    """
    converts list to string
    :param values:
    :return:
    """
    values = list(filter(None, values))
    if len(values) > 0:
        return '\n'.join(x.strip() for x in values if x.strip())
    else:
        return 'No Data'


def convert_value_if_empty(value):
    """
    Converts value if empty
    :param value:
    :return:
    """
    if value:
        return value
    else:
        return "No Data"
