"""
Back end script: Used to manage merchant system, all users and roles
"""

import os
import sys

from bson.objectid import ObjectId
from pymongo import errors

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class MerchantManager:
    """
    Class handling Merchant system. Storing licenses, purchases, etc.
    """

    def __init__(self, connection):
        self.connection = connection
        self.communities = self.connection['CryptoLink']

        # Collection of community profiles
        self.community_profiles = self.communities.MerchantCommunityProfile

        # Collection of stellar community wallets
        self.community_stellar_wallets = self.communities.StellarCommunityWallets

        # Collection of monetized roles per each community
        self.monetized_roles = self.communities.MerchantMonetizedRoles

        # Collection of applied users in the system
        self.applied_users = self.communities.MerchantAppliedUsers


    def check_if_community_exist(self, community_id: int):
        """
        Check if community is registered into the system
        :param community_id: unique community ID provided by discord
        :return: boolean
        """
        result = self.community_profiles.find_one({"communityId": community_id})
        return result

    def register_role(self, new_role_data: dict):
        """
        Register community role into the system and make it available to be monetized
        """
        try:
            self.monetized_roles.insert_one(new_role_data)
            return True
        except errors.PyMongoError:
            return False

    def get_all_roles_community(self, community_id: int):
        """
        Returns all the roles in the system which were monetized by owner of the community
        :param community_id: unique community ID
        :return:
        """
        roles = list(self.monetized_roles.find({"communityId": community_id},
                                               {"_id": 0}))
        return roles

    def find_role_details(self, role_id: int):
        """
        Returns the information on specific role ID
        :param role_id: Unique role id
        :return: role details as dict, or empty dict
        """
        role_details = self.monetized_roles.find_one({"roleId": role_id})

        return role_details

    def register_community_wallet(self, community_id: int, community_owner_id: int, community_name: str):
        """
        Makes community wallets once owner of the community registers details
        :param community_id: discord community ID
        :param community_owner_id: discord community owner
        :param community_name: Discord Community name
        :return: boolean
        """
        # Data for registration entry
        community_details = {
            "communityId": int(community_id),
            "communityOwner": int(community_owner_id),
            "communityName": community_name
        }

        # DData for stellar community wallet
        stellar_community_wallet = {
            "communityId": int(community_id),
            "communityOwner": int(community_owner_id),
            "communityName": community_name,
            "balance": int(0),
            "overallGained": int(0),
            "rolesObtained": int(0)
        }

        try:
            self.community_profiles.insert_one(community_details)
            self.community_stellar_wallets.insert_one(stellar_community_wallet)
            return True
        except errors.PyMongoError:
            return False

    def get_wallet_balance(self, community_id: int):
        """
        Get merchant community wallet balances
        :param community_id: unique discord community ID
        :return: data on both wallets if exist or nothing
        """
        stellar_wallet = self.community_stellar_wallets.find_one({"communityId": community_id},
                                                                 {"_id": 0,
                                                                  "balance": 1})

        return stellar_wallet

    def modify_funds_in_community_merchant_wallet(self, community_id: int, amount: int, wallet_tick: str,
                                                  direction: int):
        """
        Transfers funds to community merchant wallet once user has payed for it
        :param community_id: Unique community ID
        :param amount: atomic amount as integer of any currency
        :param wallet_tick: ticker to cross-reference the wallet for update
        :param direction:
        :return: boolean
        """
        if direction != 0:
            amount = amount * (-1)

        if wallet_tick == 'xlm':
            try:
                self.community_stellar_wallets.update_one({"communityId": community_id},
                                                          {"$inc": {"balance": amount}})
                return True
            except errors.PyMongoError as e:
                print(e)
                return False
        else:
            print('Currency in community merchant wallet not found')
            return False

    def add_user_to_payed_roles(self, purchase_data: dict):
        """
        add users to the payed roles in the system
        :return: boolean
        """
        try:
            self.applied_users.insert_one(purchase_data)
            return True
        except errors.WriteConcernError:
            return False
        except errors.WriteError:
            return False

    def remove_monetized_role_from_system(self, role_id, community_id):
        """
        Removes the monetized roles from the system if they get deleted
        :param role_id:
        :param community_id:
        :return:
        """
        result = self.monetized_roles.delete_one({"roleId": role_id, "communityId": community_id})

        return result.deleted_count == 1

    def remove_all_monetized_roles(self, guild_id):
        try:
            self.monetized_roles.delete_many({"communityId": guild_id})
            return True
        except errors.PyMongoError:
            return False

    def check_user_roles(self, user_id, discord_id):
        """
        return roles which user has obtained on the community
        :param user_id:
        :param discord_id:
        :return:
        """
        applied_roles = list(self.applied_users.find({'userId': user_id, "communityId": discord_id},
                                                     {"_id": 0}))

        return applied_roles

    def get_over_due_users(self, timestamp: int):
        """
        Returns all users who's role is overdue based on the timestamp
        :param timestamp: unix time stamp
        :return:
        """
        all_users = list(self.applied_users.find({"end": {"$lt": timestamp}}))
        return all_users

    def remove_overdue_user_role(self, community_id, user_id, role_id):
        """
        Remove user from the active role database upon expiration
        :param community_id:
        :param user_id:
        :param role_id:
        :return:
        """
        result = self.applied_users.delete_one({"communityId": community_id, "userId": user_id, "roleId": role_id})

        if result.deleted_count == 1:
            return True
        else:
            return False

    def change_role_details(self, role_data):
        """
        Change the role ID based pn object ID
        :param role_data:
        :return:
        """
        result = self.monetized_roles.update_one({'_id': ObjectId(role_data['_id'])},
                                                 {"$set": role_data})
        return result.modified_count > 0

    def delete_user_from_applied(self, community_id: int, user_id: int):
        """
        Removing user from database of active purchased roles as he/she does not exist anymore
        """
        result = self.applied_users.delete_many({"communityId": community_id, "userId": user_id})
        return result.deleted_count > 0

    def delete_all_users_with_role_id(self, community_id: int, role_id: int):
        """
        Delete all entries under active roles in database if community does not have that role anymore.
        """
        try:
            self.applied_users.delete_many({"communityId": community_id, "roleId": role_id})
            return True
        except errors.PyMongoError:
            return False

    def bulk_user_clear(self, community_id, role_id):
        """
        Delete all users who have applied for the role however owner of the community has delete the role from the
        system and is not available anymore. Function used to keep database in check
        :param community_id:
        :param role_id:
        :return:
        """
        result = self.applied_users.delete_many({"communityId": community_id, "roleId": role_id})
        return result.deleted_count > 0

    def get_balance_based_on_ticker(self, community_id, ticker):
        """
        Return guild balance based on guild's ID
        """

        if ticker == 'xlm':
            stellar_wallet = self.community_stellar_wallets.find_one({"communityId": community_id},
                                                                     {"_id": 0,
                                                                      "balance": 1})
            return stellar_wallet['balance']

        else:
            return None
