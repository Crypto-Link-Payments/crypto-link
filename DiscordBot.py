import discord
from discord.ext import commands
from discord import Intents
from colorama import Fore, init
import json
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

def get_prefix(client,message):
    with open("prefixe.json","r") as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]


class DiscordBot(commands.Bot):
    def __init__(self, backoffice, bot_settings: dict):
        helper = Helpers()
        self.bot_settings = bot_settings
        self.integrated_coins = helper.read_json_file(file_name='integratedCoins.json')
        self.hot_wallets = backoffice.stellar_wallet.public_key
        self.list_of_coins = list(self.integrated_coins.keys())
        # super().__init__(
        #     command_prefix=commands.when_mentioned_or(self.bot_settings['command']),
        #     intents=Intents.all())
        super().__init__(
            command_prefix=commands.when_mentioned_or(get_prefix),
            intents=Intents.all())
        self.remove_command('help')  # removing the old help command
        self.backoffice = backoffice
        self.load_cogs()

        print(Fore.CYAN + f'{self.hot_wallets}')

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

    async def on_ready(self):
        """
            Print out to console once bot logs in
            :return:
            """

        for g in self.guilds:
            check_guild_prefix = self.backoffice.guild_profiles.check_guild_prefix(guild_id=int(g.id))
            if not check_guild_prefix:
                if self.backoffice.guild_profiles.set_guild_prefix(guild_id=int(g.id), prefix="!"):
                    print(Fore.YELLOW + f"Default prefix registered for {g}")
                else:
                    print(Fore.RED + f"Could not register prefix for {g}")
            else:
                print(Fore.GREEN + f"{g} Prefix ....OK")

        await self.change_presence(status=discord.Status.online, activity=discord.Game('Monitoring Stellar'))
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
