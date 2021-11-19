from pymongo import MongoClient
import motor.motor_asyncio

from utils.tools import Helpers

from backOffice.backendCheck import BotStructureCheck
from backOffice.stellarOnChainHandler import StellarWallet
from backOffice.merchantManager import MerchantManager
from backOffice.stellarActivityManager import StellarManager
from backOffice.statsManager import StatsManager
from backOffice.userWalletManager import UserWalletManager
from backOffice.guildServicesManager import GuildProfileManager
from backOffice.profileRegistrations import AccountManager
from backOffice.botWallet import BotManager
from backOffice.corpHistory import CorporateHistoryManager
from backOffice.secondLevelWalletManager import SecondLevelWalletManager
from backOffice.thirdLevelWalletManager import ThirdLevelWalletManager
from backOffice.tokenManager import TokenManager
from backOffice.votingPoolManager import VotingPoolManager


class BackOffice:
    def __init__(self, bot_settings: dict):
        self.helper = Helpers()
        self.auto_messaging_channels = self.helper.read_json_file(file_name='autoMessagingChannels.json')
        self.connection = MongoClient(bot_settings['database']['connection'], maxPoolSize=20)
        self.as_connection = motor.motor_asyncio.AsyncIOMotorClient(bot_settings['database']['connection'])
        self.twitter_details = bot_settings["twitter"]
        self.creator_id = bot_settings["creator"]
        self.backend_check = BotStructureCheck(self.connection)
        self.second_level_manager = SecondLevelWalletManager(self.connection)
        self.third_level_manager = ThirdLevelWalletManager(self.connection)
        self.stellar_wallet = StellarWallet(network_type=bot_settings["mainNet"])
        self.merchant_manager = MerchantManager(self.connection)
        self.stellar_manager = StellarManager(self.connection, self.as_connection)
        self.stats_manager = StatsManager(self.connection, self.as_connection)
        self.wallet_manager = UserWalletManager(self.connection, self.as_connection)
        self.guild_profiles = GuildProfileManager(self.connection, self.as_connection)
        self.account_mng = AccountManager(self.connection)
        self.bot_manager = BotManager(self.connection)
        self.corporate_hist_mng = CorporateHistoryManager(self.connection)
        self.token_manager = TokenManager(self.connection)
        self.voting_manager = VotingPoolManager(self.connection)

    def check_backend(self):
        self.backend_check.check_collections()
        self.backend_check.checking_stats_documents()
        self.backend_check.checking_bot_wallets()
        self.backend_check.check_xlm_integration()
