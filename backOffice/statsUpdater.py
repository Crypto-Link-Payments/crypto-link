"""
Script to handle statistics of the bot
"""

import os
import sys

from pymongo import MongoClient
from pprint import pprint
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

    def update_user_deposit_stats(self, user_id:int, amount:float):
        """Updates users deposit stats"""
        self.userProfiles.find_one_and_update({"userId": user_id},
                                              {"$inc": {"xlmStats.depositsCountXlm": 1,
                                                        "xlmStats.totalDepositedXlm":amount}})

    def update_user_withdrawal_stats(self, user_id, amount):
        """Updates users withdrawal stats"""
        self.userProfiles.find_one_and_update({"userId": user_id},
                                              {"$inc": {"xlmStats.withdrawalsCountXlm": 1,
                                                        "xlmStats.totalWithdrawnXlm": amount}})



