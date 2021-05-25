"""
Main bot file to bring it online... Run it
"""

from colorama import Fore, init
import logging
from DiscordBot import DiscordBot
from backOffice.backOffice import BackOffice
from PeriodicTasks import PeriodicTasks, start_scheduler
from MerchantTasks import MerchantTasks, start_merchant_scheduler

init(autoreset=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    backoffice = BackOffice()

    # Check file system
    backoffice.check_backend()
    backend_check = Fore.GREEN + '+++++++++++++++++++++++++++++++++++++++\n' \
                                 '          Checking backend....        \n'
    print(backend_check)

    bot = DiscordBot(backoffice)

    # Activate periodic tasks
    periodic_tasks = PeriodicTasks(backoffice, bot)
    scheduler = start_scheduler(periodic_tasks)

    # Activate merchant tasks
    merchant_tasks = MerchantTasks(backoffice, bot)
    merchant_scheduler = start_merchant_scheduler(merchant_tasks)

    # Discord Token
    bot.run()
    print("DONE")
