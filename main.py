"""
Main bot file to bring it online... Run it
"""

from colorama import Fore, init
import logging
from DiscordBot import DiscordBot
from backOffice.backOffice import BackOffice
from PeriodicTasks import PeriodicTasks, start_scheduler
from MerchantTasks import MerchantTasks, start_merchant_scheduler
from utils.tools import Helpers
from pprint import pprint
init(autoreset=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    helper = Helpers()
    bot_settings = helper.read_json_file(file_name='botSetup.json')
    backoffice = BackOffice(bot_settings)

    # Check file system
    backend_check = Fore.GREEN + '+++++++++++++++++++++++++++++++++++++++\n' \
                                 '          Checking backend....        \n'
    backoffice.check_backend()
    bot = DiscordBot(backoffice=backoffice, bot_settings=bot_settings)

    # Activate periodic tasks
    periodic_tasks = PeriodicTasks(backoffice, bot, main_net=bot_settings["mainNet"])
    scheduler = start_scheduler(periodic_tasks)
    #
    # Activate merchant tasks
    merchant_tasks = MerchantTasks(backoffice, bot)
    merchant_scheduler = start_merchant_scheduler(merchant_tasks)

    # Discord Token
    bot.run()
    print("DONE")
