from nextcord.ext import commands
from nextcord import Intents

from colorama import Fore, init
import json
from utils.tools import Helpers

CONST_SEPARATOR = '+++++++++++++++++++++++++++++++++++++++'
# init colorama :
init(autoreset=True)

cl_cogs = ['cogs.help', 'cogs.transactions', 'cogs.accounts',
           'cogs.system', 'cogs.withdrawals',
           'cogs.guildMerchant', 'cogs.consumer', 'cogs.automatic', 'cogs.guildOwners','cogs.specialPayments',
           'cogs.ballotOwner', 'cogs.voters']

horizon_cogs = ['horizonCommands.horizonMain',
                'horizonCommands.accounts',
                'horizonCommands.payments',
                'horizonCommands.ledger',
                'horizonCommands.transactions',
                'horizonCommands.assets',
                'horizonCommands.effects',
                'horizonCommands.operations',
                'horizonCommands.offers',
                'horizonCommands.trades',
                'horizonCommands.orderBook',
                'horizonCommands.paths',
                'horizonCommands.tradeAggregations']


# non_custodial_layer_cmds = ['thirdLevel.thirdLevelAccounts']
#
# custodial_layer = ['secondLevel.secondLevelAccounts']


class DiscordBot(commands.Bot):
    def __init__(self, backoffice, bot_settings: dict):
        self.bot_settings = bot_settings
        self.hot_wallets = backoffice.stellar_wallet.public_key

        super().__init__(
            command_prefix=commands.when_mentioned_or(self.get_prefix),
            intents=Intents.all())
        self.remove_command('help')  # removing the old help command
        self.backoffice = backoffice
        self.load_cogs()

        print(Fore.CYAN + f'{self.hot_wallets}')

    def get_prefix_help(self, guild_id):
        try:
            return self.backoffice.guild_profiles.get_guild_prefix_norm(guild_id=guild_id)
        except Exception:
            return self.bot_settings['command']

    async def get_prefix(self, message):
        try:
            return await self.backoffice.guild_profiles.get_guild_prefix(guild_id=message.guild.id)
        except Exception:
            return self.bot_settings['command']

    def load_cogs(self):
        notification_str = Fore.GREEN + '+++++++++++++++++++++++++++++++++++++++\n' \
                                        '           LOADING Crypto Link COGS....        \n'
        for extension in cl_cogs:
            try:
                self.load_extension(extension)
            except Exception as error:
                notification_str += f'| {extension} --> {error}\n'
                raise
        notification_str += CONST_SEPARATOR
        print(notification_str)

        # notification_str = Fore.WHITE + '+++++++++++++++++++++++++++++++++++++++\n' \
        #                                 '           LOADING Commands level 3....        \n'

        # for cmd in non_custodial_layer_cmds:
        #     try:
        #         self.load_extension(cmd)
        #         notification_str += f'| {cmd} :smile: \n'
        #     except Exception as error:
        #         notification_str += f'| {cmd} --> {error}\n'
        #         raise
        # notification_str += CONST_SEPARATOR
        # print(notification_str)
        #
        # notification_str = Fore.CYAN + '+++++++++++++++++++++++++++++++++++++++\n' \
        #                                '           LOADING Horizon commands....        \n'
        for hor in horizon_cogs:
            try:
                self.load_extension(hor)
            except Exception as error:
                notification_str += f'| {hor} --> {error}\n'
                raise
        notification_str += CONST_SEPARATOR
        print(notification_str)

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
