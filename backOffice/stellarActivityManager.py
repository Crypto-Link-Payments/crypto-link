"""
Class StellarManager is designed to handle off-chain and on-chain activities and store data
into history
"""

import os
import sys

from pymongo import MongoClient, errors

from utils.tools import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

helper = Helpers()
hot = helper.read_json_file(file_name='hotWallets.json')
d = helper.read_json_file(file_name='botSetup.json')


class StellarManager:
    """
    Manages Stellar on chain activities
    """

    def __init__(self):
        self.xlmHotWallet = hot['xlm']
        self.connection = MongoClient(d['database']['connection'], maxPoolSize=20)
        self.stellarCoin = self.connection['CryptoLink']

        # Collections connections
        self.stellarWallets = self.stellarCoin.StellarWallets  # Access to all stellar wallets
        self.stellarDeposits = self.stellarCoin.StellarDeposits  # Access to history of successfull deposits
        self.stellarWithdrawals = self.stellarCoin.StellarWithdrawals  # Access to history of successfull withdrawals
        self.stellarUnprocessedDep = self.stellarCoin.StellarUnprocessedDeposits  # Accaes to history of unsuccessfull deposits
        self.stellarUnprocessedWith = self.stellarCoin.StellarUnprocessedWithdrawals  # Access to history of unprocessed withdrawals
        self.stellarCorpWallets = self.stellarCoin.StellarCorporateWallets

    def stellar_deposit_history(self, deposit_type: int, tx_data):
        """
        Managing history of deposits
        :param deposit_type: Deposit based on if MEMO is found or not. 1=found , 2= not found
        :param tx_data: dictionary of data from TX to be stored on deposit
        :return:
        """
        if deposit_type == 1:
            result = self.stellarDeposits.insert_one(tx_data)
        elif deposit_type == 2:
            result = self.stellarUnprocessedDep.insert_one(tx_data)

        if result.inserted_id:
            return True
        else:
            return False

    def stellar_withdrawal_history(self, tx_type: int, tx_data: dict):
        """
        Managing history off withdrawals

        :param tx_type:
        :param tx_data:
        :return:
        """
        if tx_type == 1:  # IF Successfull
            result = self.stellarWithdrawals.insert_one(tx_data)
        elif tx_type == 2:  # IF error
            result = self.stellarUnprocessedWith.insert_one(tx_data)

        if result.inserted_id:
            return True
        else:
            return False

    def check_if_stellar_memo_exists(self, tx_memo):
        """
        Check if deposit payment ID exists in the system
        :param tx_memo: Deposit payment ID for Stellar Wallet
        :return: boolean
        """

        result = self.stellarWallets.find_one({"depositId": tx_memo})

        if result:
            return True
        else:
            return False

    def check_if_deposit_hash_processed_succ_deposits(self, tx_hash):
        """
        Function which checks if HASH has been already processed
        """
        result = self.stellarDeposits.find_one({"hash": tx_hash})

        if result:
            return True
        else:
            return False

    def check_if_deposit_hash_processed_unprocessed_deposits(self, tx_hash):
        """
        Check if hash is stored in unprocessed deposits
        """
        result = self.stellarUnprocessedDep.find_one({"hash": tx_hash})

        if result:
            return True
        else:
            return False

    def get_stellar_wallet_data_by_discord_id(self, discord_id: int):
        """
        Get users wallet details by unique Discord id.
        """
        result = self.stellarWallets.find_one({"userId": discord_id},
                                              {"_id": 0})
        if result:
            return result
        else:
            return {}

    def update_stellar_balance_by_memo(self, memo, stroops: int, direction: int):
        """
        Updates the balance based on stellar memo with stroops
        :param memo: Deposit payment id
        :param stroops: minimal stellar unit stroop as int
        :param direction: updating stellar balance based on memo. if 1 = append otherwise deduct
        :return:
        """
        if direction == 1:  # Append
            pass
        else:
            stroops *= (-1)  # Deduct

        try:
            result = self.stellarWallets.update_one({"depositId": memo},
                                                    {'$inc': {"balance": stroops},
                                                     "$currentDate": {"lastModified": True}})

            return result.matched_count > 0
        except errors.PyMongoError as e:
            print(f'Could not update balance by memo: {e}')
            return False

    def update_stellar_balance_by_discord_id(self, discord_id: int, stroops: int, direction: int):
        """
        Updates the balance based on discord id  with stroops
        :param discord_id: Unique Discord id
        :param stroops: micro unit of stellar chain
        :param direction: updating stellar balance based on memo. if 1 = append otherwise deduct
        :return:
        """
        if direction == 1:  # Append
            pass
        else:
            stroops *= (-1)  # Deduct

        try:
            result = self.stellarWallets.update_one({"userId": discord_id},
                                                    {'$inc': {"balance": int(stroops)},
                                                     "$currentDate": {"lastModified": True}})

            return result.matched_count > 0
        except errors.PyMongoError as e:
            print(e)
            return False

    def get_discord_id_from_deposit_id(self, deposit_id):
        """
        Query unique users discord if based on deposit_id / memo
        """
        result = self.stellarWallets.find_one({"depositId": deposit_id})
        return result
