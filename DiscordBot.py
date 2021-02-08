import discord
from discord.ext import commands
from discord import Intents
from colorama import Fore, init

from utils.tools import Helpers

CONST_SEPARATOR = '+++++++++++++++++++++++++++++++++++++++'
# init colorama :
init(autoreset=True)

cl_cogs = ['cogs.help', 'cogs.transactions', 'cogs.accounts',
           'cogs.system', 'cogs.withdrawals',
           'cogs.guildMerchant', 'cogs.consumer', 'cogs.automatic', 'cogs.guildOwners']


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
    def __init__(self, backoffice):
        helper = Helpers()
        self.bot_settings = helper.read_json_file(file_name='botSetup.json')
        self.integrated_coins = helper.read_json_file(file_name='integratedCoins.json')
        self.list_of_coins = list(self.integrated_coins.keys())
        super().__init__(
            command_prefix=commands.when_mentioned_or(self.bot_settings['command']),
            intents=Intents.all())
        self.remove_command('help')  # removing the old help command
        self.backoffice = backoffice
        self.load_cogs()

    def load_cogs(self):
        notification_str = Fore.GREEN + '+++++++++++++++++++++++++++++++++++++++\n' \
                                        '           LOADING Crypto Link COGS....        \n'
        for extension in cl_cogs:
            try:
                self.load_extension(extension)
                notification_str += f'| {extension} :smile: \n'
            except Exception as error:
                notification_str += f'| {extension} --> {error}\n'
                raise
        notification_str += CONST_SEPARATOR
        print(notification_str)

        # notification_str = Fore.BLUE + '+++++++++++++++++++++++++++++++++++++++\n' \
        #                                '           LOADING Commands level 2....        \n'
        #
        # for cust_cmd in custodial_layer:
        #     try:
        #         self.load_extension(cust_cmd)
        #         notification_str += f'| {cust_cmd} :smile: \n'
        #     except Exception as error:
        #         notification_str += f'| {cust_cmd} --> {error}\n'
        #         raise
        # notification_str += CONST_SEPARATOR
        # print(notification_str)

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
                notification_str += f'| {hor} :smile: \n'
            except Exception as error:
                notification_str += f'| {hor} --> {error}\n'
                raise
        notification_str += CONST_SEPARATOR
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

    async def on_reconnect(self):
        guild = await self.fetch_guild(guild_id=756132394289070102)
        role = guild.get_role(role_id=773212890269745222)
        channel = self.get_channel(id=int(773157463628709898))
        message = f':robot: {role.mention} I have just reconnected due to Discord Api Ping error.'
        await channel.send(content=message)

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
