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


class BackOffice:
    def __init__(self):
        helper = Helpers()
        bot_data = helper.read_json_file(file_name='botSetup.json')
        self.connection = MongoClient(bot_data['database']['connection'], maxPoolSize=20)
        self.as_connection = motor.motor_asyncio.AsyncIOMotorClient(bot_data['database']['connection'])
        self.twitter_details = bot_data["twitter"]
        self.horizon_url = bot_data['horizonServer']

        self.backend_check = BotStructureCheck(self.connection)
        self.second_level_manager = SecondLevelWalletManager(self.connection)
        self.third_level_manager = ThirdLevelWalletManager(self.connection)
        self.stellar_wallet = StellarWallet(horizon_url=self.horizon_url)
        self.merchant_manager = MerchantManager(self.connection)
        self.stellar_manager = StellarManager(self.connection, self.as_connection)
        self.stats_manager = StatsManager(self.connection, self.as_connection)
        self.wallet_manager = UserWalletManager(self.connection, self.as_connection)
        self.guild_profiles = GuildProfileManager(self.connection, self.as_connection)
        self.account_mng = AccountManager(self.connection)
        self.bot_manager = BotManager(self.connection)
        self.corporate_hist_mng = CorporateHistoryManager(self.connection)

    def check_backend(self):
        self.backend_check.check_collections()
        self.backend_check.checking_stats_documents()
        self.backend_check.checking_bot_wallets()
