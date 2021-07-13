import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class UserWalletManager:
    """
    Manages Stellar on chain activities
    """

    def __init__(self, connection, as_connection):
        self.connection = connection
        self.as_connection = as_connection
        self.crypto_link = self.connection['CryptoLink']

        self.user_wallets = self.crypto_link.userWallets
        # Collections connections async
        self.as_cl_connection = self.as_connection['CryptoLink']
        self.as_user_profiles = self.as_cl_connection.userProfiles  # Connection to user profiles
        self.as_user_wallets = self.as_cl_connection.userWallets  # Connection to user profiles

    def get_discord_id_from_memo(self, memo: str):
        result = self.user_wallets.find_one({"depositId": memo},
                                            {"_id": 0,
                                             "userId": 1})
        return int(result["userId"])

    def update_coin_balance_by_memo(self, memo: str, coin: str, amount: int):
        result = self.user_wallets.update_one({"depositId": memo},
                                              {"$inc": {f"{coin.lower()}": int(amount)}})
        return result.modified_count > 0

    def update_user_balance_off_chain(self, user_id, coin_details: dict):
        result = self.user_wallets.update_one({"userId": user_id},
                                              {"$inc": coin_details})
        return result.modified_count > 0

    def update_coin_balance(self, coin, user_id: int, amount: int, direction: int):
        if direction == 1:  # Append
            pass
        else:
            amount *= (-1)  # Deduct

        result = self.user_wallets.update_one({"userId": user_id},
                                              {"$inc": {f"{coin}": amount}})
        return result.modified_count > 0

    def get_ticker_balance(self, asset_code, user_id: int):
        result = self.user_wallets.find_one({"userId": user_id},
                                            {"_id": 0,
                                             f"{asset_code}": 1})
        if result:
            return result[f"{asset_code}"]
        else:
            return None

    def get_balances(self, user_id: int):
        """
        Get balances of all wallets
        """
        result = self.user_wallets.find_one({"userId": user_id},
                                            {"_id": 0,
                                             "depositId": 0,
                                             "userId": 0,
                                             "userName": 0})
        return result

    def get_full_details(self, user_id: int):
        """
        Get balances of all wallets
        """
        result = self.user_wallets.find_one({"userId": user_id},
                                            {"_id": 0})
        return result


