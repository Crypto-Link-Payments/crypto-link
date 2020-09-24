from datetime import datetime

from discord import Embed, Colour
from discord.ext import commands

from backOffice.clTokenACtivityManager import ClTokenManager
from backOffice.profileRegistrations import AccountManager
from backOffice.stellarActivityManager import StellarManager
from cogs.utils.customCogChecks import is_public, user_has_wallet
from cogs.utils.monetaryConversions import convert_to_usd, get_rates, rate_converter
from cogs.utils.monetaryConversions import get_normal, get_decimal_point, scientific_conversion
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
account_mng = AccountManager()
customMessages = CustomMessages()
stellar = StellarManager()
clToken = ClTokenManager()

d = helper.read_json_file(file_name='botSetup.json')
hot_wallets = helper.read_json_file(file_name='hotWallets.json')

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_ACC_REG_STATUS = '__Account registration status__'


class UserAccountCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(user_has_wallet)
    async def bal(self, ctx):
        print(f'BAL: {ctx.author}-> {ctx.message.content}')
        values = account_mng.get_wallet_balances_based_on_discord_id(discord_id=ctx.message.author.id)
        if values:
            stellar_balance = get_normal(value=str(values['stellar']['balance']),
                                         decimal_point=get_decimal_point('xlm'))
            stellar_to_usd = convert_to_usd(amount=float(stellar_balance), coin_name='stellar')
            balance_embed = Embed(title=f"Account details for  {ctx.message.author}",
                                  description='Bellow is the latest data on your Discord Wallet balance',
                                  colour=Colour.green())

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

    @commands.group()
    @commands.check(user_has_wallet)
    async def acc(self, ctx):
        stellar_wallet_data = stellar.get_stellar_wallet_data_by_discord_id(discord_id=ctx.message.author.id)
        token_wallet_data = clToken.get_cl_token_data_by_id(discord_id=ctx.message.author.id)
        account_details = account_mng.get_account_details(discord_id=ctx.message.author.id)
        xlm_balance = round(float(stellar_wallet_data["balance"]) / 10000000, 7)

        rates = get_rates(coin_name='stellar')
        in_eur = rate_converter(xlm_balance, rates["stellar"]["eur"])
        in_usd = rate_converter(xlm_balance, rates["stellar"]["usd"])
        in_btc = rate_converter(xlm_balance, rates["stellar"]["btc"])
        in_eth = rate_converter(xlm_balance, rates["stellar"]["eth"])

        transaction_counter = account_details["transactionCounter"]

        stellar_stats = account_details["xlmStats"]
        cl_coin_stats = account_details["clCoinStats"]

        stellar_balance = get_normal(value=str(stellar_wallet_data["balance"]),
                                     decimal_point=get_decimal_point('xlm'))

        cl_token_balance = get_normal(value=str(token_wallet_data["balance"]),
                                      decimal_point=get_decimal_point('xlm'))

        utc_now = datetime.utcnow()
        acc_entry = Embed(title='__Account Details__',
                          colour=Colour.dark_blue(),
                          timestamp=utc_now)
        acc_entry.set_thumbnail(url=ctx.author.avatar_url)
        acc_entry.add_field(name=f'Account Owner',
                            value=f'{ctx.message.author}',
                            inline=True)
        acc_entry.add_field(name=f'Account Id',
                            value=f'{ctx.message.author.id}',
                            inline=True)
        acc_entry.add_field(name=f'Stellar Lumen Balance',
                            value=f'{stellar_balance} {CONST_STELLAR_EMOJI} (${in_usd})',
                            inline=True)
        acc_entry.add_field(name=f'Crypto Link Token Balance',
                            value=f'{cl_token_balance} :sweat_drops:',
                            inline=True)
        acc_entry.add_field(name='Sent Transactions',
                            value=f'{transaction_counter["sentTxCount"]}',
                            inline=False)
        acc_entry.add_field(name='Received Transactions',
                            value=f'{transaction_counter["receivedCount"]}')
        acc_entry.add_field(name='Multi Transactions',
                            value=f'{transaction_counter["multiTxCount"]}')
        acc_entry.add_field(name='Emoji Transactions',
                            value=f'{transaction_counter["emojiTxCount"]}')
        acc_entry.add_field(name='Roles Purchased',
                            value=f'{transaction_counter["rolePurchase"]}')
        await ctx.author.send(embed=acc_entry)

        xlm_wallet = Embed(title=f'{CONST_STELLAR_EMOJI} Stellar Lumen Wallet Details {CONST_STELLAR_EMOJI}',
                           description='Bellow are latest details on your Stellar Lumen Crypto Link wallet',
                           colour=Colour.light_grey(),
                           timestamp=utc_now)
        xlm_wallet.add_field(name='Hot Wallet Address',
                             value=f'```{hot_wallets["xlm"]}```',
                             inline=False)
        xlm_wallet.add_field(name='Deposit Memo',
                             value=f'{stellar_wallet_data["depositId"]}',
                             inline=False)
        xlm_wallet.add_field(name='Stellar Lumen (XLM) Balance',
                             value=f'{stellar_balance} {CONST_STELLAR_EMOJI}',
                             inline=False)
        xlm_wallet.add_field(name='Wallet Conversions',
                             value=f'$ {in_usd}\n'
                                   f'€ {in_eur}\n'
                                   f'₿ {in_btc}\n'
                                   f'Ξ {in_eth}',
                             inline=True)
        xlm_wallet.add_field(name='Market Rate',
                             value=f'$ {rates["stellar"]["usd"]}\n'
                                   f'€ {rates["stellar"]["eur"]}\n'
                                   f'₿ {scientific_conversion(rates["stellar"]["btc"], 8)}\n'
                                   f'Ξ {rates["stellar"]["eth"]}\n',
                             inline=True)

        xlm_wallet.add_field(name='Σ Deposits',
                             value=f'{stellar_stats["depositsCount"]}',
                             inline=False)
        xlm_wallet.add_field(name='Σ Total Deposited',
                             value=f'{stellar_stats["totalDeposited"]}')
        xlm_wallet.add_field(name='Σ Withdrawals',
                             value=f'{stellar_stats["withdrawalsCount"]}',
                             inline=True)
        xlm_wallet.add_field(name='Σ Withdrawn',
                             value=f'{stellar_stats["totalWithdrawn"]}',
                             inline=True)
        xlm_wallet.add_field(name='Σ XLM Sent',
                             value=f'{stellar_stats["sent"]}')
        xlm_wallet.add_field(name='Σ XLM Received',
                             value=f'{stellar_stats["received"]}')
        xlm_wallet.add_field(name='Σ Public Tx',
                             value=f'{stellar_stats["publicTxCount"]}',
                             inline=True)
        xlm_wallet.add_field(name='Σ Private Tx',
                             value=f'{stellar_stats["privateTxCount"]}',
                             inline=True)

        await ctx.author.send(embed=xlm_wallet)

        token_wallet = Embed(title=':sweat_drops: Crypto Link Token Details :sweat_drops:',
                             description='Bellow are latest details on your Crypto Link Token wallet',
                             colour=Colour.blue(),
                             timestamp=utc_now)
        token_wallet.add_field(name='Hot Wallet Address',
                               value=f'```{hot_wallets["xlm"]}```',
                               inline=False)
        token_wallet.add_field(name='Deposit Memo',
                               value=f'{stellar_wallet_data["depositId"]}',
                               inline=False)
        token_wallet.add_field(name='Crypto Link Token Balance',
                               value=f'{stellar_balance} :sweat_drops:',
                               inline=False)

        token_wallet.add_field(name='Σ Deposits',
                               value=f'{cl_coin_stats["depositsCount"]}')
        token_wallet.add_field(name='Σ Total Deposited',
                               value=f'{cl_coin_stats["totalDeposited"]}')
        token_wallet.add_field(name='Σ Withdrawals',
                               value=f'{cl_coin_stats["withdrawalsCount"]}',
                               inline=True)
        token_wallet.add_field(name='Σ Withdrawn',
                               value=f'{cl_coin_stats["totalWithdrawn"]}',
                               inline=True)
        token_wallet.add_field(name='Σ :sweat_drops: Sent',
                               value=f'{cl_coin_stats["sent"]}')
        token_wallet.add_field(name='Σ :sweat_drops: Received',
                               value=f'{cl_coin_stats["received"]}')
        token_wallet.add_field(name=':pick: Mined',
                               value=f'{cl_coin_stats["mined"]}')
        token_wallet.add_field(name='Σ Public Tx',
                               value=f'{cl_coin_stats["publicTxCount"]}',
                               inline=True)
        token_wallet.add_field(name='Σ Private Tx',
                               value=f'{cl_coin_stats["privateTxCount"]}',
                               inline=True)
        await ctx.author.send(embed=token_wallet)

        membership_stats = account_details["membershipStats"]

        merchant_info = Embed(title=':convenience_store: Membership Statistics :convenience_store: ',
                              description='Statistics on Merchant System Usage and Role purchases',
                              colour=Colour.orange(),
                              timestamp=utc_now)
        merchant_info.add_field(name='Roles purchased',
                                value=f'{membership_stats["rolePurchased"]}',
                                inline=False)
        merchant_info.add_field(name='USD Spent',
                                value=f'${membership_stats["spentOnRolesUsd"]}')
        merchant_info.add_field(name='CL Token Spent',
                                value=f'{membership_stats["spentOnRolesCl"]} :sweat_drops:')
        merchant_info.add_field(name='XLM Spent',
                                value=f'{membership_stats["spentOnRolesXlm"]} {CONST_STELLAR_EMOJI}')
        await ctx.author.send(embed=merchant_info)

    @commands.command()
    @commands.check(is_public)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def register(self, ctx):
        print(f'REGISTER: {ctx.author} -> {ctx.message.content}')
        if not account_mng.check_user_existence(user_id=ctx.message.author.id):
            if account_mng.register_user(discord_id=ctx.message.author.id, discord_username=f'{ctx.message.author}'):
                message = f'Account has been successfully registered into the system and wallets created.' \
                          f' Please use {d["command"]}bal or {d["command"]}wallet.'
                await customMessages.system_message(ctx=ctx, color_code=0, message=message, destination=0,
                                                    sys_msg_title=CONST_ACC_REG_STATUS)
            else:
                message = f'Account could not be registered at this moment please try again later.'
                await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                    sys_msg_title=CONST_ACC_REG_STATUS)
        else:
            message = f'You have already registered account into the system. Please use ***{d["command"]}bal*** or ' \
                      f'***{d["command"]}wallet*** to obtain details on balances and your profile'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=CONST_ACC_REG_STATUS)

    @commands.group()
    @commands.check(user_has_wallet)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def wallet(self, ctx):
        print(f'WALLET: {ctx.author} -> {ctx.message.content}')
        if ctx.invoked_subcommand is None:
            title = '__Available Wallets__'
            description = "All commands to check wallet details for each available cryptocurrency"
            list_of_values = [{"name": "Quick balance check", "value": f"{d['command']}bal"},
                              {"name": "How to deposit to Discord wallet", "value": f"{d['command']}wallet deposit"},
                              {"name": "How to deposit to Discord wallet", "value": f"{d['command']}wallet stats"},
                              {"name": "Get Stellar (XLM) wallet details", "value": f"{d['command']}wallet balance"}]

            await customMessages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                               destination=1)

    @wallet.command()
    async def stats(self, ctx):
        utc_now = datetime.utcnow()
        account_details = account_mng.get_account_details(discord_id=ctx.message.author.id)
        from pprint import pprint
        pprint(account_details)
        stellar_stats = account_details["xlmStats"]
        token_stats = account_details["clCoinStats"]
        transaction_stats = account_details["transactionCounter"]

        sum_sent = transaction_stats["sentTxCount"] + transaction_stats["multiTxCount"] + transaction_stats[
            "emojiTxCount"] + transaction_stats["rolePurchase"]

        acc_entry = Embed(title='__Account Statistics__',
                          colour=Colour.dark_blue(),
                          timestamp=utc_now)
        acc_entry.set_thumbnail(url=ctx.author.avatar_url)
        acc_entry.add_field(name=f'Account Owner',
                            value=f'{ctx.message.author} (ID: {ctx.message.author.id})',
                            inline=False)
        acc_entry.add_field(name=f':abacus: Sent ',
                            value=f'{sum_sent}')
        acc_entry.add_field(name=':outbox_tray:  Tx',
                            value=f'{transaction_stats["sentTxCount"]}')
        acc_entry.add_field(name=':inbox_tray:  Tx',
                            value=f'{transaction_stats["receivedCount"]}')
        acc_entry.add_field(name=':cloud_rain: Multi Tx',
                            value=f'{transaction_stats["multiTxCount"]}')
        acc_entry.add_field(name=':slight_smile: Tx',
                            value=f'{transaction_stats["emojiTxCount"]}')
        acc_entry.add_field(name=':man_juggling:  Purchase Tx',
                            value=f'{transaction_stats["rolePurchase"]}')
        await ctx.author.send(embed=acc_entry)

    @wallet.command()
    async def deposit(self, ctx):
        print(f'WALLET DEPOSIT: {ctx.author} -> {ctx.message.content}')
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
        print(f'WALLET BALANCE: {ctx.author} -> {ctx.message.content}')

        data = stellar.get_stellar_wallet_data_by_discord_id(discord_id=ctx.message.author.id)
        stellar_balance = get_normal(value=str(data['balance']),
                                     decimal_point=get_decimal_point('xlm'))
        stellar_to_usd = convert_to_usd(amount=float(stellar_balance), coin_name='stellar')
        if data:
            stellar_balance = get_normal(value=str(data['balance']),
                                         decimal_point=get_decimal_point('xlm'))

            balance_embed = Embed(title=f"Stellar wallet details for {ctx.message.author}",
                                  colour=Colour.green())
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
            title = f'__System Error__'
            message = f'You have not registered yourself into the system yet. Please head to one of the public ' \
                      f'channels, where Virtual Interactive Pilot is Accessible and  execute {d["command"]}register'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)

    @bal.error
    async def quick_bal_check_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__Balance check error__'
            message = f'In order to check balance you need to be registered into the system'
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
            message = f'In order to access your wallet you need to be first registered into payment system. You' \
                      f' can do that with {d["command"]}register!'
            await customMessages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                sys_msg_title=title)


def setup(bot):
    bot.add_cog(UserAccountCommands(bot))
