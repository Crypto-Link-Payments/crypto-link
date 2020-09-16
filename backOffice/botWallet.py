"""
Script to handle bot off chain wallet and bot fees
"""

import os
import sys
from pymongo import MongoClient, errors
from utils.tools import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

helper = Helpers()
d = helper.read_json_file(file_name='botSetup.json')


class BotManager(object):
    def __init__(self):
        self.connection = MongoClient(d['database']['connection'], maxPoolSize=20)
        self.botStuff = self.connection['CryptoLink']
        self.botWallet = self.botStuff.CLWallets
        self.botFees = self.botStuff.CLFees

    def update_lpi_wallet_balance(self, amount: int, wallet: str, direction: int):
        """
        manipulating wallet balance when transactions happens
        """
        if direction == 1:
            pass

        else:
            amount *= (-1)

        try:
            result = self.botWallet.update_one({"ticker": f"{wallet}"},
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
        query = list(self.botWallet.find({},
                                         {"_id": 0}))
        return query

    def get_bot_wallet_balance_by_ticker(self, ticker):
        query = self.botWallet.find_one({"ticker": ticker},
                                        {"_id": 0,
                                         "balance": 1})
        return query['balance']

    def create_new_fee(self, type: str, value: float):
        """
        Insert New fee into database. Not integrated but used when updatin project manually
        """
        fee_struct = {
            "type": type,
            "key": type,
            "fee": value,

        }
        try:
            self.botFees.insert_one(fee_struct)
            return True
        except errors.PyMongoError:
            return False

    def license_fee_handling(self, fee: float, key: str):
        """
        Function used to update licensing fees
        :param fee: Flot number in $
        :param key: Key to search from which fee to update
        :return:
        """
        try:
            self.botFees.update_one({"key": key},
                                    {"$set": {"fee": fee},
                                     "$currentDate": {"lastModified": True}})
            return True
        except errors.PyMongoError:
            return False

    def get_fees_by_category(self, all: int = None, key: str = None):
        """
        Return details on the fees from database
        :param all:
        :param key:
        :return:
        """
        if all:
            data = list(self.botFees.find({}))
            return data
        else:
            data = self.botFees.find_one({"key": key},
                                         {"_id": 0})
            return data
