import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class CustodialWalletManager:
    """Class dealing with the Layer two wallets"""

    def __init__(self, connection):
        """Connection to Database and Crypto Link collections"""
        self.connection = connection
        self.bot_stuff = self.connection['CryptoLink']
        self.hotWallets = self.bot_stuff.userHotWallets

    def second_level_user_reg_status(self, user_id: int):
        """
        Check user registration status
        """
        data = self.hotWallets.find_one({"userId": int(user_id)})
        if data:
            return True
        else:
            return False

    def create_user_wallet(self, data_to_store:dict):
        """
        Creates the user hot wallet into the database. Decryption happens in COGS
        """
        result = self.hotWallets.insert_one(data_to_store)

        if result.inserted_id:
            return True
        else:
            return False

    def get_account_details(self, user_id: int):
        """
        Get user hot wallet details for decription in cogs
        """
        data = self.hotWallets.find_one({"userId": int(user_id)},
                                        {"_id": 0})
        if data:
            return data
        else:
            return {}

    def get_custodial_hot_wallet_addr(self, user_id: int):
        """
        Get user hot wallet details for decription in cogs
        """
        data = self.hotWallets.find_one({"userId": int(user_id)},
                                        {"_id": 0,
                                         "publicAddress": 1})
        if data:
            return data["publicAddress"]
        else:
            return {}
