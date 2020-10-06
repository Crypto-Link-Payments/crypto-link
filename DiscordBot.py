import discord
from discord.ext import commands
from colorama import Fore, init

from utils.tools import Helpers

#init colorama :
init(autoreset=True)


extensions = ['cogs.generalCogs', 'cogs.transactionCogs', 'cogs.userAccountCogs',
              'cogs.systemMngCogs', 'cogs.withdrawalCogs',
              'cogs.merchantCogs', 'cogs.consumerMerchant', 'cogs.autoMessagesCogs', 'cogs.merchantLicensingCogs',
              'cogs.feeManagementCogs', 'cogs.guildOwnersCmds']


class DiscordBot(commands.Bot):
    def __init__(self, backoffice):
        helper = Helpers()
        self.bot_settings = helper.read_json_file(file_name='botSetup.json')

        super().__init__(command_prefix=commands.when_mentioned_or(self.bot_settings['command']))
        self.remove_command('help')  # removing the old help command
        self.backoffice = backoffice
        self.load_cogs()

    def load_cogs(self):
        notification_str = Fore.GREEN + '+++++++++++++++++++++++++++++++++++++++\n' \
                                        '           LOADING COGS....        \n'
        for extension in extensions:
            try:
                self.load_extension(extension)
                notification_str += f'| {extension} :smile: \n'
            except Exception as error:
                notification_str += f'| {extension} --> {error}\n'
                raise
        notification_str += '+++++++++++++++++++++++++++++++++++++++'
        print(notification_str)

    async def on_ready(self):
        """
            Print out to console once bot logs in
            :return:
            """

        await self.change_presence(status=discord.Status.online, activity=discord.Game('Online and ready'))
        print(Fore.GREEN + 'DISCORD BOT : Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        print('================================')

    def run(self):
        super().run(self.bot_settings['token'], reconnect=True)

    def is_animus(self, user_id):
        """
        Check if creator
        """
        return user_id == self.bot_settings['creator']

    def is_one_of_gods(self, user_id):
        list_of_gods = [self.bot_settings['ownerId'], self.bot_settings['creator']]
        return [god for god in list_of_gods if god == user_id]

    def get_command_str(self):
        return self.bot_settings['command']

