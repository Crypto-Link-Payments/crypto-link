"""
Script initiated at start to check if all collections in mongodb exist
"""

import os
import sys

from pymongo import MongoClient
from colorama import Fore, init

from utils.tools import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

init(autoreset=True)
helper = Helpers()
d = helper.read_json_file(file_name='botSetup.json')


class BotStrucutreCheck(object):
    def __init__(self):
        self.connection = MongoClient(d['database']['connection'], maxPoolSize=20)
        self.cryptoLink = self.connection["CryptoLink"]  #

        self.required_collections = ["CLOnChainStats",
                                     "CLOffChainStats",
                                     "CLWallets",
                                     "CLFees",
                                     "CORPFromTransactions",
                                     "MerchantCommunityProfile",
                                     "StellarCommunityWallets",
                                     "UserWallets"
                                     "MerchantMonetizedRoles",
                                     "MerchantAppliedUsers",
                                     "MerchantPurchasedLicenses",
                                     "StellarWallets",
                                     "StellarDeposits",
                                     "StellarWithdrawals",
                                     "StellarUnprocessedDeposits",
                                     "StellarUnprocessedWithdrawals",
                                     "StellarCorporateWallets"]

    def check_collections(self):
        """
        Check all required collections
        """
        # Check collections for bot stats
        bot_collections = self.cryptoLink.list_collection_names()
        print(Fore.GREEN + "1. Checking collection for BOT STATS")
        for collection in self.required_collections:
            if collection not in bot_collections:
                self.cryptoLink.create_collection(name=collection)
                print(Fore.YELLOW + f"{collection.upper()} has been created!")
            else:
                print(Fore.GREEN + f'{collection.upper()} already exists')
        print(Fore.LIGHTGREEN_EX + "====DONE====")

    def checking_stats_documents(self):
        """
        Checking document for statistical entry
        """
        # Connection to collections
        self.on_chain = self.cryptoLink.CLOnChainStats
        self.off_chain = self.cryptoLink.CLOffChainStats

        stats_on_chain = len(list(self.on_chain.find()))
        stats_off_chain = len(list(self.on_chain.find()))
        print(Fore.LIGHTBLUE_EX + "=====Checking STATS backend===")
        if stats_on_chain == 0:
            print(Fore.YELLOW + "MAKING ON CHAIN DOCUMENT ENTRY")
            stellarChain = {
                "ticker": "xlm",
                "depositCount": int(0),
                "withdrawalCount": int(0),
                "depositAmount": int(0),
                "withdrawalAmount": int(0)
            }

            self.on_chain.insert_one(stellarChain)
            print(Fore.GREEN + "DONE")
        else:
            print(Fore.LIGHTGREEN_EX + "XLM ON CHAIN OK")
        print('+++++++++++++++++++++++++++++++++++++++++++++++++')
        if stats_off_chain == 0:
            print(Fore.YELLOW + "MAKING OFF CHAIN DOCUMENT ENTRY")
            stellarOfChain = {
                "ticker": "xlm",
                "transactionCount": int(0),
                "offChainMoved": int(0)
            }
            self.off_chain.insert_one(stellarOfChain)
            print(Fore.GREEN + "DONE")
        else:
            print(Fore.LIGHTGREEN_EX + "XLM OFF CHAIN OK")

    def checking_bot_wallets(self):
        """
        Check if bot wallets exists and if not than create them
        """
        self.BotWallets = self.cryptoLink.CLWallets
        self.BotFees = self.cryptoLink.CLFees

        botWallets = len(list((self.BotWallets.find({}))))
        botFees = len(list(self.BotFees.find()))
        print(Fore.LIGHTBLUE_EX + "=====Checking BOT OFF CHAIN WALLET AND BOT FEES DOCUMENT======")

        if botWallets == 0:
            print(Fore.YELLOW + "MAKING BOT OFF CHAIN WALLET")
            mylist = [
                {"ticker": "xlm", "balance": 0}
            ]
            self.BotWallets.insert_many(mylist)
            print(Fore.GREEN + "DONE")
        else:
            print(Fore.LIGHTGREEN_EX + "BOT OFF CHAIN XLM WALLET OK ")

        if botFees == 0:
            print(Fore.YELLOW + "MAKING FEE STRUCTURE DOCS")
            mylist = [
                {"type": "with_xlm", "key": 'xlm', 'fee': float(1.0)},
                {"type": "merch_transfer_cost", "key": 'wallet_transfer', 'fee': float(1.0)},
                {"type": "merch_license", "key": 'license', 'fee': float(1.0)},
                {"type": "merch_transfer_min", "key": 'merchant_min', 'fee': float(1.0)}]

            self.BotFees.insert_many(mylist)
            print(Fore.GREEN + "DONE")
        else:
            print(Fore.LIGHTGREEN_EX + "BOT FEE SETTINGS EXIST ALREADY ")
