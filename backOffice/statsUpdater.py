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
CONST_CURRENT_DATE = '$currentDate'
CONST_INC = '$inc'


class StatsManager(object):
    """
    Class handling Crypto Link statistics
    """

    def __init__(self):
        # main db connection
        self.connection = MongoClient(d['database']['connection'])

        # Database of bot users
        self.cl_connection = self.connection['CryptoLink']
        self.user_profiles = self.cl_connection.user_profiles
        self.chain_activities = self.cl_connection.CLOnChainStats
        self.off_chain_activities = self.cl_connection.CLOffChainStats

    def update_user_deposit_stats(self, user_id: int, amount: float, key: str):
        """
        Updates users deposit stats
        """

        self.user_profiles.find_one_and_update({"userId": user_id},
                                               {"$inc": {f"{key}.depositsCount": 1,
                                                         f"{key}.totalDeposited": amount}})

    def update_user_withdrawal_stats(self, user_id, amount, key: str):
        """Updates users withdrawal stats"""
        self.user_profiles.find_one_and_update({"userId": user_id},
                                               {f"{CONST_INC}": {f"{key}.withdrawalsCount": 1,
                                                                 f"{key}.totalWithdrawn": amount}})

    def update_bot_chain_stats(self, type_of: str, ticker: str, amount: float):
        """
        Update stats when on chain activity happens
        """

        if type_of == "deposit":
            self.chain_activities.update_one({"ticker": f"{ticker}"},
                                             {f"{CONST_INC}": {"depositCount": 1,
                                                               "depositAmount": round(float(amount), 7)},
                                              f"{CONST_CURRENT_DATE}": {"lastModified": True}})
        elif type_of == "withdrawal":
            self.chain_activities.update_one({"ticker": f"{ticker}"},
                                             {f"{CONST_INC}": {"withdrawalCount": 1,
                                                               "withdrawnAmount": round(float(amount), 7)},
                                              f"{CONST_CURRENT_DATE}": {"lastModified": True}})

    def update_user_transaction_stats(self, user_id: int, key, amount: float, direction: str, tx_type: str,
                                      special: str = None, mined: float = None):

        data = dict()
        # Public or private and direction of funds
        if tx_type == 'public':
            data[f'{key}.publicTxCount'] = 1
            if direction == 'outgoing':
                data[f'{key}.publicSent'] = amount
            elif direction == 'incoming':
                data[f'{key}.publicReceived'] = amount

        elif tx_type == 'private':
            data[f'{key}.privateTxCount'] = 1
            if direction == 'outgoing':
                data[f'{key}.privateSent'] = amount
            elif direction == 'incoming':
                data[f'{key}.privateReceived'] = amount

        # incoming or outgoing
        if direction == 'incoming':
            data[f"transactionCounter.receivedCount"] = 1
            data[f"{key}.received"] = round(float(amount), 7)

        elif direction == 'outgoing':
            data[f"transactionCounter.sentTxCount"] = 1
            data[f"{key}.sent"] = round(float(amount), 7)

        # special or not
        if special:
            if special == 'emoji':
                data["transactionCounter.emojiTxCount"] = 1
            elif special == 'multiTx':
                data["transactionCounter.multiTxCount"] = 1
            elif special == 'rolePurchase':
                data["transactionCounter.rolePurchase"] = 1

        # Mined or not
        if mined and direction == 'outgoing':
            data[f"clCoinStats.mined"] = mined

        self.user_profiles.find_one_and_update({"userId": user_id}, {f"{CONST_INC}": data})

    def update_bot_off_chain_stats(self, ticker: str, tx_amount: int, xlm_amount: float, tx_type: str):
        """
        update bot stats based on transaction type in the system
        """
        if tx_type == 'public':
            self.off_chain_activities.update_one({"ticker": f"{ticker}"},
                                                 {f"{CONST_INC}": {"totalTx": int(tx_amount),
                                                                   "totalMoved": xlm_amount,
                                                                   "totalPublicCount": 1,
                                                                   "totalPublicMoved": xlm_amount},
                                                  f"{CONST_CURRENT_DATE}": {"lastModified": True}})

        elif tx_type == 'private':
            self.off_chain_activities.update_one({"ticker": f"{ticker}"},
                                                 {f"{CONST_INC}": {"totalTx": int(tx_amount),
                                                                   "totalMoved": xlm_amount,
                                                                   "totalPrivateCount": 1,
                                                                   "totalPrivateMoved": xlm_amount},
                                                  f"{CONST_CURRENT_DATE}": {"lastModified": True}})

        elif tx_type == 'emoji':
            self.off_chain_activities.update_one({"ticker": f"{ticker}"},
                                                 {f"{CONST_INC}": {"totalTx": int(tx_amount),
                                                                   "totalMoved": xlm_amount,
                                                                   "totalEmojiTx": 1,
                                                                   "totalEmojiMoved": xlm_amount},
                                                  f"{CONST_CURRENT_DATE}": {"lastModified": True}})
        elif tx_type == 'multiTx':
            self.off_chain_activities.update_one({"ticker": f"{ticker}"},
                                                 {f"{CONST_INC}": {"totalTx": int(tx_amount),
                                                                   "totalMoved": xlm_amount,
                                                                   "multiTxCount": 1,
                                                                   "multiTxMoved": xlm_amount},
                                                  f"{CONST_CURRENT_DATE}": {"lastModified": True}})

        elif tx_type == 'rolePurchase':
            self.off_chain_activities.update_one({"ticker": f"{ticker}"},
                                                 {f"{CONST_INC}": {"totalTx": int(tx_amount),
                                                                   "totalMoved": xlm_amount,
                                                                   "rolePurchaseTxCount": 1,
                                                                   "roleMoved": xlm_amount},
                                                  f"{CONST_CURRENT_DATE}": {"lastModified": True}})
