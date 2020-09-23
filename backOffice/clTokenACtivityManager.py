"""
Class StellarManager is designed to handle off-chain and on-chain activities and store data
into history
"""

import os
import sys

from pymongo import MongoClient, errors

from utils.tools import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

helper = Helpers()
hot = helper.read_json_file(file_name='hotWallets.json')
d = helper.read_json_file(file_name='botSetup.json')


class ClTokenManager:
    """
    Handler for Crypto Link Custom Token built on Stellar Chain
    """

    def __init__(self):
        """
        Init for the class
        """
        self.xlmHotWallet = hot['xlm']
        self.connection = MongoClient(d['database']['connection'], maxPoolSize=20)
        self.clConnection = self.connection['CryptoLink']

        # Collections connections
        self.clTokenWallets = self.clConnection.ClTokenWallets

    def get_cl_token_data_by_id(self, discord_id):
        """
        Get users wallet details by unique Discord id.
        """
        result = self.clTokenWallets.find_one({"userId": discord_id},
                                              {"_id": 0})
        if result:
            return result
        else:
            return {}

    def update_token_balance_by_id(self, discord_id: int, token_micro: int, append: bool):
        """
        Updates the balance based on discord id  with stroops
        :param discord_id: Unique Discord id
        :param token_micro: micro unit of crypto link token
        :param append: boolean True will append to user wallet, False deducts funds
        :return:
        """
        if append == 1:  # Append
            pass
        else:
            token_micro *= (-1)  # Deduct

        try:
            result = self.clTokenWallets.update_one({"userId": discord_id},
                                                    {'$inc': {"balance": int(token_micro)},
                                                     "$currentDate": {"lastModified": True}})

            return result.matched_count > 0
        except errors.PyMongoError as e:
            print(e)
            return False

    def get_discord_id_from_deposit_id(self, deposit_id):
        """
        Query unique users discord if based on deposit_id / memo
        """
        result = self.clTokenWallets.find_one({"depositId": deposit_id})
        return result
