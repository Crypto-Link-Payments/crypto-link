"""
Script to handle statistics of the bot
"""

import os
import sys

from pymongo import MongoClient

from utils.tools import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

helper = Helpers()
d = helper.read_json_file(file_name='botSetup.json')


class StatsManager(object):
    def __init__(self):
        # main db connection
        self.connection = MongoClient(d['database']['connection'])

        # Database of bot users
        self.clConnection = self.connection['CryptoLink']
        self.userProfiles = self.clConnection.userProfiles
        self.chainActivities = self.clConnection.CLOnChainStats
        self.offChainActivities = self.clConnection.CLOffChainStats

    def update_user_deposit_stats(self, user_id: int, amount: float, key: str):
        """Updates users deposit stats"""

        self.userProfiles.find_one_and_update({"userId": user_id},
                                              {"$inc": {f"{key}.depositsCount": 1,
                                                        f"{key}.totalDeposited": amount}})

    def update_user_withdrawal_stats(self, user_id, amount, key: str):
        """Updates users withdrawal stats"""
        self.userProfiles.find_one_and_update({"userId": user_id},
                                              {"$inc": {f"{key}.withdrawalsCount": 1,
                                                        f"{key}.totalWithdrawn": amount}})

    def update_bot_chain_stats(self, type_of: str, ticker: str, amount: float):
        """
        Update stats when on chain activity happens
        """

        if type_of == "deposit":
            self.chainActivities.update_one({"ticker": f"{ticker}"},
                                            {"$inc": {"depositCount": 1,
                                                      "depositAmount": round(float(amount), 7)},
                                             "$currentDate": {"lastModified": True}})
        elif type_of == "withdrawal":
            self.chainActivities.update_one({"ticker": f"{ticker}"},
                                            {"$inc": {"withdrawalCount": 1,
                                                      "withdrawnAmount": round(float(amount), 7)},
                                             "$currentDate": {"lastModified": True}})

    def update_public_tx_user_stats(self, direction, ):
        pass

    def update_private_tx_user_stats(self):
        pass

    def update_bot_off_chain_stats(self, ticker: str, tx_amount: int, xlm_amount: float, tx_type: str,
                                   usd_value: float):
        """
        update bot stats based on transaction type in the system
        """
        if tx_type == 'public':
            self.offChainActivities.update_one({"ticker": f"{ticker}"},
                                               {"$inc": {"totalTx": int(tx_amount),
                                                         "totalMoved": xlm_amount,
                                                         "totalPublicCount": 1,
                                                         "totalSpentUsd": usd_value,
                                                         "totalPublicMoved": xlm_amount},
                                                "$currentDate": {"lastModified": True}})

        elif tx_type == 'private':
            self.offChainActivities.update_one({"ticker": f"{ticker}"},
                                               {"$inc": {"totalTx": int(tx_amount),
                                                         "totalMoved": xlm_amount,
                                                         "totalPrivateCount": 1,
                                                         "totalSpentUsd": usd_value,
                                                         "totalPrivateMoved": xlm_amount},
                                                "$currentDate": {"lastModified": True}})

        elif tx_type == 'emoji':
            self.offChainActivities.update_one({"ticker": f"{ticker}"},
                                               {"$inc": {"totalTx": int(tx_amount),
                                                         "totalMoved": xlm_amount,
                                                         "totalSpentUsd": usd_value,
                                                         "totalEmojiTx": 1,
                                                         "totalEmojiMoved": xlm_amount},
                                                "$currentDate": {"lastModified": True}})
        elif tx_type == 'multiTx':
            self.offChainActivities.update_one({"ticker": f"{ticker}"},
                                               {"$inc": {"totalTx": int(tx_amount),
                                                         "totalMoved": xlm_amount,
                                                         "totalSpentUsd": usd_value,
                                                         "multiTxCount": 1,
                                                         "multiTxMoved": xlm_amount},
                                                "$currentDate": {"lastModified": True}})

        elif tx_type == 'rolePurchase':
            self.offChainActivities.update_one({"ticker": f"{ticker}"},
                                               {"$inc": {"totalTx": int(tx_amount),
                                                         "totalMoved": xlm_amount,
                                                         "totalSpentUsd": usd_value,
                                                         "rolePurchaseTxCount": 1,
                                                         "roleMoved": xlm_amount},
                                                "$currentDate": {"lastModified": True}})
