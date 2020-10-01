import os
import sys

from pymongo import MongoClient, errors

from utils.tools import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

helper = Helpers()
d = helper.read_json_file(file_name='botSetup.json')


class BotManager:
    """Class dealing with the management of Crypto Link own bot wallet and fees management"""

    def __init__(self):
        """Connection to Database and Crypto Link collections"""
        self.connection = MongoClient(d['database']['connection'], maxPoolSize=20)
        self.bot_stuff = self.connection['CryptoLink']
        self.bot_wallet = self.bot_stuff.CLWallets
        self.bot_fees = self.bot_stuff.CLFees

    def update_lpi_wallet_balance(self, amount: int, wallet: str, direction: int):
        """
        manipulating wallet balance when transactions happens
        """
        if direction != 1:
            amount *= (-1)

        try:
            result = self.bot_wallet.update_one({"ticker": f"{wallet}"},
                                                {"$inc": {"balance": int(amount)},
                                                 "$currentDate": {"lastModified": True}})
            return result.matched_count > 0
        except errors.PyMongoError as e:
            print(e)
            return False

    def get_bot_wallets_balance(self):
        """
        Obtain Crypto link off chain wallet balance
        """
        query = list(self.bot_wallet.find({},
                                          {"_id": 0}))
        return query

    def get_bot_wallet_balance_by_ticker(self, ticker):
        query = self.bot_wallet.find_one({"ticker": ticker},
                                         {"_id": 0,
                                          "balance": 1})
        return query['balance']

    def manage_fees_and_limits(self, key: str, data_to_update: dict):

        result = self.bot_fees.update_one({"key": key},
                                          {"$set": data_to_update,
                                           "$currentDate": {"lastModified": True}})
        return result.modified_count > 0

    def get_fees_by_category(self, all_fees: bool, key: str = None):
        """
        Return details on the fees from database
        :param all_fees: boolean True if all keys returned
        :param key: Key names
        :return:
        """
        if all_fees:
            data = list(self.bot_fees.find({}))
        else:
            data = self.bot_fees.find_one({"key": key},
                                          {"_id": 0})
        return data
