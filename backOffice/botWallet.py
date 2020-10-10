import os
import sys

from utils.tools import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class BotManager:
    """Class dealing with the management of Crypto Link own bot wallet and fees management"""

    def __init__(self, connection):
        """Connection to Database and Crypto Link collections"""
        self.connection = connection
        self.bot_stuff = self.connection['CryptoLink']
        self.bot_wallet = self.bot_stuff.CLWallets
        self.bot_fees = self.bot_stuff.CLFees

    def update_lpi_wallet_balance_multi(self, fees_data: dict, token: str = None):
        xlm_data = fees_data["xlm"]
        token_data = fees_data[f'{token}']
        xlm_result = self.bot_wallet.update_one({"ticker": f"xlm"},
                                                {"$inc": {"balance": xlm_data["balance"]}})
        token_result = self.bot_wallet.update_one({"ticker": f"{token}"},
                                                  {"$inc": {"balance": token_data["balance"]}})
        count_modifications = (int(xlm_result.modified_count) + int(token_result.modified_count))
        return count_modifications == 2

    def update_lpi_wallet_balance(self, ticker: str, to_update: dict):
        """
        manipulating wallet balance when transactions happens
        """

        result = self.bot_wallet.update_one({"ticker": f"{ticker}"},
                                            {"$inc": to_update})
        return result.modified_count > 0

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
                                          {"$set": data_to_update})
        return result.modified_count > 0

    def get_fees_by_category(self, key: str ):
        """
        Return details on the fees from database
        :param key: Key names
        :return:
        """
        data = self.bot_fees.find_one({"key": key},
                                          {"_id": 0})
        return data

    def get_all_fees(self):
        """
        Return details on all the fees from database
        """
        data = list(self.bot_fees.find({}))
        return data
