"""
Script to handle statistics of the bot
"""

import os
import sys
from pymongo import errors, DESCENDING

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

CONST_INC = '$inc'


class StatsManager(object):
    """
    Class handling Crypto Link statistics
    """

    def __init__(self, connection, as_connectin):
        # main db connection
        self.connection = connection
        self.as_connection = as_connectin

        # Database of bot users
        self.cl_connection = self.connection['CryptoLink']
        self.user_profiles = self.cl_connection.userProfiles
        self.chain_activities = self.cl_connection.CLOnChainStats
        self.off_chain_activities = self.cl_connection.CLOffChainStats

        # Async support
        self.as_cl_connection = self.as_connection['CryptoLink']
        self.as_user_profiles = self.as_cl_connection.userProfiles  # Connection to user profiles
        self.as_cl_off_chain_stats = self.as_cl_connection.CLOffChainStats  # Connection to CL Off chain stats
        self.as_on_chain_activities = self.as_cl_connection.CLOnChainStats
        self.as_cl_guild_profiles = self.as_cl_connection.guildProfiles
        self.as_cl_earnings = self.as_cl_connection.CLEarning
        self.as_user_wallets = self.as_cl_connection.userWallets

    async def create_bridge(self, user_id: int):
        """
        Increase user stats on bridges
        """
        await self.as_user_profiles.update_one({"userId": user_id},
                                               {f"{CONST_INC}": {"bridges": 1}})

    async def count_total_registered_wallets(self):
        """
        Return count of registered wallets
        """
        data = await self.as_user_wallets.count_documents({})
        return data

    async def update_cl_earnings(self, time, amount: int, system: str, token: str, user: str,user_id:int):
        """
        Appends fee to CL wallet level 1
        """

        result = await self.as_cl_earnings.insert_one({"time": time, "system": system,
                                                       "amount": amount,
                                                       "token": token,
                                                       "user": user,
                                                       "userId":user_id})
        if result.inserted_id:
            return True
        else:
            return False

    async def update_cl_merchant_stats(self, ticker: str, merchant_stats: dict, ticker_stats: dict):
        await self.as_cl_off_chain_stats.update_one({"ticker": ticker},
                                                    {f"{CONST_INC}": ticker_stats})

        await self.as_cl_off_chain_stats.update_one({"ticker": "merchant"},
                                                    {f"{CONST_INC}": merchant_stats})

    async def update_cl_off_chain_stats(self, ticker: str, ticker_stats: dict):
        """
        Updating crypto link transaction stats
        """
        await self.as_cl_off_chain_stats.update_one({"ticker": ticker},
                                                    {f"{CONST_INC}": ticker_stats})

    async def update_cl_on_chain_stats(self, ticker: str, stat_details: dict):
        """
        Update stats when on chain activity happens.
        """
        try:
            result = await self.as_on_chain_activities.update_one({"ticker": ticker},
                                                                  {f"$inc": stat_details})
            return result.matched_count > 0
        except errors.PyMongoError:
            return False

    async def update_user_on_chain_stats(self, user_id: int, stats_data: dict):
        """
        Updates users deposit stats.
        """
        await self.as_user_profiles.find_one_and_update({"userId": user_id},
                                                        {"$inc": stats_data})

    async def update_usr_tx_stats(self, user_id: int, tx_stats_data: dict):

        try:
            result = await self.as_user_profiles.update_one({"userId": user_id},
                                                            {f"{CONST_INC}": tx_stats_data})
            return result.matched_count > 0
        except errors.PyMongoError:
            return False

    async def as_update_role_purchase_stats(self, user_id: int, merchant_data: dict):
        await self.as_user_profiles.update_one({"userId": user_id},
                                               {f"{CONST_INC}": merchant_data})

    async def update_guild_stats(self, guild_id: int, guild_stats_data: dict):
        await self.as_cl_guild_profiles.update_one({"guildId": guild_id},
                                                   {f"{CONST_INC}": guild_stats_data})

    async def update_registered_users(self, guild_id: int):
        await self.as_cl_guild_profiles.update_one({"guildId": guild_id},
                                                   {f"{CONST_INC}": {"registeredUsers": 1}})

    def get_all_stats(self):
        """
        Get all bot stats on request
        """
        off_chain_xlm = self.off_chain_activities.find_one({"ticker": "xlm"},
                                                           {"_id": 0})
        on_chain_xlm = self.chain_activities.find_one({"ticker": "xlm"},
                                                      {"_id": 0})

        data = {"xlm": {"offChain": off_chain_xlm,
                        "onChain": on_chain_xlm}}

        return data

    def get_top_builders(self, limit:int):
        top_list = self.user_profiles.find({}).sort(
            "bridges", DESCENDING).limit(limit)
        return top_list

