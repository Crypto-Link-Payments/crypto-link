from stellar_sdk import Account
from stellar_sdk.exceptions import Ed25519PublicKeyInvalidError


def check_stellar_address(address):
    """
    Filter for withdrawals
    """
    try:
        Account(account_id=address, sequence=0)
        return True

    except Ed25519PublicKeyInvalidError:
        return False
