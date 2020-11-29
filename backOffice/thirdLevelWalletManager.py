import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class ThirdLevelWalletManager:
    """Class dealing with the level three walets"""

    def __init__(self, connection):
        """Connection to Database and Crypto Link collections"""
        self.connection = connection
        self.bot_stuff = self.connection['CryptoLink']
        self.third_level = self.bot_stuff.ThirdLevelWallets

    def third_level_user_reg_status(self, user_id: int):
        """
        Check user registration status
        """
        data = self.third_level.find_one({"userId": int(user_id)})
        if data:
            return True
        else:
            return False

    def register_rd_level_wallet(self, data_to_store: dict):
        """
        Creates the user hot wallet into the database. Decryption happens in COGS
        """
        result = self.third_level.insert_one(data_to_store)

        if result.inserted_id:
            return True
        else:
            return False

    def update_public_address(self, user_id: int, pub_address: str):
        result = self.third_level.update_one({"userId": int(user_id)},
                                             {"$set": {"publicAddress": pub_address}})
        return result.modified_count > 0

    def get_third_account_details(self, user_id: int):
        """
        Get user hot wallet details for decription in cogs
        """
        data = self.third_level.find_one({"userId": int(user_id)},
                                         {"_id": 0})
        if data:
            return data
        else:
            return {}

    def get_third_hot_wallet_addr(self, user_id: int):
        """
        Get user hot wallet details for decription in cogs
        """
        data = self.third_level.find_one({"userId": int(user_id)},
                                         {"_id": 0,
                                          "publicAddress": 1})
        if data:
            return data["publicAddress"]
        else:
            return {}

    def remove_account(self, user_id: int):

        result = self.third_level.delete_one({"userId": int(user_id)})

        return result.deleted_count > 0
