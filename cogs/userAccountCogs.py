from datetime import datetime

from discord import Embed, Colour
from discord.ext import commands

from backOffice.profileRegistrations import AccountManager
from backOffice.userWalletManager import UserWalletManager
from cogs.utils.customCogChecks import is_public, user_has_wallet
from cogs.utils.monetaryConversions import convert_to_usd, get_rates, rate_converter
from cogs.utils.monetaryConversions import get_normal, scientific_conversion
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
account_mng = AccountManager()
custom_messages = CustomMessages()
user_wallets = UserWalletManager()

d = helper.read_json_file(file_name='botSetup.json')
hot_wallets = helper.read_json_file(file_name='hotWallets.json')

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_ACC_REG_STATUS = '__Account registration status__'


class UserAccountCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(user_has_wallet)
    async def acc(self, ctx):
        utc_now = datetime.utcnow()
        wallet_data = user_wallets.get_full_details(user_id=ctx.message.author.id)

        xlm_balance = round(float(wallet_data["xlm"]) / 10000000, 7)
        rates = get_rates(coin_name='stellar')
        in_eur = rate_converter(xlm_balance, rates["stellar"]["eur"])
        in_usd = rate_converter(xlm_balance, rates["stellar"]["usd"])
        in_btc = rate_converter(xlm_balance, rates["stellar"]["btc"])
        in_eth = rate_converter(xlm_balance, rates["stellar"]["eth"])
        in_rub = rate_converter(xlm_balance, rates["stellar"]["rub"])
        in_ltc = rate_converter(xlm_balance, rates["stellar"]["ltc"])

        acc_details = Embed(title=f'{ctx.author}',
                            description=f'***__Basic details on your Discord account__***',
                            colour=Colour.light_grey(),
                            timestamp=utc_now)
        acc_details.set_author(name=f'Discord Account details', icon_url=ctx.author.avatar_url)
        acc_details.add_field(name=":map: Wallet address :map: ",
                              value=f"```{hot_wallets['xlm']}```")
        acc_details.add_field(name=":compass:  MEMO :compass: ",
                              value=f"```{wallet_data['depositId']}```",
                              inline=False)
        acc_details.add_field(name=':moneybag: Stellar Lumen (XLM) Balance :moneybag: ',
                              value=f'{xlm_balance} {CONST_STELLAR_EMOJI}\n\n',
                              inline=False)
        acc_details.add_field(name=f':flag_us: USA',
                              value=f'$ {scientific_conversion(in_usd, 4)}')
        acc_details.add_field(name=f':flag_eu: EUR',
                              value=f'€ {scientific_conversion(in_eur, 4)}')
        acc_details.add_field(name=f':flag_ru:  RUB',
                              value=f'₽ {scientific_conversion(in_rub, 4)}')
        acc_details.add_field(name=f'BTC',
                              value=f'₿ {scientific_conversion(in_btc, 8)}')
        acc_details.add_field(name=f'ETH',
                              value=f'Ξ {scientific_conversion(in_eth, 8)}')
        acc_details.add_field(name=f'LTC',
                              value=f'Ł {scientific_conversion(in_ltc, 8)}')

        acc_details.add_field(name=f'More On Stellar Lumen (XLM)',
                              value=f'[Stellar](https://www.stellar.org/)\n'
                                    f'[Stellar Foundation](https://www.stellar.org/foundation)\n'
                                    f'[Stellar Lumens](https://www.stellar.org/lumens)\n'
                                    f'[CMC](https://coinmarketcap.com/currencies/stellar/)')
        acc_details.set_footer(text='Conversion rates provided by CoinGecko')
        await ctx.author.send(embed=acc_details)

    @commands.command()
    @commands.check(is_public)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def register(self, ctx):
        if not account_mng.check_user_existence(user_id=ctx.message.author.id):
            if account_mng.register_user(discord_id=ctx.message.author.id, discord_username=f'{ctx.message.author}'):
                message = f'Account has been successfully registered into the system and wallets created.' \
                          f' Please use {d["command"]}acc or {d["command"]}wallet.'
                await custom_messages.system_message(ctx=ctx, color_code=0, message=message, destination=0,
                                                     sys_msg_title=CONST_ACC_REG_STATUS)
            else:
                message = f'Account could not be registered at this moment please try again later.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=CONST_ACC_REG_STATUS)
        else:
            message = f'You have already registered account into the system. Please use ***{d["command"]}acc*** or ' \
                      f'***{d["command"]}wallet*** to obtain details on balances and your profile'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACC_REG_STATUS)

    @commands.group()
    @commands.check(user_has_wallet)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def wallet(self, ctx):
        if ctx.invoked_subcommand is None:
            title = '__Available Wallets__'
            description = "All commands to check wallet details for each available cryptocurrency"
            list_of_values = [{"name": "Quick balance check", "value": f"{d['command']}acc"},
                              {"name": "How to deposit to Discord wallet", "value": f"{d['command']}wallet deposit"},
                              {"name": "How to deposit to Discord wallet", "value": f"{d['command']}wallet stats"},
                              {"name": "Get Stellar (XLM) wallet details", "value": f"{d['command']}wallet balance"}]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1)

    @wallet.command()
    async def stats(self, ctx):
        utc_now = datetime.utcnow()
        account_details = account_mng.get_account_details(discord_id=ctx.message.author.id)
        stellar_stats = account_details["xlmStats"]
        # Send XLM Wallet stats
        await custom_messages.stellar_wallet_overall(ctx=ctx, utc_now=utc_now, stellar_stats=stellar_stats)

    @wallet.command()
    async def deposit(self, ctx):
        user_profile = account_mng.get_user_memo(user_id=ctx.message.author.id)
        if user_profile:
            description = ' :warning: To top up your Discord wallets, you will need to send from your preferred' \
                          ' wallet(GUI, CLI) to the address and deposit ID provided below. Have in mind that there is' \
                          ' difference bet ween Stellar and Scala deposit values. Providing wrong details for either ' \
                          'of them will result in funds being lost to which staff of Launch Pad Investments is not ' \
                          'responsible for. :warning:'

            deposit_embed = Embed(title='How to deposit',
                                  colour=Colour.green(),
                                  description=description)

            deposit_embed.add_field(name=':warning: **__Warning__** :warning:',
                                    value='Be sure to include and provide appropriate  **__deposit ID__** and Wallet '
                                          'address for each currency , otherwise your deposit will be lost!',
                                    inline=False)
            deposit_embed.add_field(
                name=f' {CONST_STELLAR_EMOJI} Stellar Lumen Deposit details {CONST_STELLAR_EMOJI}',
                value=f'Stellar wallet Address:\n'
                      f'```{hot_wallets["xlm"]}```\n'
                      f'\nMEMO:\n'
                      f'> {user_profile["stellarDepositId"]}',
                inline=False)
            deposit_embed.set_thumbnail(url=ctx.message.author.avatar_url)
            await ctx.author.send(embed=deposit_embed)
        else:
            title = '__Deposit information error__'
            message = f'Deposit details for your account could not be obtained at this moment from the system. ' \
                      f'Please try again later, or contact one of the staff members. '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)

    @wallet.command()
    async def balance(self, ctx):
        user_balances = user_wallets.get_balances(user_id=ctx.message.author.id)
        coin_data = helper.read_json_file(file_name='integratedCoins.json')
        if user_balances:
            all_wallets = list(user_balances.keys())

            # initiate Discord embed
            balance_embed = Embed(title=f"Wallet details for {ctx.message.author}",
                                  timestamp=datetime.utcnow(),
                                  colour=Colour.green())
            balance_embed.set_thumbnail(url=ctx.message.author.avatar_url)
            for wallet_ticker in all_wallets:
                coin_settings = coin_data[wallet_ticker]

                token_balance = get_normal(value=str(user_balances[wallet_ticker]),
                                           decimal_point=int(coin_settings["decimal"]))

                if coin_settings["coinGeckoListing"]:
                    token_to_usd = convert_to_usd(amount=float(token_balance), coin_name='stellar')
                else:
                    token_to_usd = {"total": 0,
                                    "usd": 0}

                balance_embed.add_field(
                    name=f"{coin_settings['emoji']} {coin_settings['name']} Balance {coin_settings['emoji']}",
                    value=f'__Crypto__: \n{token_balance} {coin_settings["emoji"]}\n'
                          f'__Fiat__: \n${token_to_usd["total"]} ({token_to_usd["usd"]})',
                    inline=False)

            await ctx.author.send(embed=balance_embed)
        else:
            title = '__Stellar Wallet Error__'
            message = f'Wallet could not be obtained from the system please try again later'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)

    @balance.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__System Error__'
            message = f'You have not registered yourself into the system yet. Please head to one of the public ' \
                      f'channels, where Virtual Interactive Pilot is Accessible and  execute {d["command"]}register'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @acc.error
    async def quick_acc_check_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__Balance check error__'
            message = f'In order to check balance you need to be registered into the system'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @register.error
    async def register_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__{d["command"]}register error__'
            message = f'You can not register over DM with the bot. Please head to one of the channel on Launch Pad ' \
                      f'Investment community and execute command  {d["command"]}register'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @deposit.error
    async def deposit_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__{d["command"]}wallet deposit error__'
            message = f'You have not registered yourself yet into the system. Please use first {d["command"]}register'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @wallet.error
    async def wallet_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__{d["command"]}wallet Error__'
            message = f'In order to access your wallet you need to be first registered into payment system. You' \
                      f' can do that with {d["command"]}register!'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(UserAccountCommands(bot))
