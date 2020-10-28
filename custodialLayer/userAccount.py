from discord import Embed, Colour
from discord.ext import commands

from cogs.utils.customCogChecks import user_has_wallet, user_has_custodial
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

helper = Helpers()
custom_messages = CustomMessages()
hot_wallets = helper.read_json_file(file_name='hotWallets.json')
integrated_coins = helper.read_json_file(file_name='integratedCoins.json')
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_ACC_REG_STATUS = '__Account registration status__'
CONST_TRUST_ERROR = ':warning: __Trustline error__ :warning:'


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
            list_of_values = [{"name": " :woman_technologist: Get Full Account Balance Report :woman_technologist:  ",
                               "value": f"`{self.command_string}custodial register`"}]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.dark_orange())

    @custodial.command()
    async def register(self, ctx):
        if not self.backoffice.custodial_manager.second_level_user_reg_status(user_id=ctx.author.id):
            details = self.backoffice.stellar_wallet.create_stellar_account()
            new_account = Embed(title=f':new: Stellar Account Created :new:',
                                description=f':warning: You have successfully created new account on {details["network"]}. Do'
                                            f' not deposit real XLM as this account has been created on testnet. '
                                            f'Head to [Stellar Laboratory](https://laboratory.stellar.org/#account-creator?network=test)'
                                            f' and use Friend bot to activate account :warning:',
                                colour=Colour.lighter_gray()
                                )
            new_account.add_field(name=f':map: Public Address :map: ',
                                  value=f'```{details["address"]}```',
                                  inline=False)
            new_account.add_field(name=f':key: Secret :key: ',
                                  value=f'```{details["secret"]}```',
                                  inline=False)
            new_account.add_field(name=f':warning: Important Message:warning:',
                                  value=f'Please store/backup account details somewhere safe and delete this embed on'
                                        f' Discord. Exposure of Secret to any other entity or 3rd party application'
                                        f'might result in loss of funds. Your secret key has been successfully '
                                        f'encrypted and stored in Crypto Link Database.',
                                  inline=False)
            await ctx.author.send(embed=new_account, delete_after=360)

    @custodial.group()
    @custodial.check(user_has_custodial)
    async def account(self):
        pass

    @custodial.command()
    async def balance(self):
        pass

    @custodial.group()
    @custodial.check(user_has_custodial)
    async def send(self):
        pass

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
                      f" you need to first register a custodial wallet into the system with " \
                      f"`{self.command_string}custodial register"
            title = f'**__Custodial wallet not registered__** :clipboard:'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(CustodialAccounts(bot))
