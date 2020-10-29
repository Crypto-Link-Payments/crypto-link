from discord import Embed, Colour, Member
from discord.ext import commands

from cogs.utils.customCogChecks import user_has_wallet, user_has_custodial, is_dm
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

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
    @commands.check(user_has_custodial)
    @commands.check(is_dm)
    async def account(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':joystick: __Available Custodial Account Commands__ :joystick: '
            description = "All commands to operate with custodial wallet system (Layer 2) in Crypto Link"
            list_of_values = [{"name": "Check Account Balance",
                               "value": f"`{self.command_string}custodial account balance`"}]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.dark_orange())

    @custodial.command()
    async def balance(self):
        # Get address from database
        # scan the newtwork and return data
        pass

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
