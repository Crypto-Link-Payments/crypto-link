from pymongo import MongoClient

from utils.tools import Helpers

from backOffice.backendCheck import BotStructureCheck
from backOffice.stellarOnChainHandler import StellarWallet
from backOffice.merchatManager import MerchantManager
from backOffice.stellarActivityManager import StellarManager
from backOffice.statsManager import StatsManager
from backOffice.userWalletManager import UserWalletManager
from backOffice.guildServicesManager import GuildProfileManager

class BackOffice:
    def __init__(self):
        helper = Helpers()
        bot_data = helper.read_json_file(file_name='botSetup.json')
        self.connection = MongoClient(bot_data['database']['connection'], maxPoolSize=20)
        self.backend_check = BotStructureCheck(self.connection)
        self.stellar_wallet = StellarWallet()
        #self.merchant_manager = MerchantManager(self.connection) # not yet, because the constructor is called at other places
        #self.stellar_manager = StellarManager(self.connection)# idem
        self.merchant_manager = MerchantManager()
        self.stellar_manager = StellarManager()
        self.stats_manager = StatsManager()
        self.wallet_manager = UserWalletManager()
        self.guild_profiles = GuildProfileManager()


    def check_backend(self):
        self.backend_check.check_collections()
        self.backend_check.checking_stats_documents()
        self.backend_check.checking_bot_wallets()

