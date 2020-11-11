from datetime import datetime
from stellar_sdk import Asset


def format_date(date: str):
    dt_format = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    return dt_format


def get_emoji(title):
    if title == 'ledger':
        return ':ledger:'
    elif title == 'Transaction Hash':
        return ':hash:'
    elif title == "account":
        return ':map:'


def process_memo(record: dict):
    """Filter memo"""
    if record.get('memo'):
        memo = f'{record["memo"]} (Type: {record["memo_type"]})'
    else:
        memo = None

    return memo


def get_asset(asset_code, asset_issuer):
    if asset_code.upper() != 'XLM':
        destination_asset = Asset(code=asset_code.upper(), issuer=asset_issuer)
    else:
        destination_asset = Asset(code='XLM').native()

    return destination_asset
