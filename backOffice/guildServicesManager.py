"""
Class handling the corporate wallet activities
"""
import os
import sys

from pymongo import MongoClient
from pymongo import errors
import motor.motor_asyncio

from utils.tools import Helpers

helper = Helpers()
d = helper.read_json_file(file_name='botSetup.json')

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)


class GuildServices:
    """Class managing guild profiles"""

    def __init__(self):
        self.connection = MongoClient(d['database']['connection'], maxPoolSize=20)
        self.guild_activity = self.connection['CryptoLink']
        self.guild_services = self.guild_activity.guildServices

        self.as_connection = motor.motor_asyncio.AsyncIOMotorClient(d['database']['connection'])
        self.as_guild_services = self.as_connection.guildServices  # Connection to user profiles

    async def register_guild(self, guild_data: dict):
        result = await self.as_guild_services.insert_one(guild_data)
        return result.id

    async def get_all_explorer_applied_channels(self):
        result = [guild for guild in self.as_guild_services.find({}, {"explorerChannel"}) if
                  guild["explorerChannel"] > 0]
        return result
