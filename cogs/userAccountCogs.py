import discord
from discord.ext import commands

from backOffice.botWallet import BotManager
from backOffice.profileRegistrations import AccountManager
from backOffice.stellarActivityManager import StellarManager
from backOffice.stellarOnChainHandler import StellarWallet
from cogs.utils.customCogChecks import is_public, user_has_wallet
from cogs.utils.monetaryConversions import convert_to_usd
from cogs.utils.monetaryConversions import get_normal, get_decimal_point
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
account_mng = AccountManager()
stellar_wallet = StellarWallet()
customMessages = CustomMessages()
bot_manager = BotManager()
stellar = StellarManager()

d = helper.read_json_file(file_name='botSetup.json')
notf_channels = helper.read_json_file(file_name='autoMessagingChannels.json')
hot_wallets = helper.read_json_file(file_name='hotWallets.json')

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'


class UserAccountCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(user_has_wallet)
    async def bal(self, ctx):
        print(f'BAL: {ctx.author}-> {ctx.message.content}')
        """
        Gets the user balances
        :param ctx:
        :return:
        """
        try:
            await ctx.message.delete()
        except Exception:
            pass

        values = account_mng.get_wallet_balances_based_on_discord_id(discord_id=ctx.message.author.id)
        if values:
            stellar_balance = get_normal(value=str(values['stellar']['balance']),
                                         decimal_point=get_decimal_point('xlm'))
            stellar_to_usd = convert_to_usd(amount=float(stellar_balance), coin_name='stellar')
            balance_embed = discord.Embed(title=f"Account details for  {ctx.message.author}",
                                          description='Bellow is the latest data on your Discord Wallet balance',
                                          colour=discord.Colour.green())

            balance_embed.add_field(
                name=f"{CONST_STELLAR_EMOJI} Stellar Balance {CONST_STELLAR_EMOJI}",
                value=f'__Crypto__ {stellar_balance} {CONST_STELLAR_EMOJI}\n'
                      f'__Fiat__: ${round(stellar_to_usd["total"], 4)} ({round(stellar_to_usd["usd"], 4)}$/XLM)\n'
                      f'web: https://www.stellar.org/\n'
                      f'cmc: https://coinmarketcap.com/currencies/stellar/',
                inline=False)
            balance_embed.set_footer(text='Conversion rates provided by CoinGecko')
            balance_embed.set_thumbnail(url=ctx.message.author.avatar_url)

            await ctx.author.send(embed=balance_embed)
        else:
            title = '__Account Balance Status__'
            message = f'Balance could not be checked at this moment. Please try again later.'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)

    @commands.command()
    @commands.check(is_public)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def register(self, ctx):
        print(f'REGISTER: {ctx.author} -> {ctx.message.content}')
        """
        Register user in the system
        :param ctx:
        :return:
        """
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if not account_mng.check_user_existence(user_id=ctx.message.author.id):
            if account_mng.register_user(discord_id=ctx.message.author.id, discord_username=f'{ctx.message.author}'):
                title = '__Account registration status__'
                message = f'Account has been successfully registered into the system and wallets created.' \
                          f' Please use {d["command"]}balance or {d["command"]}wallet.'
                await customMessages.system_message(ctx=ctx, color_code=0, message=message, destination=0,
                                                    sys_msg_title=title)
            else:
                title = '__Account registration status__'
                message = f'Account could not be registered at this moment please try again later.'
                await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                    sys_msg_title=title)
        else:
            title = '__Account registration status__'
            message = f'You have already registered account into the system. Please use ***{d["command"]}balance*** or ' \
                      f'***{d["command"]}wallet*** to obtain details on balances and your profile'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)

    @commands.group()
    @commands.check(user_has_wallet)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def wallet(self, ctx):
        print(f'WALLET: {ctx.author} -> {ctx.message.content}')
        """
        Get the details
        :param ctx:
        :return:
        """
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if ctx.invoked_subcommand is None:
            title = '__Available Wallets__'
            description = "All commands to check wallet details for each available cryptocurrency"
            list_of_values = [{"name": "Quick balance check", "value": f"{d['command']}bal"},
                {"name": "How to deposit to Discord wallet", "value": f"{d['command']}wallet deposit"},
                {"name": "Get Stellar (XLM) wallet details", "value": f"{d['command']}wallet balance"}]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                               destination=1)

    @wallet.command()
    async def deposit(self, ctx):
        """
        Returns instructions on how to deposit to the Discord Wallet
        :param ctx:
        :return:
        """
        print(f'WALLET DEPOSIT: {ctx.author} -> {ctx.message.content}')

        try:
            await ctx.message.delete()
        except Exception:
            pass

        user_profile = account_mng.get_user_profile(user_id=ctx.message.author.id)
        if user_profile:
            description = ' :warning: To top up your Discord wallets, you will need to send from your preferred wallet' \
                          ' (GUI, CLI) to the address and deposit ID provided below. Have in mind that there is ' \
                          'difference between Stellar and Scala deposit values. Providing wrong details for either ' \
                          'of them will result in funds being lost to which staff of Launch Pad Investments is not ' \
                          'responsible for. :warning:'

            deposit_embed = discord.Embed(title='How to deposit',
                                          colour=discord.Colour.green(),
                                          description=description)

            deposit_embed.add_field(name=':warning: **__Warning__** :warning:',
                                    value='Be sure to include and provide appropriate  **__deposit ID__** and Wallet '
                                          'address for each currency , otherwise your deposit will be lost!',
                                    inline=False)
            deposit_embed.add_field(
                name=f' {CONST_STELLAR_EMOJI} Stellar Lumen Deposit details {CONST_STELLAR_EMOJI}',
                value=f'Stellar wallet Address:\n'
                      f'{hot_wallets["xlm"]}\n'
                      f'\nMEMO:\n'
                      f'{user_profile["stellarDepositId"]}',
                inline=False)
            deposit_embed.set_thumbnail(url=ctx.message.author.avatar_url)
            await ctx.author.send(embed=deposit_embed)
        else:
            title = '__Deposit information error__'
            message = f'Deposit details for your account could not be obtained at this moment from the system. ' \
                      f'Please try again later, or contact one of the staff members. '
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)

    @wallet.command()
    async def balance(self, ctx):
        """
        Querying account details for the Stellar Lumen Wallet
        :param ctx:
        :return:
        """
        try:
            await ctx.message.delete()
        except Exception:
            pass

        print(f'WALLET BALANCE: {ctx.author} -> {ctx.message.content}')

        data = stellar.get_stellar_wallet_data_by_discord_id(discord_id=ctx.message.author.id)
        stellar_balance = get_normal(value=str(data['balance']),
                                     decimal_point=get_decimal_point('xlm'))
        stellar_to_usd = convert_to_usd(amount=float(stellar_balance), coin_name='stellar')
        if data:
            stellar_balance = get_normal(value=str(data['balance']),
                                         decimal_point=get_decimal_point('xlm'))

            balance_embed = discord.Embed(title=f"Stellar wallet details for {ctx.message.author}",
                                          colour=discord.Colour.green())
            balance_embed.add_field(name=":map:  Wallet address :map: ",
                                    value=hot_wallets['xlm'],
                                    inline=False)
            balance_embed.add_field(name=":pencil: Deposit ID:pencil: ",
                                    value=data['depositId'],
                                    inline=False)
            balance_embed.add_field(
                name=f"{CONST_STELLAR_EMOJI} Stellar Balance {CONST_STELLAR_EMOJI} ",
                value=f'__Crypto__: \n{stellar_balance} {CONST_STELLAR_EMOJI}\n'
                      f'__Fiat__: \n${stellar_to_usd["total"]} ({stellar_to_usd["usd"]})',
                inline=False)
            balance_embed.set_thumbnail(url="https://s2.coinmarketcap.com/static/img/coins/64x64/512.png")
            await ctx.author.send(embed=balance_embed)
        else:
            title = '__Stellar Wallet Error__'
            message = f'Wallet could not be obtained from the system please try again later'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                sys_msg_title=title)

    @balance.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__Balance check error__'
            message = f'You have not registered yourself into the system yet. Please head to one of the public ' \
                      f'channels, where Virtual Interactive Pilot is Accessible and  execute {d["command"]}register'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)

    @bal.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__Balance check error__'
            message = f'You have not registered yourself into the system yet. Please head to one of the public ' \
                      f'channels, where Virtual Interactive Pilot is Accessible and  execute {d["command"]}register'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)

    @register.error
    async def register_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__{d["command"]}register error__'
            message = f'You can not register over DM with the bot. Please head to one of the channel on Launch Pad ' \
                      f'Investment community and execute command  {d["command"]}register'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)

    @deposit.error
    async def deposit_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__{d["command"]}wallet deposit error__'
            message = f'You have not registered yourself yet into the system. Please use first {d["command"]}register'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)

    @wallet.error
    async def wallet_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__{d["command"]}wallet Error__'
            message = f'In order to access your wallet you need to be first registered into payment system. You can do' \
                      f' that with {d["command"]}register!'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)


def setup(bot):
    bot.add_cog(UserAccountCommands(bot))
