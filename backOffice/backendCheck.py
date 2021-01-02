"""
Script initiated at start to check if all collections in mongodb exist
"""

import os
import sys

from colorama import Fore, init

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

init(autoreset=True)


class BotStructureCheck(object):
    def __init__(self, connection):
        self.connection = connection
        self.crypto_link = self.connection["CryptoLink"]  #

        self.required_collections = ["CLOnChainStats",  # On chain statistics
                                     "CLOffChainStats",  # OFf chain statistics
                                     "CLEarning"
                                     "CLWallets",
                                     "CLFees",
                                     "CORPFromTransactions",
                                     "MerchantCommunityProfile",
                                     "StellarCommunityWallets",
                                     "userProfiles",
                                     "MerchantMonetizedRoles",
                                     "MerchantAppliedUsers",
                                     "userWallets",
                                     "StellarDeposits",
                                     "StellarWithdrawals",
                                     "StellarUnprocessedDeposits",
                                     "StellarUnprocessedWithdrawals",
                                     "guildProfiles",
                                     "userHotWallets",
                                     "thirdLevelWallets"]

    def check_collections(self):
        """
        Check all required collections
        """
        # Check collections for bot stats
        bot_collections = self.crypto_link.list_collection_names()
        print(Fore.GREEN + "1. Checking collections")
        for collection in self.required_collections:
            if collection not in bot_collections:
                self.crypto_link.create_collection(name=collection)
                print(Fore.YELLOW + f"{collection.upper()} has been created!")
            else:
                print(Fore.GREEN + f'{collection.upper()} already exists')
        print(Fore.LIGHTGREEN_EX + "====DONE====")

    def checking_stats_documents(self):
        """
        Checking document for statistical entry
        """
        # Connection to collections
        on_chain = self.crypto_link.CLOnChainStats
        off_chain = self.crypto_link.CLOffChainStats

        stats_on_chain = len(list(on_chain.find()))
        stats_off_chain = len(list(off_chain.find()))
        print(Fore.LIGHTBLUE_EX + "=====Checking STATS backend===")
        if stats_on_chain == 0:
            print(Fore.YELLOW + "MAKING ON CHAIN DOCUMENT ENTRY")
            global_stats = [{
                "ticker": "xlm",
                "depositCount": int(0),
                "withdrawalCount": int(0),
                "depositAmount": float(0.0),
                "withdrawnAmount": float(0.0)
            }, {
                "ticker": "clt",
                "depositCount": int(0),
                "withdrawalCount": int(0),
                "depositAmount": float(0.0),
                "withdrawnAmount": float(0.0)
            }]

            on_chain.insert_many(global_stats)
            print(Fore.GREEN + "DONE")
        else:
            print(Fore.LIGHTGREEN_EX + "XLM ON CHAIN OK")
        print('+++++++++++++++++++++++++++++++++++++++++++++++++')

        if stats_off_chain == 0:
            print(Fore.YELLOW + "MAKING OFF CHAIN DOCUMENT ENTRY")
            stats_off = [{
                "ticker": "xlm",
                "totalTx": int(0),
                "totalMoved": float(0.0),
                "totalPrivateCount": int(0),
                "totalPrivateMoved": float(0.0),
                "totalPublicCount": int(0),
                "totalPublicMoved": float(0.0),
                "totalEmojiTx": int(0),
                "totalEmojiMoved": float(0),
                "multiTxCount": int(0),
                "multiTxMoved": float(0.0),
                "merchantPurchases": int(0),
                "merchantMoved": float(0)
            }, {
                "ticker": "clt",
                "totalTx": int(0),
                "totalMoved": float(0.0),
                "totalPrivateCount": int(0),
                "totalPrivateMoved": float(0.0),
                "totalPublicCount": int(0),
                "totalPublicMoved": float(0.0),
                "totalEmojiTx": int(0),
                "totalEmojiMoved": float(0),
                "multiTxCount": int(0),
                "multiTxMoved": float(0.0),
                "merchantPurchases": int(0),
                "merchantMoved": float(0)
            }]

            off_chain.insert_many(stats_off)
            print(Fore.GREEN + "DONE")
        else:
            print(Fore.LIGHTGREEN_EX + "XLM OFF CHAIN OK")

    def checking_bot_wallets(self):
        """
        Check if bot wallets exists and if not than create them
        """
        bot_wallets = self.crypto_link.CLWallets
        bot_fees = self.crypto_link.CLFees

        count_bot_wallets = len(list((bot_wallets.find({}))))
        count_bot_fees = len(list(bot_fees.find()))
        print(Fore.LIGHTBLUE_EX + "=====Checking BOT OFF CHAIN WALLET AND BOT FEES DOCUMENT======")

        if count_bot_wallets == 0:
            print(Fore.YELLOW + "MAKING BOT OFF CHAIN WALLET")
            my_list = [
                {"ticker": "xlm", "balance": 0},
                {"ticker": "clt", "balance": 0}
            ]
            bot_wallets.insert_many(my_list)
            print(Fore.GREEN + "DONE")

        else:
            print(Fore.LIGHTGREEN_EX + "BOT OFF CHAIN XLM WALLET OK ")

        if count_bot_fees == 0:
            print(Fore.YELLOW + "MAKING FEE STRUCTURE DOCS")
            token_fees = {
                "xlm": float(1.0),
                'clt': float(1.0)
            }
            fee_list = [
                {"type": "withdrawal_fees", "key": 'withdrawals', 'fee_list': token_fees},
                {"type": "merch_transfer_cost", "key": 'wallet_transfer', 'fee': float(1.0)},
                {"type": "merch_license", "key": 'license', 'fee': float(1.0)},
                {"type": "merch_transfer_min", "key": 'merchant_min', 'fee': float(1.0)}]

            bot_fees.insert_many(fee_list)
            print(Fore.GREEN + "DONE")
        else:
            print(Fore.LIGHTGREEN_EX + "BOT FEE SETTINGS EXIST ALREADY ")
