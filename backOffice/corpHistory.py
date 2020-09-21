"""
Class handling the corporate wallet activities
"""
import os
import sys

import pymongo
from pymongo import MongoClient
from pymongo import errors

from utils.tools import Helpers

helper = Helpers()
d = helper.read_json_file(file_name='botSetup.json')

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class CorporateHistoryManager:
    def __init__(self):
        self.connection = MongoClient(d['database']['connection'], maxPoolSize=20)
        self.corporateActivity = self.connection['CryptoLink']
        self.fromCorpTransfers = self.corporateActivity.CORPFromTransactions

    def store_transfer_from_corp_wallet(self, time_utc, author, destination, amount_atomic, amount, currency):
        """
        Stores to history when transactions is done from corp wallet to certain user
        :param time_utc: utc unix timestamp
        :param author: author who initiates the transfer
        :param destination: destination to where funds were transferred
        :param amount_atomic: atomic number (for xlm is stroops)
        :param amount: amount
        :param currency: currency
        :return:
        """

        data = {
            "timestamp": int(time_utc),
            "authorId": int(author),
            "destinationId": int(destination),
            "currency": str(currency),
            "amount": str(amount),
            "amountAtomic": int(amount_atomic),

        }

        try:
            self.fromCorpTransfers.insert_one(data)
            return True
        except pymongo.errors.PyMongoError as e:
            print(e)
            return False
