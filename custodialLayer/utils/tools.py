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


def get_network_base_fee(self):
    """
    Get network fee and handle error if error
    """
    try:
        return self.server.fetch_base_fee()
    except ConnectionError:
        return 0.0000001
    except NotFoundError:
        return 0.0000001
    except BadRequestError:
        return 0.0000001
    except BadResponseError:
        return 0.0000001
    except UnknownRequestError:
        return 0.0000001
