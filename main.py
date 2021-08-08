"""
Main bot file to bring it online... Run it
"""

from colorama import Fore, init
import logging
from discord import Status,Game
from DiscordBot import DiscordBot
from backOffice.backOffice import BackOffice
from PeriodicTasks import PeriodicTasks, start_scheduler
from MerchantTasks import MerchantTasks, start_merchant_scheduler
from utils.tools import Helpers
from discord_components import DiscordComponents
from pprint import pprint
init(autoreset=True)

logging.basicConfig(level=logging.INFO)
helper = Helpers()
bot_settings = helper.read_json_file(file_name='botSetup.json')
backoffice = BackOffice(bot_settings)

# Check file system
backend_check = Fore.GREEN + '+++++++++++++++++++++++++++++++++++++++\n' \
                             '          Checking backend....        \n'
backoffice.check_backend()
bot = DiscordBot(backoffice=backoffice, bot_settings=bot_settings)

# periodic_tasks = PeriodicTasks(backoffice, bot, main_net=bot_settings["mainNet"])
# scheduler = start_scheduler(periodic_tasks)
# #
# # Activate merchant tasks
# merchant_tasks = MerchantTasks(backoffice, bot)
# merchant_scheduler = start_merchant_scheduler(merchant_tasks)


@bot.event
async def on_ready():
    DiscordComponents(bot)
    for g in bot.guilds:
        check_guild_prefix = bot.backoffice.guild_profiles.check_guild_prefix(guild_id=int(g.id))
        if not check_guild_prefix:
            if bot.backoffice.guild_profiles.set_guild_prefix(guild_id=int(g.id), prefix="!"):
                print(Fore.YELLOW + f"Default prefix registered for {g}")
            else:
                print(Fore.RED + f"Could not register prefix for {g}")
        else:
            print(Fore.GREEN + f"{g} Prefix ....OK")

    await bot.change_presence(status=Status.online, activity=Game('Monitoring'))
    print(Fore.GREEN + 'DISCORD BOT : Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print('================================')

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    # helper = Helpers()
    # bot_settings = helper.read_json_file(file_name='botSetup.json')
    # backoffice = BackOffice(bot_settings)
    #
    # # Check file system
    # backend_check = Fore.GREEN + '+++++++++++++++++++++++++++++++++++++++\n' \
    #                              '          Checking backend....        \n'
    # backoffice.check_backend()
    # bot = DiscordBot(backoffice=backoffice, bot_settings=bot_settings)
    # bot.run()
    # print("DONE")

    # Activate periodic tasks
    # periodic_tasks = PeriodicTasks(backoffice, bot, main_net=bot_settings["mainNet"])
    # scheduler = start_scheduler(periodic_tasks)
    # #
    # # Activate merchant tasks
    # merchant_tasks = MerchantTasks(backoffice, bot)
    # merchant_scheduler = start_merchant_scheduler(merchant_tasks)


    # Discord Token
    bot.run()
    print("DONE")
