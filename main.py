"""
Main bot file to bring it online... Run it
"""

import logging
import sys

from colorama import Fore, init
from dotenv import load_dotenv

from DiscordBot import DiscordBot
from backOffice.backOffice import BackOffice
from PeriodicTasks import PeriodicTasks, start_scheduler
from MerchantTasks import MerchantTasks, start_merchant_scheduler
from utils.tools import Helpers
from utils.ntfy_client import NtfyClient


init(autoreset=True)
load_dotenv()

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    notifier = NtfyClient.from_env()

    notifier.startup("CryptoLink bot process is starting.")

    helper = Helpers()

    try:
        bot_settings = helper.read_json_file(file_name="botSetup.json")
        backoffice = BackOffice(bot_settings)

        print(
            Fore.GREEN
            + "+++++++++++++++++++++++++++++++++++++++\n"
            + "          Checking backend....        \n"
            + "+++++++++++++++++++++++++++++++++++++++"
        )

        backoffice.check_backend()

        bot = DiscordBot(backoffice=backoffice, bot_settings=bot_settings)

        # Makes notifier available in cogs/tasks as self.bot.notifier
        bot.notifier = notifier

        periodic_tasks = PeriodicTasks(
            backoffice,
            bot,
            main_net=bot_settings["mainNet"],
        )
        scheduler = start_scheduler(periodic_tasks)

        merchant_tasks = MerchantTasks(backoffice, bot)
        merchant_scheduler = start_merchant_scheduler(merchant_tasks)

        async def start_schedulers_when_ready():
            if getattr(bot, "_schedulers_started", False):
                return

            bot._schedulers_started = True

            try:
                scheduler.start()
                merchant_scheduler.start()

                print(Fore.LIGHTBLUE_EX + "Schedulers started after Discord bot ready")

                await bot.notifier.safe_send_async(
                    title="CryptoLink bot",
                    message="Discord bot is online and schedulers started.",
                    priority="high",
                    tags=["computer", "white_check_mark"],
                    sequence_id="cryptolink-startup",
                )

            except Exception as e:
                logger.exception("Failed to start schedulers")

                await bot.notifier.send_exception_async(
                    e,
                    context="Schedulers failed to start after Discord bot became ready",
                )

                raise

        bot.add_listener(start_schedulers_when_ready, "on_ready")

        print(Fore.GREEN + "DONE")

        bot.run()

    except KeyboardInterrupt:
        logger.info("Bot stopped manually with KeyboardInterrupt")

        notifier.safe_send(
            title="CryptoLink bot",
            message="Bot was stopped manually.",
            priority="high",
            tags=["warning"],
        )

        sys.exit(0)

    except Exception as e:
        logger.exception("CryptoLink bot crashed")

        notifier.send_exception(
            e,
            context="CryptoLink bot crashed",
        )

        raise

    finally:
        notifier.shutdown("CryptoLink bot process exited.")
        print("Exited...")


if __name__ == "__main__":
    main()