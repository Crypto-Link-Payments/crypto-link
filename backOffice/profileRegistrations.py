"""
File responsible to deal with the database of users
"""

import os
import sys

from pymongo import MongoClient
from pymongo import errors

from backOffice.tools.helppersOffice import VariousTools
from utils.tools import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

helper = Helpers()
vt = VariousTools()
d = helper.read_json_file(file_name='botSetup.json')
hot = helper.read_json_file(file_name='hotWallets.json')


class AccountManager(object):
    def __init__(self):
        self.xlmHotWallet = hot['xlm']
        # main db connection
        self.connection = MongoClient(d['database']['connection'])

        # Database of bot users
        self.clConnection = self.connection['CryptoLink']
        self.userProfiles = self.clConnection.UserWallets

        # Stellar connection
        self.stellarWallets = self.clConnection.StellarWallets  # Access to all stellar wallets

    def __create_stellar_wallet(self, discord_id: int, discord_username: str, deposit_id):
        """
        Creates stellar wallet for the user
        :param discord_id:
        :param discord_username:
        :return:
        """
        stellar_wallet = {
            "userId": discord_id,
            "userName": discord_username,
            "depositId": deposit_id,
            "balance": int(0),
            'ClTokenBalance': int(0)
        }

        result = self.stellarWallets.insert_one(stellar_wallet)

        if result.inserted_id:
            return True
        else:
            return False

    def update_user_wallet_balance(self, discord_id: int, ticker: str, direction: int, amount: int):
        """
        Updating the user wallet balance used with merchant system
        """
        if direction == 0:
            pass
        else:
            amount = amount * (-1)

        if ticker == 'xlm':
            try:
                self.stellarWallets.update_one({"userId": int(discord_id)},
                                               {"$inc": {"balance": amount},
                                                "$currentDate": {"lastModified": True}})
                return True
            except errors.PyMongoError as e:
                print(f' Could not update user wallet with xlm: {e}')
                return False

    def register_user(self, discord_id: int, discord_username: str):
        """
        Registers user into the system
        :param discord_id: Discord Unique ID
        :param discord_username: Discord Current username
        :return: bool

        """
        stellar_deposit_id = vt.get_xlm_payment_id()

        self.__create_stellar_wallet(discord_id=discord_id, discord_username=discord_username,
                                     deposit_id=stellar_deposit_id)

        new_user = {
            "userId": discord_id,
            "userName": discord_username,
            "stellarDepositId": stellar_deposit_id,
            "transactionCounter": {"sentTxCount": int(0),
                                   "receivedCount": int(0),
                                   "multiTxCount": int(0),
                                   "emojiTxCount": int(0)},
            "xlmStats": {"depositsCountXlm": int(0),
                         "withdrawalsCountXlm": int(0),
                         "totalWithdrawnXlm": float(0.0),
                         "totalDepositedXlm": float(0.0),
                         'privateXlmTxCount': int(0),
                         'publicXlmTxCount': int(0),
                         "xlmReceived": float(0.0),
                         "xlmSent": float(0.0),
                         'spentOnRolesXlm': float(0.0)},
            "clCoinStats": {"depositsCountCl": int(0),
                            "withdrawalsCountCl": int(0),
                            "totalWithdrawnCl": int(0),
                            "totalDepositedCl": int(0),
                            'privateClTxCount': int(0),
                            'publicClTxCount': int(0),
                            'clMined': float(0.0),
                            "clReceived": float(0.0),
                            "clSent": float(0.0)},
            "membershipStats": {"rolePurchased": int(0),
                                'spentOnRolesUsd': float(0.0),
                                "spentOnRolesXlm": int(0),
                                "spentOnRolesCl": int(0)}
        }

        try:
            self.userProfiles.insert_one(new_user)
            return True
        except errors.PyMongoError:
            return False

    def check_user_existence(self, user_id: int):
        """
        Checks if the user is already registered into the system
        :param user_id: Discord unique ID
        :return: bool
        """

        result = self.userProfiles.find_one({"userId": user_id})

        if result:
            return True
        else:
            return False

    def get_user_profile(self, user_id: int):
        """
        Gets whole user profile data based on the ID
        :param user_id: Unique Discord ID
        :return: dictionary of data
        """
        result = self.userProfiles.find_one({"userId": user_id},
                                            {"_id": 0,
                                             "stellarDepositId": 1})

        if result:
            return result
        else:
            return []

    def get_wallet_balances_based_on_discord_id(self, discord_id: int):
        """
        Gets both wallets details based on discord id
        :param discord_id:
        :return:
        """
        stellar = self.stellarWallets.find_one({"userId": discord_id},
                                               {"_id": 0,
                                                "balance": 1,
                                                "depositId": 1})

        try:
            if stellar:
                values = {
                    "stellar": stellar,
                }

                return values
            else:
                return {}
        except errors.PyMongoError as e:
            print(e)
            return {}

    def get_balance_based_on_ticker(self, user_id, ticker):

        if ticker == 'xlm':
            stellar_wallet = self.stellarWallets.find_one({"userId": int(user_id)},
                                                          {"_id": 0,
                                                           "balance": 1})
            return stellar_wallet['balance']
