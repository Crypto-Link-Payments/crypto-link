
from backOffice.backendCheck import BotStructureCheck
from pymongo import MongoClient
from utils.tools import Helpers


class BackOffice:
    def __init__(self):
        helper = Helpers()
        bot_data = helper.read_json_file(file_name='botSetup.json')
        connection = MongoClient(bot_data['database']['connection'], maxPoolSize=20)
        self.backend_check = BotStructureCheck(connection)

    def check_backend(self):
        self.backend_check.check_collections()
        self.backend_check.checking_stats_documents()
        self.backend_check.checking_bot_wallets()

