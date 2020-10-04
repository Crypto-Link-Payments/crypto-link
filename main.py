"""
Main bot file to bring it online... Run it
"""

from colorama import Fore, init

from DiscordBot import DiscordBot
from backOffice.backOffice import BackOffice
from PeriodicTasks import PeriodicTasks, start_scheduler

init(autoreset=True)


if __name__ == '__main__':
    backoffice = BackOffice()

    # Check file system
    backoffice.check_backend()
    backend_check = Fore.GREEN + '+++++++++++++++++++++++++++++++++++++++\n' \
                                 '          Checking backend....        \n'
    print(backend_check)

    bot = DiscordBot(backoffice)

    periodic_tasks = PeriodicTasks(backoffice, bot)

    scheduler = start_scheduler(periodic_tasks)
    # Discord Token
    bot.run()
    print("DONE")
