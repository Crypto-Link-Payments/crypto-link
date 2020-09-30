"""
Class handling the corporate wallet activities
"""
import os
import sys

from pymongo import MongoClient
import motor.motor_asyncio

from utils.tools import Helpers

helper = Helpers()
d = helper.read_json_file(file_name='botSetup.json')

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class GuildProfileManager:
    """Class managing guild profiles"""

    def __init__(self):
        self.connection = MongoClient(d['database']['connection'], maxPoolSize=20)
        self.cl_db_access = self.connection['CryptoLink']
        self.guild_profiles = self.cl_db_access.guildProfiles

        self.as_connection = motor.motor_asyncio.AsyncIOMotorClient(d['database']['connection'])
        self.as_cl_db_access = self.as_connection['CryptoLink']
        self.as_guild_profiles = self.as_cl_db_access.guildProfiles  # Connection to user profiles

    def check_guild_registration_stats(self, guild_id: int):
        result = list(self.guild_profiles.find({"guildId": guild_id}))
        return result

    async def register_guild(self, guild_data: dict):
        result = self.as_guild_profiles.insert_one(guild_data)
        return result

    def get_all_explorer_applied_channels(self):
        result = [guild["explorerSettings"]["channelId"] for guild in
                  self.guild_profiles.find({}, {"_id": 0, "explorerSettings.channelId": 1}) if
                  guild["explorerSettings"]["channelId"] > 0]
        return result

    async def get_guild_stats(self, guild_id: int):
        stats = await self.as_guild_profiles.find_one({"guildId": guild_id},
                                                      {"_id": 0,
                                                       "xlm": 1,
                                                       "clt": 1})
        return stats

    async def update_guild_profile(self, guild_id, data_to_update: dict):
        result = await self.as_guild_profiles.update_one({"guildId": guild_id},
                                                         {"$set": data_to_update})
        return result.modified_count > 0

    async def get_service_statuses(self, guild_id: int):
        return await self.as_guild_profiles.find_one({"guildId": guild_id},
                                                     {"_id": 0,
                                                      "explorerSettings": 1,
                                                      "txFees": 1})
