from stellar_sdk import Account, Keypair
from stellar_sdk.exceptions import Ed25519PublicKeyInvalidError, Ed25519SecretSeedInvalidError


def check_stellar_address(address):
    """
    Filter for withdrawals
    """
    try:
        Account(account_id=address, sequence=0)
        return True

    except Ed25519PublicKeyInvalidError:
        return False


def check_stellar_private(private_key):
    try:
        user_key_pair = Keypair.from_secret(private_key)
        root_account = Account(account_id=user_key_pair.public_key, sequence=1)
        print(root_account)
        return True
    except Ed25519SecretSeedInvalidError as e:
        print(e)
        return False
