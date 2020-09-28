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
CONST_CURRENT_DATE = '$currentDate'


class BotStatsManager(object):
    """
    Class handling bot statistics
    """

    def __init__(self):
        self.connection = MongoClient(d['database']['connection'], maxPoolSize=20)
        self.bot_stuff = self.connection['CryptoLink']
        self.chain_activities = self.bot_stuff.CLOnChainStats
        self.off_chain_activities = self.bot_stuff.CLOffChainStats

    def get_all_stats(self):
        """
        Get all bot stats on request
        """
        off_chain_xlm = self.off_chain_activities.find_one({"ticker": "xlm"},
                                                           {"_id": 0})
        on_chain_xlm = self.chain_activities.find_one({"ticker": "xlm"},
                                                      {"_id": 0})

        data = {"xlm": {"ofChain": off_chain_xlm,
                        "onChain": on_chain_xlm}}

        return data
