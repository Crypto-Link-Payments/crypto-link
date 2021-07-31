"""
COGS: Help commands for the payment services
"""
import discord
from discord.ext import commands
from discord import Colour
from utils.tools import Helpers
from utils.customCogChecks import is_owner, is_public
from cogs.utils.systemMessaages import CustomMessages

custom_messages = CustomMessages()

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'


class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.helper = Helpers()
        self.command_string = bot.get_command_str()

    @commands.group()
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':sos: __Available Help Commands__ :sos: '
            description = f"Available sub commands for `{self.command_string}help`"
            list_of_values = [
                {"name": " :mega: About the Crypto Link :mega:",
                 "value": f"```{self.command_string}about```"},
                {"name": ":rocket: How to get started :rocket:",
                 "value": f"```{self.command_string}get_started```\n"
                          f"`Aliases: start`"},
                {"name": " :moneybag: Wallet level system information :moneybag: ",
                 "value": f"```{self.command_string}help levels```"},
                {"name": ":coin: Available Currencies :coin:",
                 "value": f"```{self.command_string}help currencies```\n"
                          f"`Aliases: tokens, coins`"},
                {"name": ":office_worker: Accessing personal account :office_worker:",
                 "value": f"```{self.command_string}help account```\n"
                          f"`Aliases: acc, user, profile, wallet`"},
                {"name": ":money_with_wings: P2P transaction execution :money_with_wings:",
                 "value": f"```{self.command_string}help transactions```\n"
                          f"`Aliases: tx, pay`"},
                {"name": ":crown: Guild Owner Commands :crown:",
                 "value": f"```{self.command_string}help owner```"},
                {"name": ":sunrise:  Query Stellar Horizon :sunrise: ",
                 "value": f"```{self.command_string}help horizon```\n"
                          f"`Aliases: hor, network, explorer`"},
            ]
            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.blue())

    @commands.command()
    async def about(self, ctx):
        """
        Command which returns information on About the system
        :param ctx:
        :return:
        """
        title = ':mega: __Welcome to Crypto Link__ :mega: '
        description = "What Crypto Link is and what it offers"
        list_of_values = [
            {"name": ":information_source: About :information_source: ",
             "value": 'Crypto Link is a multi-functional & multi-guild Discord bot serving as a bridge between the '
                      'Stellar Ecosystem and Discord users. Being built ontop of the Stellar Blockchain, it utilizes '
                      'the native token, Stellar Lumen (a.k.a XLM) and tokens issued on Stellar chain, '
                      'allowing for execution of Peer to Peer transactions amongst users, monetization'
                      ' opportunities for Discord guild owners and project promotions/crowdfunding/ICOs activities'
                      ' at low costs for aspiring fintech-companies building with the help of Stellar.'},
            {"name": ":moneybag: Wallet Types :moneybag:  ",
             "value": f'Crypto Link has integrated and interconnected system of custodial, noncustodial wallets.'
                      f' To find more information and explanation '
                      f'please use `{self.command_string}help wallets`. Each user is required to register for custodial '
                      f'system in order to be able to use noncustodial.'},

            {"name": ":money_with_wings: Instant Peer to Peer feeless transactions :money_with_wings:  ",
             "value": f"Users are able to execute instant peer-2-peer transactions without fees either with the Stellar"
                      f" native currency XLM or integrated tokens. Currently system supports public and private types."
                      f" For full list of supported currencies please use command {self.command_string}currencies"},

            {"name": ":convenience_store: Merchant system :convenience_store: ",
             "value": f"Discord Guild owners can monetize roles in various lengths and "
                      f"values and make them available for purchase. Once role is purchased, Crypto Link will handle"
                      f" micro management tasks (role management, transfer of funds, role monitoring and its removal "
                      f"uppon expiration) on its own, saving owners a lot of time."},

            {"name": ":satellite_orbital: Crypto Link Up-Link system :satellite_orbital:  ",
             "value": f"Owners can as well set-up Up-Link which provides opportunity to monitor Crypto Link System"
                      f" activities. Serving as an 'Network Explorer' users are able to see activites happening"
                      f" across other guilds who have integrated the system"},

            {"name": ":postal_horn: ICO's and Project promotions :postal_horn: ",
             "value": f'Integrated support for Stellar Native Crypto Currency and its tokens provides as well '
                      f'possibility for Crypto Link to be utilized as one of the channels for running '
                      f'ICOs/Crowdfundings or simple project promotion activities. If you would like to know more '
                      f'or would like to get in touch with us, please write us on'
                      f' ***__cryptolinkpayments@gmail.com__***, open issue on Github or contact us directly over '
                      f'Discord Crypto Link Community.'},
            {"name": ":sunrise: Queries to Horizon Network from Discord :sunrise: ",
             "value": f'Crypto Link has integrated as well access to Stellar Horizon which is  client-facing API server for '
                      f'the Stellar ecosystem. Discord Users can now execute queries to it straight from Discord'
                      f' through execution of specific Discord Commands. To find and familiarize yourself with Horizon'
                      f' initiate `{self.command_string}help horizon` with the bot or jump straight into it '
                      f' with `{self.command_string}horizon`.'},
            {"name": ":placard: Further information and links:placard: ",
             "value": f'[Homepage](https://cryptolink.carrd.co/) \n'
                      f'[Github](https://github.com/launch-pad-investments/crypto-link) \n'
                      f'[Twitter](https://twitter.com/CryptoLink8)'},
        ]

        await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                            destination=1, c=Colour.blue())

    @commands.command(aliases=["start"])
    async def get_started(self, ctx):
        """
        How to get started with the payment system
        :param ctx: Discord Context
        :return: Discord Embed
        """
        start_embed = discord.Embed(title=f':rocket: Launch {self.bot.user.name} Experience :rocket:',
                                    colour=Colour.blue())
        start_embed.add_field(name=':one: Register yourself custodial wallet :one:',
                              value=f'In order for you to be able to make peer to peer transactions and use merchant'
                                    f' system, you must have registered at least custodial wallet.\n'
                                    f'You can do that by executing command `{self.command_string}register` on any '
                                    f'public Discord channel where Crypto Link has access to .\n'
                                    f'Once successful, you will create personal wallet with details which you can use '
                                    f' to move or deposit funds. To further familiarize yourself with other'
                                    f' commands use `{self.command_string}help`',
                              inline=False)
        start_embed.add_field(name=':two: Get Deposit Details :two:',
                              value=f'Get deposit details of your Discord wallet with `{self.command_string}wallet'
                                    f' deposit` and deposit XLM or any other supported Stellar native token. '
                                    f'Please use `{self.command_string}help currencies` to check all available '
                                    f'tokens on the system besides XLM',
                              inline=False)
        start_embed.add_field(name=':three: Make P-2-P Transaction :three:',
                              value=f'`{self.command_string}send <@discord.Member> <amount> <ticker>`\n'
                                    f'Example: `{self.command_string}send @animus 10 xlm`',
                              inline=False)
        start_embed.add_field(name=':sos: Explore Crypto Link :sos: ',
                              value=f'```{self.command_string}help```',
                              inline=False)

        await ctx.author.send(embed=start_embed)

    @help.command(aliases=['tokens', 'coins'])
    async def currencies(self, ctx):
        """
        Returns representation of all available currencies available to be utilized int transactions
        :return: Discord Embed
        """

        available = discord.Embed(title=':coin: Integrated coins and tokens :coin: ',
                                  description='Below is a list of all available currencies for making peer 2 peer'
                                              ' transactions or to be used with merchant system',
                                  colour=Colour.blue())
        await ctx.author.send(embed=available)

        #TODO update to pull supported from DB
        # for coin in coins:
        #     available.add_field(name=f'====================================',
        #                         value='\u200b')
        #     available.add_field(
        #         name=f"{coins[coin]['emoji']} {coins[coin]['name']} {coins[coin]['emoji']}",
        #         value=f'`Symbol:` ***{coins[coin]["ticker"]}***\n'
        #               f'`Issuer:` ***{coins[coin]["assetIssuer"]}***\n'
        #               f'`Decimals:` ***{coins[coin]["decimal"]}***\n'
        #               f'`Min. Withdrawal:` ***{coins[coin]["minimumWithdrawal"] / 10000000}***\n'
        #               f'`Expert Link:` ***{coins[coin]["expert"]}***\n'
        #               f'`Homepage:` ***{coins[coin]["homepage"]}***',
        #         inline=False)
        await ctx.author.send(embed=available)

    @help.command()
    async def wallets(self, ctx):
        title = ':office_worker: __Multi Level Wallet system__:office_worker: '
        description = "Explanation of the multi-level wallet system"
        list_of_values = [
            {"name": ":one: Custodial Wallet :one: ",
             "value": f"Registration for `custodial wallet level` is mandatory for all users who would like to "
                      f"use all the functions Crypto Link has to offer. Wallet operates based on MEMO when depositing. "
                      f"This allows anyone to receive transaction from sender "
                      f"instantly, even doe if recipient has not registered yet into the system. Custodial wallet is  "
                      f"is automatically created and all actions connected with it do not require private key "
                      f"to be used for signing. In order to fully protect your wallet, please activate 2FA for Discord "
                      f"account. "},
            {"name": ":two: Non-Custodial wallet support :two: ",
             "value": "`Noncustodial wallet` which utilizes XDR envelopes to make XDR envelopes to be signed either through"
                      " [Stellar Laboratory](https://laboratory.stellar.org/#?network=public) or any other application"
                      " allowing to import XDR or than straight through "
                      "Discord. the only details which are stored into Crypto Link system are unique user id and "
                      "user public address so XDR can be successfully built and that others can efficiently transfer "
                      "tokens to you from Custodial to Non Custodial wallet"
                      f"```Access it with: {self.command_string}three```"}
        ]

        await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                            destination=1, c=Colour.blue())

    @help.command(aliases=['tx', 'pay'])
    async def transactions(self, ctx):
        title = ':money_with_wings: __How to make transactions/payments on level 1__ :money_with_wings: '
        description = f"Forms of transactions available on {self.bot.user.name}"
        list_of_values = [
            {"name": f":cowboy: Public P-2-P transactions :cowboy:",
             "value": f"`{self.command_string}send <@Discord User> <amount> <ticker> <message=optional>`\n"
                      f"__Example__:`{self.command_string}send 10 xlm @animus Have a nice day`"},
            {"name": f":detective: Private transactions :detective:  ",
             "value": f"`{self.command_string}private <@Discord User> <amount> <ticker> <message=optional>`\n"
                      f"__Example__: `{self.command_string}private 10 xlm @animus Dont tell anyone`"}
        ]

        await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                            destination=1, c=Colour.blue())

    @help.command(aliases=['acc', 'user', 'profile', 'wallet'])
    async def account(self, ctx):
        title = ':office_worker: __Obtain information on personal account of level 1__:office_worker: '
        description = "Below are presented all currencies available for P2P transactions"
        list_of_values = [
            {"name": ":credit_card: Get balance information :credit_card: ",
             "value": f"```{self.command_string}me```"},
            {"name": ":moneybag: Access wallet commands :moneybag: ",
             "value": f"```{self.command_string}wallet```"},
            {"name": " :woman_technologist: Get full account balance report :woman_technologist:  ",
             "value": f"```{self.command_string}wallet balance```"},
            {"name": ":bar_chart: Wallet Statistics :bar_chart:",
             "value": f"```{self.command_string}wallet stats```"},
            {"name": ":inbox_tray: Get instructions on how to deposit :inbox_tray:",
             "value": f"```{self.command_string}wallet deposit```"},
            {"name": ":outbox_tray: Withdrawal instructions :outbox_tray: ",
             "value": f"```{self.command_string}withdraw```"}]

        await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                            destination=1, c=Colour.blue())

    @help.group()
    @commands.check(is_public)
    @commands.check(is_owner)
    async def owner(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':crown: __Available Commands for guild owners__ :crown: '
            description = "All available commands for you to familiarize yourself with payment and merchant " \
                          "services available as owner of the community."

            list_of_values = [
                {"name": f":scales:  Register Guild into System :scales: ",
                 "value": f"```{self.command_string}owner register```"},
                {"name": f":bank: Guild wallet commands :bank:",
                 "value": f"```{self.command_string}help owner corporate```"},
                {"name": f":convenience_store: About Merchant and Setup :convenience_store:",
                 "value": f"```{self.command_string}help owner merchant```"},
                {"name": f":satellite_orbital: About Uplink and Setup :satellite_orbital:  ",
                 "value": f"```{self.command_string}help owner uplink```"}

            ]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                destination=1, c=Colour.blue())

    # @owner.command(aliases=['corp', 'business'])
    # async def corporate(self, ctx):
    #     corp_info = discord.Embed(title=':bank:  __Merchant System Commands__ :bank:',
    #                               description=' Commands to operate with the guilds own wallet',
    #                               colour=discord.Color.blue())
    #     corp_info.add_field(name=':bar_chart: Obtain Statistics on Guild activity',
    #
    #                         value=f'`{self.command_string}owner stats`',
    #                         inline=False)
    #     corp_info.add_field(name=':service_dog: Get status of activated services :service_dog:  ',
    #                         value=f'`{self.command_string}owner services`',
    #                         inline=False)
    #     corp_info.add_field(name=':moneybag: Merchant wallet balance check :moneybag: ',
    #                         value=f'`{self.command_string}merchant balance`',
    #                         inline=False)
    #
    #     corp_info.set_thumbnail(url=self.bot.user.avatar_url)
    #     await ctx.author.send(embed=corp_info, delete_after=500)

    # @owner.command(aliases=['store', 'monetize', 'merch'])
    # async def merchant(self, ctx):
    #     """
    #     Entry point for merchant system
    #     """
    #     merchant_nfo = discord.Embed(title=':convenience_store: __Merchant System Commands__ :convenience_store: ',
    #                                  description='Basic explanation on what is merchant system.',
    #                                  colour=discord.Color.blue())
    #     merchant_nfo.add_field(name=':mega: About Merchant System:mega:',
    #                            value='Merchant is part of the Crypto Link eco system and provides owners of the '
    #                                  'community opportunity to, automize'
    #                                  ' and fully automate role system. Once monetized roles are created, '
    #                                  'Discord members can use available Crypto Link integrated currencies'
    #                                  ' to purchase roles in various durations and values (determined by community '
    #                                  'owner). System will than handle distribution on appropriate role'
    #                                  ', transfer of funds to corporate account, and as well remove it from the user '
    #                                  'once duration expires.',
    #                            inline=False)
    #     merchant_nfo.add_field(name=':scroll: Fees and licensing :scroll: ',
    #                            value='Activation and integration of merchant system is free of charge, however once '
    #                                  'owner wants to withdraw funds from merchant account'
    #                                  'to his own, a dynamic fee is applied. There is an option as well to obtain '
    #                                  'monthly license, and with it remove the transfer fees.',
    #                            inline=False)
    #     merchant_nfo.add_field(name=':rocket: Get Started with Merchant :rocket: ',
    #                            value=f":one: Register yourself {self.bot.user.name} account with "
    #                                  f"`{self.command_string}register`\n"
    #                                  f":two: Register your guild  into the {self.bot.user.name} system "
    #                                  f"with`{self.command_string}owner register`\n"
    #                                  f":three: Initiate the merchant with `{self.command_string}merchant_initiate`\n"
    #                                  f":four: Familiarize yourself with merchant system through command `{self.command_string}merchant`",
    #                            inline=False)
    #     merchant_nfo.set_thumbnail(url=self.bot.user.avatar_url)
    #     await ctx.author.send(embed=merchant_nfo, delete_after=500)

    @owner.command(aliases=['link', 'up_link'])
    async def uplink(self, ctx):
        """
        Entry point for merchant system
        """
        uplink_nfo = discord.Embed(title=':convenience_store: Uplink System Commands__ :convenience_store: ',
                                   description='Basic explanation on what is merchant system',
                                   colour=discord.Color.blue())
        uplink_nfo.add_field(name=':mega: About Up-Link :mega:',
                             value=' Crypto Link Up-Link is a service, allowing Discord Guild Owner to opt-in one '
                                   'of the text channels available for updates on Crypto Link activity. It serves'
                                   'as a "explorer" of activity. As soon as someone purchases role, or makes '
                                   'p2p transaction, a Discord Wide messages will be sent to channels opted in for'
                                   'service.  ',
                             inline=False)
        uplink_nfo.add_field(name=':rocket: Get Started with Up-Link :rocket: ',
                             value=f':one: `{self.command_string}uplink apply <#discord.TextChannel>`\n'
                                   f':two: Watch the magic happen on next activity\n'
                                   f':three: For further references use `{self.command_string}owner uplink`',
                             inline=False)

        uplink_nfo.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.author.send(embed=uplink_nfo, delete_after=500)

    @help.command(aliases=['hor', 'network', 'explorer'])
    async def horizon(self, ctx):
        """
        Entry point for merchant system
        """
        horizon_info = discord.Embed(title=':sunrise: __ Stellar Horizon Access__ :sunrise:  ',
                                     description='What is Horizon',
                                     colour=Colour.lighter_gray())
        horizon_info.add_field(name=':information_source:  About Horizon :information_source: ',
                               value='Horizon is the client-facing API server for the Stellar ecosystem. It acts as '
                                     'the interface between Stellar Core and applications that want to access the'
                                     ' Stellar network. Horizon allows you to submit transactions to the network, '
                                     'check the status of accounts, and subscribe to event streams. The goal'
                                     ' of the Discord command over Crypto Link is to try to bridge as many API calls as'
                                     ' possible and mimic the functions from '
                                     '[Stellar Laboratory](https://laboratory.stellar.org/#?network=public) and '
                                     'bring them to Discord Users.',
                               inline=False)
        horizon_info.add_field(name=':joystick: How to access Horizon :joystick: ',
                               value=f'`{self.command_string}horizon` is the entry point to navigate '
                                     f'through available options and endpoints which you can access from Discord.',
                               inline=False)
        horizon_info.add_field(name=':joystick: Horizon Synonyms :joystick: ',
                               value=f'Synonyms are "nicknames" for `{self.command_string}horizon`:\n'
                                     f'`{self.command_string}hor`:\n'
                                     f'`{self.command_string}network`:\n'
                                     f'`{self.command_string}explorer`:\n',
                               inline=False)

        await ctx.author.send(embed=horizon_info, delete_after=500)

    @owner.error
    async def owner_error_assistance(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'You can access this are only if you are the owner of the guild and command is executed on ' \
                      f'public channel'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0)


def setup(bot):
    bot.add_cog(HelpCommands(bot))
