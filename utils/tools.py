import json
import os
import sys
from stellar_sdk import TextMemo, Account, Keypair
from stellar_sdk.exceptions import MemoInvalidException, Ed25519PublicKeyInvalidError, Ed25519SecretSeedInvalidError

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class Helpers:
    """Class including helper functions"""

    def __init__(self):
        """
        initiate a object Helper
        """
        pass

    @staticmethod
    def read_json_file(file_name: str):
        """
        Loads the last block height which was stored in last_block.json
        :return: Block height as INT
        """

        # Reads last marked block data in the document
        path = f'{project_path}/{file_name}'
        try:
            with open(path) as json_file:
                data = json.load(json_file)
                return data
        except IOError:
            return None

    def update_json_file(self, file_name: str, key, value):
        """
        Updates Json file based on file name key and value
        """
        try:
            # read data
            data = self.read_json_file(file_name)
            data[key] = value
            path = f'{project_path}/{file_name}'
            with open(path, 'w') as f:
                json.dump(data, f)
            return True
        except FileExistsError as e:
            print(e)
            return False

    @staticmethod
    def check_memo(memo):
        try:
            TextMemo(text=memo)
            return True
        except MemoInvalidException:
            return False

    @staticmethod
    def check_public_key(address: str):
        try:
            Account(account_id=address, sequence=0)
            return True
        except Ed25519PublicKeyInvalidError:
            return False

    @staticmethod
    def check_private_key(private_key: str):
        """
        Check if private key constructed matches criteria
        """
        try:
            Keypair.from_secret(private_key)
            return True
        except Ed25519SecretSeedInvalidError:
            return False
