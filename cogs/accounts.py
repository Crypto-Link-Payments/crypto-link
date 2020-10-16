from datetime import datetime
import re
from discord import Embed, Colour
from discord.ext import commands

from cogs.utils.customCogChecks import is_public, user_has_wallet
from cogs.utils.monetaryConversions import convert_to_usd, get_rates, rate_converter
from cogs.utils.monetaryConversions import get_normal, scientific_conversion
from cogs.utils.systemMessaages import CustomMessages
from cogs.utils.securityChecks import check_stellar_private
from utils.tools import Helpers

helper = Helpers()
custom_messages = CustomMessages()
hot_wallets = helper.read_json_file(file_name='hotWallets.json')
integrated_coins = helper.read_json_file(file_name='integratedCoins.json')
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_ACC_REG_STATUS = '__Account registration status__'
CONST_TRUST_ERROR = ':warning: __Trustline error__ :warning:'


class UserAccountCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.list_of_coins = list(integrated_coins.keys())

    @commands.command(aliases=['me', 'account'])
    @commands.check(user_has_wallet)
    async def acc(self, ctx):
        utc_now = datetime.utcnow()
        wallet_data = self.backoffice.wallet_manager.get_full_details(user_id=ctx.message.author.id)

        xlm_balance = round(float(wallet_data["xlm"]) / 10000000, 7)
        rates = get_rates(coin_name='stellar')
        in_eur = rate_converter(xlm_balance, rates["stellar"]["eur"])
        in_usd = rate_converter(xlm_balance, rates["stellar"]["usd"])
        in_btc = rate_converter(xlm_balance, rates["stellar"]["btc"])
        in_eth = rate_converter(xlm_balance, rates["stellar"]["eth"])
        in_rub = rate_converter(xlm_balance, rates["stellar"]["rub"])
        in_ltc = rate_converter(xlm_balance, rates["stellar"]["ltc"])

        acc_details = Embed(title=f':office_worker: {ctx.author} :office_worker:',
                            description=f' ***__Basic details on your Discord account__*** ',
                            colour=Colour.dark_orange(),
                            timestamp=utc_now)
        acc_details.set_author(name=f'Discord Account details', icon_url=ctx.author.avatar_url)
        acc_details.add_field(name=":map: Wallet address :map: ",
                              value=f"```{hot_wallets['xlm']}```")
        acc_details.add_field(name=":compass: MEMO :compass: ",
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

        acc_details.add_field(name=f'{CONST_STELLAR_EMOJI} More On Stellar Lumen (XLM) {CONST_STELLAR_EMOJI}',
                              value=f'[Stellar](https://www.stellar.org/)\n'
                                    f'[Stellar Foundation](https://www.stellar.org/foundation)\n'
                                    f'[Stellar Lumens](https://www.stellar.org/lumens)\n'
                                    f'[CMC](https://coinmarketcap.com/currencies/stellar/)\n'
                                    f'[Stellar Expert](https://stellar.expert/explorer/public)')
        acc_details.set_footer(text='Conversion rates provided by CoinGecko')
        await ctx.author.send(embed=acc_details)

    @commands.command(aliases=['reg', 'apply'])
    @commands.check(is_public)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def register(self, ctx):
        if not self.backoffice.account_mng.check_user_existence(user_id=ctx.message.author.id):
            if self.backoffice.account_mng.register_user(discord_id=ctx.message.author.id,
                                                         discord_username=f'{ctx.message.author}'):
                message = f'Account has been successfully registered into the system and wallets created.' \
                          f' Please use {self.command_string}acc or {self.command_string}wallet.'
                await custom_messages.system_message(ctx=ctx, color_code=0, message=message, destination=0,
                                                     sys_msg_title=CONST_ACC_REG_STATUS)
            else:
                message = f'Account could not be registered at this moment please try again later.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=CONST_ACC_REG_STATUS)
        else:
            message = f'You have already registered account into the system. Please use ***{self.command_string}acc*** or ' \
                      f'***{self.command_string}wallet*** to obtain details on balances and your profile'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACC_REG_STATUS)

    @commands.group()
    @commands.check(user_has_wallet)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def wallet(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':joystick: __Available Wallet Commands__ :joystick: '
            description = "All commands available to operate execute wallet related actions"
            list_of_values = [{"name": " :woman_technologist: Get Full Account Balance Report :woman_technologist:  ",
                               "value": f"`{self.command_string}wallet balance`"},
                              {"name": ":bar_chart: Get Wallet Statistics :bar_chart:",
                               "value": f"`{self.command_string}wallet stats`"},
                              {"name": ":inbox_tray: Get Deposit Instructions :inbox_tray:",
                               "value": f"`{self.command_string}wallet deposit`"},
                              {"name": ":outbox_tray: Get Withdrawal Instructions :outbox_tray: ",
                               "value": f"`{self.command_string}withdraw`"}]
            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.dark_orange())

    @wallet.command()
    async def stats(self, ctx):
        utc_now = datetime.utcnow()
        account_details = self.backoffice.account_mng.get_account_stats(discord_id=ctx.message.author.id)
        await custom_messages.stellar_wallet_overall(ctx=ctx, coin_stats=account_details, utc_now=utc_now)

    @wallet.command()
    async def deposit(self, ctx):
        user_profile = self.backoffice.account_mng.get_user_memo(user_id=ctx.message.author.id)
        if user_profile:
            description = ' :warning: To top up your Discord wallets, you will need to send from your preferred' \
                          ' wallet(GUI, CLI) to the address and deposit ID provided below. Of them will result in ' \
                          'funds being lost to which staff of Launch Pad Investments is not ' \
                          'responsible for. :warning:'

            deposit_embed = Embed(title='How to deposit',
                                  colour=Colour.dark_orange(),
                                  description=description)

            deposit_embed.add_field(name=':warning: **__Warning__** :warning:',
                                    value='Be sure to include and provide appropriate  **__deposit ID__** and Wallet '
                                          'address for each currency , otherwise your deposit will be lost!',
                                    inline=False)
            deposit_embed.add_field(
                name=f' {CONST_STELLAR_EMOJI} Stellar wallet Deposit Details {CONST_STELLAR_EMOJI}',
                value=f'\n:map: Public Address :map: \n'
                      f'```{hot_wallets["xlm"]}```\n'
                      f':compass: MEMO :compass:\n'
                      f'> {user_profile["stellarDepositId"]}',
                inline=False)

            coins_string = ', '.join([str(coin.upper()) for coin in self.list_of_coins])

            deposit_embed.add_field(name="Currently available currencies on Crypto Link",
                                    value=f'{coins_string}')

            deposit_embed.set_thumbnail(url=ctx.message.author.avatar_url)
            await ctx.author.send(embed=deposit_embed)
        else:
            title = '__Deposit information error__'
            message = f'Deposit details for your account could not be obtained at this moment from the system. ' \
                      f'Please try again later, or contact one of the staff members. '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)

    @wallet.command(aliases=['bal', 'balances', 'b'])
    async def balance(self, ctx):
        user_balances = self.backoffice.wallet_manager.get_balances(user_id=ctx.message.author.id)
        coin_data = helper.read_json_file(file_name='integratedCoins.json')
        if user_balances:
            all_wallets = list(user_balances.keys())

            # initiate Discord embed
            balance_embed = Embed(title=f":office_worker: Wallet details for {ctx.message.author} :office_worker:",
                                  timestamp=datetime.utcnow(),
                                  colour=Colour.dark_orange())
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

    @wallet.command()
    async def trust(self, ctx, private_key, token: str):
        """
        Command which is used for users to establish a trust line between their personal dekstop accounts and
        token issuer
        """
        token = token.lower()
        # check strings, stellar address and token integration status
        if check_stellar_private(private_key=private_key):
            if not re.search("[~!#$%^&*()_+{}:;\']", token) and token in self.list_of_coins and token != 'xlm':
                if self.backoffice.stellar_wallet.establish_trust(private_key=private_key, token=f'{token.upper()}'):
                    title = ':rocket: __Trust line established__ :rocket:'
                    message = f'Trustline between your personal wallet and issuer has been successfully established. ' \
                              f' You can now withdraw token {token} to your personal wallet'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                         sys_msg_title=title)
                else:
                    message = f'Crypto Link could not establish trustline with issuer, since wallet address does not ' \
                              f'exist on the network or the wallet has not been activate yet.'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                         sys_msg_title=CONST_TRUST_ERROR)

            else:
                message = f'Trustline creation for failed, as token {token} is not implemented in Crypto Link'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                     sys_msg_title=CONST_TRUST_ERROR)
        else:
            title = '__Trustline error__'
            message = f'You have provided wrong Ed25519 Secret Seed.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)

    @balance.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__System Error__'
            message = f'You have not registered yourself into the system yet. Please head to one of the public ' \
                      f'channels, where Virtual Interactive Pilot is Accessible and  execute {self.command_string}register'
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
            title = f'__{self.command_string}register error__'
            message = f'You can not register over DM with the bot. Please head to one of the channel on Launch Pad ' \
                      f'Investment community and execute command  {self.command_string}register'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @deposit.error
    async def deposit_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__{self.command_string}wallet deposit error__'
            message = f'You have not registered yourself yet into the system. Please use first {self.command_string}register'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @wallet.error
    async def wallet_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__{self.command_string}wallet Error__'
            message = f'In order to access your wallet you need to be first registered into payment system. You' \
                      f' can do that with {self.command_string}register!'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(UserAccountCommands(bot))
