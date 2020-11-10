from datetime import datetime


def format_date(date: str):
    dt_format = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    return dt_format
