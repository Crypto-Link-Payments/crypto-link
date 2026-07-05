"""
Main bot file to bring it online... Run it
"""

from colorama import Fore, init
import logging

from dotenv import load_dotenv

from DiscordBot import DiscordBot
from backOffice.backOffice import BackOffice
from PeriodicTasks import PeriodicTasks, start_scheduler
from MerchantTasks import MerchantTasks, start_merchant_scheduler
from utils.tools import Helpers
from utils.notifications import NtfyNotifier


init(autoreset=True)
load_dotenv()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    notifier = NtfyNotifier.from_env()

    helper = Helpers()
    bot_settings = helper.read_json_file(file_name='botSetup.json')
    backoffice = BackOffice(bot_settings)

    backend_check = Fore.GREEN + '+++++++++++++++++++++++++++++++++++++++\n' \
                                 '          Checking backend....        \n'

    try:
        backoffice.check_backend()
    except Exception as e:
        notifier.send_exception(e, context="Backend check failed")
        raise

    bot = DiscordBot(backoffice=backoffice, bot_settings=bot_settings)

    # Attach notifier to bot so cogs can use it
    bot.notifier = notifier

    print("DONE")

    periodic_tasks = PeriodicTasks(backoffice, bot, main_net=bot_settings["mainNet"])
    scheduler = start_scheduler(periodic_tasks)

    merchant_tasks = MerchantTasks(backoffice, bot)
    merchant_scheduler = start_merchant_scheduler(merchant_tasks)

    async def start_schedulers_when_ready():
        if getattr(bot, "_schedulers_started", False):
            return

        bot._schedulers_started = True

        scheduler.start()
        merchant_scheduler.start()

        print(Fore.LIGHTBLUE_EX + "Schedulers started after Discord bot ready")

        await notifier.send_async(
            title="CryptoLink bot",
            message="Discord bot is online and schedulers started.",
            priority="high",
            tags=["computer"],
        )

    bot.add_listener(start_schedulers_when_ready, "on_ready")

    try:
        notifier.safe_send(
            title="CryptoLink bot",
            message="Bot process is starting.",
            priority="default",
            tags=["computer"],
        )

        bot.run()

    except Exception as e:
        notifier.send_exception(e, context="Bot crashed")
        raise

    finally:
        notifier.safe_send(
            title="CryptoLink bot",
            message="Bot process exited.",
            priority="high",
            tags=["warning"],
        )

        print("Exited...")