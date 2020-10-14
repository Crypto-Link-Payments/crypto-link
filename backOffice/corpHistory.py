"""
Class handling the corporate wallet activities
"""
import os
import sys

from pymongo import errors

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class CorporateHistoryManager:
    """Class dealing with corporate withdrawal history"""

    def __init__(self, connection):
        self.connection = connection
        self.corp_activity = self.connection['CryptoLink']
        self.corp_withdrawals = self.corp_activity.CORPFromTransactions

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
            self.corp_withdrawals.insert_one(data)
            return True
        except errors.PyMongoError as e:
            print(e)
            return False
