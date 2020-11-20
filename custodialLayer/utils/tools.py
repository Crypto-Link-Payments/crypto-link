from stellar_sdk import TextMemo, Account, Keypair
from stellar_sdk.exceptions import MemoInvalidException, Ed25519PublicKeyInvalidError, NotFoundError, BadRequestError, \
    BadResponseError, UnknownRequestError, Ed25519SecretSeedInvalidError


def check_memo(memo):
    try:
        TextMemo(text=memo)
        return True
    except MemoInvalidException:
        return False


def check_public_key(address: str):
    try:
        Account(account_id=address, sequence=0)
        return True
    except Ed25519PublicKeyInvalidError:
        return False


def check_private_key(private_key: str):
    """
    Check if private key constructed matches criteria
    """
    try:
        Keypair.from_secret(private_key)
        return True
    except Ed25519SecretSeedInvalidError:
        return False
    pass
