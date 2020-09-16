"""
Script to handle statistics of the bot
"""

import os
import sys
from pymongo import MongoClient, errors
from utils.tools import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

helper = Helpers()
d = helper.read_json_file(file_name='botSetup.json')


class BotStatsManager(object):
    def __init__(self):
        self.connection = MongoClient(d['database']['connection'], maxPoolSize=20)
        self.botStuff = self.connection['CryptoLink']
        self.chainActivities = self.botStuff.CLOnChainStats
        self.offChainActivities = self.botStuff.CLOffChainStats

    def update_chain_activity_stats(self, type_of: str, ticker: str, amount: int):
        """
        Update stats when on chain activity happens
        """
        try:
            if ticker == 'stellar':
                if type_of == "deposit":
                    self.chainActivities.update_one({"ticker": "xlm"},
                                                    {"$inc": {"depositCount": 1,
                                                              "depositAmount": amount},
                                                     "$currentDate": {"lastModified": True}})
                elif type_of == "withdrawal":
                    self.chainActivities.update_one({"ticker": "xlm"},
                                                    {"$inc": {"withdrawalCount": 1,
                                                              "withdrawalAmount": amount},
                                                     "$currentDate": {"lastModified": True}})
            return True
        except errors.PyMongoError:
            return False

    def update_off_chain_activity_stats(self, ticker: str, amount: int):

        """
        Update off chain activity when off fchain happens
        """
        try:
            if ticker == 'stellar':
                self.offChainActivities.update_one({"ticker": "xlm"},
                                                   {"$inc": {"transactionCount": 1,
                                                             "offChainMoved": amount},
                                                    "$currentDate": {"lastModified": True}})
            return True
        except errors.PyMongoError:
            return False

    def get_all_stats(self):
        """
        Get all bot stats on request
        """
        off_chain_xlm = self.offChainActivities.find_one({"ticker": "xlm"},
                                                        {"_id": 0})
        on_chain_xlm = self.chainActivities.find_one({"ticker": "xlm"},
                                                      {"_id": 0})

        data = {"xlm": {"ofChain": off_chain_xlm,
                        "onChain": on_chain_xlm}}

        return data
