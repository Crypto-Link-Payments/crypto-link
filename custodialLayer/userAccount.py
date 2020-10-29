from discord import Embed, Colour, Member
from discord.ext import commands
from datetime import datetime
from cogs.utils.customCogChecks import user_has_wallet, user_has_custodial, is_dm
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers
from cogs.utils.monetaryConversions import scientific_conversion, get_rates, rate_converter

helper = Helpers()
custom_messages = CustomMessages()
hot_wallets = helper.read_json_file(file_name='hotWallets.json')
integrated_coins = helper.read_json_file(file_name='integratedCoins.json')
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_ACC_REG_STATUS = '__Account registration status__'
CONST_TRUST_ERROR = ':warning: __Trustline error__ :warning:'


def check(author):
    def inner_check(message):
        """
        Check for answering the verification message on withdrawal. Author origin
        """
        if message.author.id == author.id:
            return True
        else:
            return False

    return inner_check


class CustodialAccounts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.list_of_coins = list(integrated_coins.keys())
        self.backoffice = bot.backoffice
        self.server = self.backoffice.stellar_wallet.server

    @commands.group()
    @commands.check(user_has_wallet)
    async def custodial(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':joystick: __Available Custodial Wallet Commands__ :joystick: '
            description = "All commands to operate with custodial wallet system (Layer 2) in Crypto Link"
            list_of_values = [{"name": "Register for In-active Custodial Wallet ",
                               "value": f"`{self.command_string}custodial register`"},
                              {"name": "Create On-Chain Transactions",
                               "value": f"`{self.command_string}custodial transaction`"}
                              ]
            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.dark_orange())

    @custodial.command()
    @commands.check(is_dm)
    async def register(self, ctx):
        if not self.backoffice.custodial_manager.second_level_user_reg_status(user_id=ctx.author.id):
            details = self.backoffice.stellar_wallet.create_stellar_account()
            new_account = Embed(title=f':new: Layer 2 Account Registration System :new:',
                                colour=Colour.lighter_gray()
                                )
            new_account.add_field(name=f':map: Public Address :map: ',
                                  value=f'```{details["address"]}```',
                                  inline=False)
            new_account.add_field(name=f':key: Secret :key: ',
                                  value=f'```{details["secret"]}```',
                                  inline=False)
            new_account.add_field(name=f':warning: Important Message :warning:',
                                  value=f'Please store/backup account details somewhere safe and delete this embed on'
                                        f' Discord. Exposure of Secret to any other entity or 3rd party application'
                                        f' might result in loss of funds, or funds beeing stolen. In order to complete'
                                        f' registration for Second Layer please proceed to next step '
                                        f':arrow_double_down: ',
                                  inline=False)
            await ctx.author.send(embed=new_account, delete_after=360)

            veri_embed = Embed(title=":warning: Verification Required :warning:",
                               description="Please verify private key by providing last 4 characters of the secret "
                                           "key provided to you above. Enter it :arrow_double_down:")

            await ctx.channel.send(embed=veri_embed)
            verification_msg = await self.bot.wait_for('message', check=check(ctx.message.author))

            if verification_msg.content.upper() == details["secret"][-4:]:
                message = "You have successfully verified your secret key. Details of the wallet have been securely " \
                          "stored into database. In order for account to become active, you are required to deposit to " \
                          "it a least 1 XLM"
                await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_green(), destination=0,
                                                     sys_msg_title=':white_check_mark: Second Layer Account Create'
                                                                   ' :white_check_mark:',
                                                     message=message)

                # TODO encrypt data and store it to the database

            else:
                message = 'Last 4 characters of secret key do not match. Please initiate process all over again'
                await custom_messages.system_message(ctx=ctx, color_code=Colour.dark_red(), destination=0,
                                                     sys_msg_title=':white_check_mark: Second Layer Account Created'
                                                                   ' :white_check_mark:',
                                                     message=message)

    @custodial.group()
    # @commands.check(user_has_custodial)
    # @commands.check(is_dm)
    async def account(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':joystick: __Available Custodial Account Commands__ :joystick: '
            description = "All commands to operate with custodial wallet system (Layer 2) in Crypto Link"
            list_of_values = [{"name": "Check Account Balance",
                               "value": f"`{self.command_string}custodial account balance`"}]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.dark_orange())

    @account.command()
    async def info(self, ctx):
        # Get address from database
        #TODO get address from database
        public_key = "GB534PMUKKWBQDCNRAKCAMKTIUHFSUGU4YVO2UNA2ZV3XWGDEKS2J62C"
        data = self.server.accounts().account_id(account_id=public_key).call()
        from pprint import pprint
        pprint(data)
        signers = " ".join(
            [f':map:`{signer["key"]}`\n:key:`{signer["type"]}` | :scales:`{signer["weight"]}`\n================' for
             signer in data["signers"]])
        if data and 'status' not in data:
            dt_format = datetime.strptime(data["last_modified_time"], '%Y-%m-%dT%H:%M:%SZ')
            account_info = Embed(title=f':office_worker: Account Information :office_worker:',
                                 description="Bellow is up to date information on your custodial account state",
                                 colour=Colour.dark_blue(),
                                 timestamp=datetime.utcnow())
            account_info.set_author(name=f'{ctx.message.author} (ID: {ctx.message.author.id})',
                                    icon_url=self.bot.user.avatar_url,
                                    url=data["_links"]["self"]['href'])
            account_info.set_thumbnail(url=ctx.message.author.avatar_url)
            account_info.add_field(name=":map: Account Address :map:",
                                   value=f'```{public_key}```',
                                   inline=False)
            account_info.add_field(name=":calendar: Last Updated :calendar: ",
                                   value=f'`{dt_format}`',
                                   inline=True)
            account_info.add_field(name=":ledger: Last Ledger :ledger:",
                                   value=f'`{data["last_modified_ledger"]}`',
                                   inline=True)
            account_info.add_field(name="Thresholds",
                                   value=f'High: `{data["thresholds"]["high_threshold"]}`\n'
                                         f'Medium: `{data["thresholds"]["med_threshold"]}`\n'
                                         f'Low: `{data["thresholds"]["low_threshold"]}`')
            account_info.add_field(name=":money_with_wings: Sponsorship :money_with_wings: ",
                                   value=f'Sponsored: `{data["num_sponsored"]}`\n'
                                         f'Sponsoring: `{data["num_sponsoring"]}`')
            account_info.add_field(name=":triangular_flag_on_post:  Flags :triangular_flag_on_post: ",
                                   value=f'Immutable: `{data["flags"]["auth_immutable"]}`\n'
                                         f'Required: `{data["flags"]["auth_required"]}`\n'
                                         f'Revocable: `{data["flags"]["auth_revocable"]}`\n')
            account_info.add_field(name=f':pen_ballpoint: Account Signers :pen_ballpoint: ',
                                   value=signers,
                                   inline=False)
            account_info.add_field(name=f':sunrise:  Horizon Access :sunrise: ',
                                   value=f'[Effects]({data["_links"]["effects"]["href"]}) | '
                                         f'[Offers]({data["_links"]["offers"]["href"]}) | '
                                         f'[Operations]({data["_links"]["operations"]["href"]}) | '
                                         f'[Payments]({data["_links"]["payments"]["href"]}) | '
                                         f'[Trades]({data["_links"]["payments"]["href"]}) | '
                                         f'[Transactions]({data["_links"]["transactions"]["href"]})',
                                   inline=False)
            await ctx.author.send(embed=account_info)

            # Creates embed object to be populated later on if user has more than XLM in wallet

            if len(data["balances"]) > 1:
                gems_nfo = Embed(title=f'Other Balances',
                                 color=Colour.dark_blue())

            for coin in data["balances"]:
                if not coin.get('asset_code'):
                    cn = 'XLM'
                else:
                    cn = coin["asset_code"]

                if cn == "XLM":
                    rates = get_rates(coin_name=f'stellar')
                    in_eur = rate_converter(float(coin['balance']), rates["stellar"]["eur"])
                    in_usd = rate_converter(float(coin['balance']), rates["stellar"]["usd"])
                    in_btc = rate_converter(float(coin['balance']), rates["stellar"]["btc"])
                    in_eth = rate_converter(float(coin['balance']), rates["stellar"]["eth"])
                    in_rub = rate_converter(float(coin['balance']), rates["stellar"]["rub"])
                    in_ltc = rate_converter(float(coin['balance']), rates["stellar"]["ltc"])

                    xlm_nfo = Embed(title=f'XLM Wallet Balance Details',
                                    description=f'```{coin["balance"]} XLM```',
                                    color=Colour.dark_blue())
                    xlm_nfo.add_field(name=f':flag_us: USA',
                                      value=f'$ {scientific_conversion(in_usd, 4)}')
                    xlm_nfo.add_field(name=f':flag_eu: EUR',
                                      value=f'€ {scientific_conversion(in_eur, 4)}')
                    xlm_nfo.add_field(name=f':flag_ru:  RUB',
                                      value=f'₽ {scientific_conversion(in_rub, 4)}')
                    xlm_nfo.add_field(name=f'BTC',
                                      value=f'₿ {scientific_conversion(in_btc, 8)}')
                    xlm_nfo.add_field(name=f'ETH',
                                      value=f'Ξ {scientific_conversion(in_eth, 8)}')
                    xlm_nfo.add_field(name=f'LTC',
                                      value=f'Ł {scientific_conversion(in_ltc, 8)}')
                    xlm_nfo.set_footer(text='Conversion rates provided by CoinGecko',
                                       icon_url="https://static.coingecko.com/s/thumbnail-007177f3eca19695592f0b8b0eabbdae282b54154e1be912285c9034ea6cbaf2.png")
                    await ctx.author.send(embed=xlm_nfo)

                else:
                    gems_nfo.add_field(name=f':gem: {cn} :gem:',
                                       value=f"{coin['balance']}")

            if len(data["balance"]) > 1:
                await ctx.author.send(embed=gems_nfo)
        else:
            sys_msg_title = 'Stellar Wallet Query Server error'
            message = 'Status of the wallet could not be obtained at this moment'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=sys_msg_title)

    @custodial.group()
    @commands.check(user_has_custodial)
    async def tx(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':joystick: __Available Transaction Commands__ :joystick: '
            description = "All commands to operate with custodial wallet system (Layer 2) in Crypto Link"
            list_of_values = [{"name": "Discord related payments",
                               "value": f"`{self.command_string}custodial transaction user`"},
                              {"name": "Non-Discord related payments",
                               "value": f"`{self.command_string}custodial transaction address`"}
                              ]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.dark_orange())

    # @tx.command()
    # async def tx(self, ctx, amount, token, discord_user: Member, layer: int = None):
    #     # Check If user is registered
    #     # Check layers of transaction
    #     #
    #     pass
    #
    # @tx.command()
    # async def address(self, ctx, amount, token, discord_user: Member, layer: int = None):
    #     # Check If user is registered
    #     # Check layers of transaction
    #     #
    #     pass

    @custodial.error
    async def cust_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f"In order to be able to use custodial wallet (Layer 2 wallet) please register first into the " \
                      f"Crypto Link system with {self.command_string}register"
            title = f'**__User not found__** :clipboard:'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @account.error
    async def acc_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            print(error)
            message = f"In order to be able to access commands under command group" \
                      f" `{self.command_string}custodial account` " \
                      f" user is required to:\n" \
                      f"- have registered custodial wallet into the system\n" \
                      f"- use command through DM with the Crypto Link"
            title = f'**__{self.command_string} custodial account error__**'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)

    @register.error
    async def reg_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f"You are allowed to register for Second Layer account only through the **direct message**" \
                      f" with Crypto Link."
            title = f'**__Wrong Channel Type__**'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(CustodialAccounts(bot))
