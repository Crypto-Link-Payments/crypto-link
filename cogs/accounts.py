from datetime import datetime
from nextcord import Embed, Colour, File, Interaction, slash_command, SlashOption
from nextcord.ext import commands, application_checks
import cooldowns
from utils.customCogChecks import has_wallet_inter_check
from cogs.utils.monetaryConversions import get_rates, rate_converter
from re import sub
from cogs.utils.systemMessaages import CustomMessages
import os

custom_messages = CustomMessages()
# Move this to class
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_ACC_REG_STATUS = '__Account registration status__'
CONST_TRUST_ERROR = ':warning: __Trustline error__ :warning:'


class UserAccountCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()

    @staticmethod
    def clean_qr_image(author_id):
        if os.path.exists(f'{author_id}.png'):
            try:
                os.remove(f'{author_id}.png')
            except Exception as e:
                print(f'Exception: {e}')
        else:
            print("The file does not exist")

    @slash_command(description="Basic details about your Crypto Link account", dm_permission=False)
    @application_checks.check(has_wallet_inter_check())
    @cooldowns.cooldown(1, 5, cooldowns.SlashBucket.author)
    async def me(self,
                 interaction: Interaction):
        utc_now = datetime.utcnow()
        wallet_data = self.backoffice.wallet_manager.get_full_details(user_id=interaction.user.id)

        try:
            xlm_balance = float(wallet_data["xlm"]) / (10 ** 7)
        except ZeroDivisionError:
            xlm_balance = 0

        rates = get_rates(coin_name='stellar')
        acc_details = Embed(title=f':office_worker: {interaction.user} :office_worker:',
                            description=f' ***__Basic details about your Crypto Link account__*** ',
                            colour=Colour.dark_orange(),
                            timestamp=utc_now)
        acc_details.add_field(name=":map: Wallet Address :map: ",
                              value=f"```{self.backoffice.stellar_wallet.public_key}```")
        acc_details.add_field(name=":compass: MEMO :compass: ",
                              value=f"```{wallet_data['depositId']}```",
                              inline=False)
        acc_details.add_field(name=':moneybag: Stellar Lumen (XLM) Balance :moneybag: ',
                              value=f'`{xlm_balance:.7f}`',
                              inline=False)

        if rates and float(wallet_data["xlm"]) > 0:
            in_eur = rate_converter(xlm_balance, rates["stellar"]["eur"])
            in_usd = rate_converter(xlm_balance, rates["stellar"]["usd"])
            in_btc = rate_converter(xlm_balance, rates["stellar"]["btc"])
            in_eth = rate_converter(xlm_balance, rates["stellar"]["eth"])
            in_rub = rate_converter(xlm_balance, rates["stellar"]["rub"])
            in_ltc = rate_converter(xlm_balance, rates["stellar"]["ltc"])
            acc_details.add_field(name=f':flag_us: USA',
                                  value=f'`$ {in_usd:.4f}`')
            acc_details.add_field(name=f':flag_eu: EUR',
                                  value=f'`€ {in_eur:.4f}`')
            acc_details.add_field(name=f':flag_ru:  RUB',
                                  value=f'`₽ {in_rub:.4f}`')
            acc_details.add_field(name=f'BTC',
                                  value=f'`₿ {in_btc:.8f}`')
            acc_details.add_field(name=f'ETH',
                                  value=f'`Ξ {in_eth:.8f}`')
            acc_details.add_field(name=f'LTC',
                                  value=f'`Ł {in_ltc:.8f}`')

        acc_details.add_field(name=f'More On Stellar Lumen (XLM)',
                              value=f'[Stellar](https://www.stellar.org/)\n'
                                    f'[Stellar Foundation](https://www.stellar.org/foundation)\n'
                                    f'[Stellar Lumens](https://www.stellar.org/lumens)\n'
                                    f'[CMC](https://coinmarketcap.com/currencies/stellar/)\n'
                                    f'[Stellar Expert](https://stellar.expert/explorer/public)')
        acc_details.set_footer(text='Conversion rates are provided by CoinGecko')
        await interaction.response.send_message(embed=acc_details, delete_after=15, ephemeral=True)

    @slash_command(description="Register to Crypto Link", dm_permission=False)
    @cooldowns.cooldown(1, 5, cooldowns.SlashBucket.guild)
    async def register(self,
                       interaction: Interaction):
        if not self.backoffice.account_mng.check_user_existence(user_id=interaction.user.id):
            if self.backoffice.account_mng.register_user(discord_id=interaction.user.id,
                                                         discord_username=f'{interaction.user}'):
                message = f'Congratulations, your account has been successfully created.' \
                          f' You can access your wallet via the following command:\n' \
                          f'/wallet'
                await custom_messages.system_message(interaction=interaction, color_code=0, message=message,
                                                     destination=0,
                                                     sys_msg_title=CONST_ACC_REG_STATUS)

                # Update guild stats on registered users
                await self.backoffice.stats_manager.update_registered_users(guild_id=interaction.guild.id)

            else:
                message = f'Oh no! Something went wrong.\n' \
                          f'Registration failed, please try again later.\n' \
                          f'If the issue persists please contact one of the developers'
                await custom_messages.system_message(interaction=interaction, color_code=1, message=message,
                                                     destination=0,
                                                     sys_msg_title=CONST_ACC_REG_STATUS)
        else:
            message = f'You already have an account! Please use ' \
                      f'***/wallet*** to access your wallet details.'
            await custom_messages.system_message(interaction=interaction, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_ACC_REG_STATUS)

    @slash_command(description="Wallet operations", dm_permission=False)
    @application_checks.check(has_wallet_inter_check())
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def wallet(self,
                     interaction: Interaction,
                     ):
        pass

    @wallet.subcommand(name="help", description="Help commands for /wallet")
    @application_checks.check(has_wallet_inter_check())
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def help(self,
                   interaction: Interaction
                   ):
        title = ':joystick: __Available Wallet Commands__ :joystick: '
        description = "Here is a summary of wallet related commands.\n"
        list_of_values = [{"name": " :woman_technologist: Get AFull Account Balance Report :woman_technologist:  ",
                           "value": f"```/wallet balance```\n"},
                          {"name": ":bar_chart: Get Your Wallet Statistics :bar_chart:",
                           "value": f"```/wallet stats <asset_code=optional for non XLM>```"},
                          {"name": ":inbox_tray: Get Deposit Instructions :inbox_tray:",
                           "value": f"```/wallet deposit```"},
                          {"name": ":outbox_tray: Withdraw from Crypto Link :outbox_tray: ",
                           "value": f"```/wallet withdraw <amount> <asset code> <address> <memo=Optional>```"}]
        await custom_messages.embed_builder(interaction=interaction, title=title,
                                            description=description, data=list_of_values,
                                            destination=1, c=Colour.dark_orange())

    @wallet.subcommand(name="stats", description="Fetch wallet stats")
    @application_checks.check(has_wallet_inter_check())
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def stats(self,
                    interaction: Interaction,
                    token: str = SlashOption(description="Balance for token", required=False, default='xlm')
                    ):
        token = token.lower()
        # Pull all the registered coin codes from database for further check
        supported_tokens = [sup["assetCode"].lower() for sup in
                            self.bot.backoffice.token_manager.get_registered_tokens()]

        utc_now = datetime.utcnow()
        if token.lower() == 'xlm':
            tokens = [x['assetCode'] for x in self.bot.backoffice.token_manager.get_registered_tokens() if
                      x['assetCode'] != 'xlm']
            available_stats = ' '.join([str("***" + elem + "***" + ", ") for elem in tokens]).capitalize()
            account_details = self.backoffice.account_mng.get_account_stats(
                discord_id=interaction.message.author.id)
            stats_info = Embed(title=f':bar_chart: Wallet level 1 statistics :bar_chart: ',
                               description='Below you will find a summary of stats which are '
                                           'automatically counted upon successful'
                                           ' execution of the commands dedicated to wallet level :one: ',
                               colour=Colour.lighter_grey())
            stats_info.add_field(name=f":symbols: Symbols :symbols: ",
                                 value=f':incoming_envelope: -> `SUM of total incoming transactions` \n'
                                       f':money_with_wings: -> `SUM of total amount sent per currency` \n'
                                       f':envelope_with_arrow:  -> `SUM of total outgoing transactions`\n'
                                       f':money_mouth: -> `SUM of total amount received per currency` \n'
                                       f':man_juggling: -> `SUM of total roles purchased through merchant system`\n'
                                       f':money_with_wings: -> `SUM of total amount spent on the merchant system` \n')
            stats_info.add_field(name=f':warning: Access token stats :warning: ',
                                 value=f'Use the same command and add an asset code. All available currencies are: '
                                       f'{available_stats}',
                                 inline=False)
            await interaction.user.send(embed=stats_info)
            await custom_messages.stellar_wallet_overall(interaction=interaction, coin_stats=account_details,
                                                         utc_now=utc_now)
        else:
            if token in supported_tokens:
                token_stats = self.backoffice.account_mng.get_token_stats(discord_id=interaction.message.author.id,
                                                                          token=token.lower())
                if token_stats:
                    token_stats_info = Embed(title=f'Details for token {token.upper()}',
                                             description=f'Below are statistical details on account activities '
                                                         f'for the selected token, till {utc_now} (UTC)',
                                             colour=Colour.gold())

                    for k, v in token_stats[token.lower()].items():
                        itm = sub(r"([A-Z])", r" \1", k).split()
                        item = ' '.join([str(elem) for elem in itm]).capitalize()
                        if k in ["depositsCount", "publicTxSendCount", "privateTxSendCount", "withdrawalsCount"]:
                            token_stats_info.add_field(name=f'{item}',
                                                       value=f'{v}')
                        else:
                            token_stats_info.add_field(name=f'{item}',
                                                       value=f'{v:,.7f} {token.upper()}')

                    await interaction.response.send_message(embed=token_stats_info, delete_after=15, ephemeral=True)

                else:
                    title = '__Token statistics__'
                    message = f'You have no activity marked in the wallet for token {token.upper()}'
                    await custom_messages.system_message(interaction=interaction, color_code=1, message=message,
                                                         destination=1,
                                                         sys_msg_title=title)
            else:
                title = '__Token not supported__'
                message = f'Token {token.upper()} is not integrated in {self.bot.user.name}. Currently available' \
                          f' tokens are:\n {", ".join([str(elem) for elem in supported_tokens]).capitalize()}'
                await custom_messages.system_message(interaction=interaction, color_code=1, message=message,
                                                     destination=1,
                                                     sys_msg_title=title)

    # @wallet.group()
    # async def deposit(self, ctx):
    #     """
    #     Returns deposit information to user
    #     """
    #     if ctx.invoked_subcommand is None:
    #         user_profile = self.backoffice.account_mng.get_user_memo(user_id=ctx.message.author.id)
    #         if user_profile:
    #             coins_string = ', '.join(
    #                 [x["assetCode"].upper() for x in self.bot.backoffice.token_manager.get_registered_tokens()])
    #
    #             description = ' :warning: To top up your Discord wallets, you will need to send from your preferred' \
    #                           ' wallet(GUI, CLI) to the address and deposit ID provided below. Of them will result in ' \
    #                           'funds being lost to which staff of Launch Pad Investments is not ' \
    #                           'responsible for. :warning:'
    #
    #             deposit_embed = Embed(title='How to deposit',
    #                                   colour=Colour.dark_orange(),
    #                                   description=description)
    #             deposit_embed.add_field(name=':gem: Supported Cryptocurrencies/Tokens for deposit:gem: ',
    #                                     value=f'```{coins_string}```',
    #                                     inline=False)
    #             deposit_embed.add_field(
    #                 name=f' {CONST_STELLAR_EMOJI} Deposit Details {CONST_STELLAR_EMOJI}',
    #                 value=f'\n:map: Public Address :map: \n'
    #                       f'```{self.backoffice.stellar_wallet.public_key}```\n'
    #                       f':compass: MEMO :compass:\n'
    #                       f'```{user_profile["stellarDepositId"]}```',
    #                 inline=False)
    #             deposit_embed.add_field(name=':warning: **__Warning__** :warning:',
    #                                     value='Be sure to include and provide appropriate  **__MEMO__** as text and Wallet '
    #                                           'address for each currency , otherwise your deposit will be lost!',
    #                                     inline=False)
    #             deposit_embed.add_field(name=":printer: QR Code :printer: ",
    #                                     value=f'Below is your personal QR code including your deposit address and '
    #                                           f'MEMO. Scan it with mobile application supporting QR. Be sure to '
    #                                           f'recheck the data once you scan it.',
    #                                     inline=False)
    #
    #             memo = user_profile["stellarDepositId"]
    #             uri = self.backoffice.stellar_wallet.generate_uri(address=self.backoffice.stellar_wallet.public_key,
    #                                                               memo=memo)
    #             image = pyqrcode.create(content=uri, error='L')
    #             image.png(file=f'{ctx.message.author.id}.png', scale=6, module_color=[0, 255, 255, 128],
    #                       background=[17, 17, 17],
    #                       quiet_zone=4)
    #             qr_to_send = File(f'{ctx.message.author.id}.png')
    #
    #             deposit_embed.set_image(url=f"attachment://{ctx.message.author.id}.png")
    #             deposit_embed.set_footer(text=f'{self.command_string}wallet deposit qr -> Only QR')
    #             await ctx.author.send(file=qr_to_send, embed=deposit_embed)
    #
    #             self.clean_qr_image(author_id=ctx.message.author.id)
    #         else:
    #             title = '__Deposit information error__'
    #             message = f'Deposit details for your account could not be obtained at this moment from the system. ' \
    #                       f'Please try again later, or contact one of the staff members. '
    #             await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
    #                                                  sys_msg_title=title)
    #
    # @deposit.command()
    # async def qr(self, ctx):
    #     """
    #     Send the QR only to user
    #     """
    #     user_profile = self.backoffice.account_mng.get_user_memo(user_id=ctx.message.author.id)
    #     if user_profile:
    #         coins_string = ', '.join(
    #             [x["assetCode"].upper() for x in self.bot.backoffice.token_manager.get_registered_tokens()])
    #
    #         deposit_embed = Embed(title='Deposit QR code',
    #                               colour=Colour.dark_orange())
    #         deposit_embed.add_field(name=':gem: Supported Cryptocurrencies and tokens to be deposited:gem: ',
    #                                 value=f'```{coins_string}```',
    #                                 inline=False)
    #         memo = user_profile["stellarDepositId"]
    #         uri = self.backoffice.stellar_wallet.generate_uri(address=self.backoffice.stellar_wallet.public_key,
    #                                                           memo=memo)
    #         image = pyqrcode.create(content=uri, error='L')
    #         image.png(file=f'{ctx.message.author.id}.png', scale=6, module_color=[0, 255, 255, 128],
    #                   background=[17, 17, 17],
    #                   quiet_zone=4)
    #         qr_to_send = File(f'{ctx.message.author.id}.png')
    #
    #         deposit_embed.set_image(url=f"attachment://{ctx.message.author.id}.png")
    #         deposit_embed.set_footer(text=f'{self.command_string}wallet deposit qr -> Only QR')
    #         await ctx.author.send(file=qr_to_send, embed=deposit_embed)
    #         self.clean_qr_image(author_id=ctx.message.author.id)
    #     else:
    #         title = '__Deposit information error__'
    #         message = f'Deposit details for your account could not be obtained at this moment from the system. ' \
    #                   f'Please try again later, or contact one of the staff members. '
    #         await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
    #                                              sys_msg_title=title)
    #
    # @wallet.command(aliases=['bal', 'balances', 'b'])
    # async def balance(self, ctx):
    #     user_balances = self.backoffice.wallet_manager.get_balances(user_id=ctx.message.author.id)
    #     bag = [k for k, v in user_balances.items() if v > 0]
    #     if bag:
    #         # initiate Discord embed
    #         balance_embed = Embed(title=f":office_worker: Details for {ctx.message.author} :office_worker:",
    #                               timestamp=datetime.utcnow(),
    #                               colour=Colour.dark_orange())
    #
    #         for k, v in user_balances.items():
    #             if v > 0:
    #                 balance_embed.add_field(
    #                     name=f"{k.upper()}",
    #                     value=f'```{v / (10 ** 7):,.7f} {k.upper()}```',
    #                     inline=False)
    #             else:
    #                 pass
    #         await ctx.author.send(embed=balance_embed)
    #     else:
    #         title = 'Crypto Link Wallet is empty__'
    #         message = f'Your wallet is empty'
    #         await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
    #                                              sys_msg_title=title)

    @me.error
    async def quick_acc_check_error(self, interaction, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__Balance check error__'
            message = f'In order to check balance you need to be registered into the system'
            await custom_messages.system_message(interaction=interaction, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @register.error
    async def register_error(self, interaction, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__/register error__'
            message = f'You can not register over DM with the bot. Please head to one of the channels on Discord ' \
                      f' server where Crypto Link is present and execute command: \n{self.command_string}register'
            await custom_messages.system_message(interaction=interaction, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @wallet.error
    async def wallet_error(self, interaction, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__/wallet Error__'
            message = f'In order to access your wallet you need to be first registered into payment system. You' \
                      f' can do that with {self.command_string}register!'
            await custom_messages.system_message(interaction=interaction, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(UserAccountCommands(bot))
