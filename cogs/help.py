"""
COGS: Help commands for the payment services
"""
import nextcord
from nextcord.ext import commands
from nextcord import Colour, Embed
from utils.tools import Helpers
from utils.customCogChecks import is_owner, is_public
from cogs.utils.systemMessaages import CustomMessages
import re
from datetime import datetime

import nextcord
from nextcord import Role, Embed, Color, utils
from nextcord.ext import commands
from utils.customCogChecks import is_public, merchant_com_reg_stats_check
from cogs.utils.monetaryConversions import convert_to_currency
from cogs.utils.monetaryConversions import get_normal
from cogs.utils.systemMessaages import CustomMessages
from nextcord import Embed, Colour, slash_command, SlashOption, Interaction, Role, TextChannel, ChannelType
from utils.customCogChecks import has_wallet_inter_check, is_guild_owner_or_has_clmng, has_clmng_role, is_public_channel
from nextcord.ext import commands
import cooldowns


custom_messages = CustomMessages()

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'


class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.helper = Helpers()
        self.command_string = bot.get_command_str()

    @slash_command(name='help', description='Get assistance with navigating the Crypot Link system')
    async def help_cmd(self, interaction: Interaction):
        await interaction.response.send_message(
            content="Use `/merchant help` to view available merchant commands.",
            ephemeral=True
        )

    @help_cmd.subcommand(name="about", description='About Crypto Link')
    async def help_about(self, interaction: Interaction):
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
             "value": f'At this moment Crypto Link supports only custodial wallet which operated based on MEMO '
                      f'when depositing. '
                      f'please use `/wallet help`. Each user is required to register for custodial '
                      f'wallet in order to be able to interact and use Crypto Link in full.'},

            {"name": ":money_with_wings: Instant Peer to Peer feels transactions :money_with_wings:  ",
             "value": f"Users are able to execute instant peer-2-peer transactions without fees either with the Stellar"
                      f" native currency XLM or integrated tokens. Currently system supports public and private types."
                      f" For full list of supported currencies please use command /currencies"},

            {"name": ":convenience_store: Merchant system :convenience_store: ",
             "value": f"Discord Guild owners can monetize roles in various lengths and "
                      f"values and make them available for purchase. Once role is purchased, Crypto Link will handle"
                      f" micro management tasks (role management, transfer of funds, role monitoring and its removal "
                      f"uppon expiration) on its own, saving owners a lot of time."},
            {"name": ":postal_horn: ICO's and Project promotions :postal_horn: ",
             "value": f'Integrated support for Stellar Native Crypto Currency and its tokens provides as well '
                      f'possibility for Crypto Link to be utilized as one of the channels for running '
                      f'ICOs/Crowdfundings or simple project promotion activities. If you would like to know more '
                      f'or would like to get in touch with us, please write us on'
                      f' ***__cryptolinkpayments@gmail.com__***, open issue on Github or contact us directly over '
                      f'Discord Crypto Link Community.'},
            {"name": ":placard: Further information and links:placard: ",
             "value": f'[Homepage](https://cryptolink.carrd.co/) \n'
                      f'[Github](https://github.com/launch-pad-investments/crypto-link) \n'
                      f'[Twitter](https://twitter.com/CryptoLink8)'},
        ]

        await custom_messages.embed_builder(interaction=interaction, title=title, description=description, data=list_of_values,
                                            destination=1, c=Colour.blue())


    @help_cmd.subcommand(name="get_started", description='About Crypto Link')
    async def help_get_started(self, interaction:Interaction):
        """
        How to get started with the payment system
        :param ctx: Discord Context
        :return: Discord Embed
        """
        start_embed = Embed(title=f':rocket: Launch {self.bot.user.name} Experience :rocket:',
                            colour=Colour.blue())
        start_embed.add_field(name=':one: Register yourself custodial wallet :one:',
                              value=f'In order for you to be able to make peer to peer transactions and use merchant'
                                    f' system, you must have registered at least custodial wallet.\n'
                                    f'You can do that by executing command `/register` on any '
                                    f'public Discord channel where Crypto Link has access to.\n'
                                    f'Once successful, you will create personal wallet with details which you can use '
                                    f' to move or deposit funds. To further familiarize yourself with other'
                                    f' commands use `/help <category>`',
                              inline=False)
        start_embed.add_field(name=':two: Get Deposit Details :two:',
                              value=f'Get deposit details of your Discord wallet with `/wallet deposit'
                                    f' and deposit XLM or any other supported Stellar native token. ',
                              inline=False)
        start_embed.add_field(name=':three: Make P-2-P Transaction :three:',
                              value=f'`{self.command_string}send <@discord.Member> <amount> <ticker>`\n'
                                    f'Example: `{self.command_string}send @animus 10 xlm`',
                              inline=False)
        start_embed.add_field(name=':four: Check your balances :four:',
                              value=f'`/wallet balance` or\n'
                                    f'`/me`',
                              inline=False)
        start_embed.add_field(name=':five: Withdraw from Discord :five:',
                              value=f'`/wallet withdraw <address> <amount> <asset_code>  <memo=optional>`\n'
                                    f'Example: `/wallet withdraw GBALRXCJ6NNRE4USDCUFLAOZCDSKDSEJZHTLGEDQXI7BM2T6M77CMMWG 10 xlm`',
                              inline=False)
        await interaction.send(embed=start_embed)

    
    @help_cmd.subcommand(name='currencies', description='Check supported currencies on Crypto Link')
    async def currencies(self, interaction: Interaction):
        """
        Returns representation of all available currencies available to be utilized int transactions
        :return: Discord Embed
        """
        available = Embed(title=':coin: Integrated coins and tokens :coin: ',
                          description='[Token List](https://cryptolink.carrd.co/)',
                          colour=Colour.blue())
        await interaction.send(embed=available)

    @help.command(aliases=['w'])
    async def wallets(self, ctx):
        title = ':office_worker: __Multi Level Wallet system__:office_worker: '
        description = "Explanation of wallet system"
        list_of_values = [
            {"name": ":one: Custodial Wallet :one: ",
             "value": f"Registration for `custodial wallet level` is mandatory for all users who would like to "
                      f"use all the functions Crypto Link has to offer. Wallet operates based on MEMO when depositing. "
                      f"This allows anyone to receive transaction from sender "
                      f"instantly, even if recipient has not registered yet into the system. Custodial wallet "
                      f"is automatically created and all actions connected with it do not require private key "
                      f"to be used for signing. In order to fully protect your wallet, please activate 2FA for Discord "
                      f"account. "}
        ]

        await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                            destination=1, c=Colour.blue())

    @help.command(aliases=['tx', 'pay'])
    async def payments(self, ctx):
        title = ':money_with_wings: __How to make P-2-P payments__ :money_with_wings: '
        description = f"Available payment types on {self.bot.user.name} System"
        list_of_values = [
            {"name": f":cowboy: Public P-2-P payment :cowboy:",
             "value": f"`{self.command_string}send <@Discord User> <amount> <asset_code> <message=optional>`\n"
                      f"__Example__:`{self.command_string}send @animus 10 xlm Have a nice day`"},
            {"name": f":detective: Private payment :detective:  ",
             "value": f"`{self.command_string}private <@Discord User> <amount> <asset_code> <message=optional>`\n"
                      f"__Example__: `{self.command_string}private  @animus 10 xlm Dont tell anyone`"},
            {"name": f":gift: Gift to other members :gift:  ",
             "value": f"`{self.command_string}give <Up to 5 taged users> <amount> <asset_code> <message=optional>`\n"
                      f"__Example__: `{self.command_string}give @Animus @Plippy @ManuManu 1 xlm`"},
            {"name": f":military_medal: Loyalty :military_medal:",
             "value": f"`{self.command_string}loyalty <Last N active users on channe> <amount> <asset_code>`\n"
                      f"__Example__: `{self.command_string}loyalty 2 1 xlm`\n"
                      f"__Description__: Sends 1 xlm to two users who have last posted to the channel where payment "
                      f"was executed  in history of 100 messages. "},
            {"name": f":mortar_board: Role Payment :mortar_board:",
             "value": f"`{self.command_string}to_role <@discord.Role> <amount> <asset_code>`\n"
                      f"__Example__: `{self.command_string}to_role @vip 1 xlm`\n"
                      f"__Description__: Send 1 xlm to each members who has been assigned role ***vip***"}
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
    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def owner(self, ctx):
        if ctx.invoked_subcommand is None:
            title = ':crown: __Available Commands for guild owners__ :crown: '
            description = f"This section of command is dedicated only for the owners of the server. "

            list_of_values = [
                {"name": f":crown: Owner panel access :crown:",
                 "value": f"```{self.command_string}owner```"},
                {"name": f":scales:  Register Guild into System :scales: ",
                 "value": f"```{self.command_string}owner register```"},
                # {"name": f":bank: Guild wallet commands :bank:",
                #  "value": f"```{self.command_string}help owner corporate```"},
                # {"name": f":convenience_store: About Merchant and Setup :convenience_store:",
                #  "value": f"```{self.command_string}help owner merchant```"},
                {"name": f":satellite_orbital: About Uplink system and Setup :satellite_orbital:  ",
                 "value": f"```{self.command_string}help owner uplink```"},
                {"name": f":convenience_store:  About merchant system over Discord :convenience_store: ",
                 "value": f"```{self.command_string}help owner merchant```"}
            ]

            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                c=Colour.blue())

    @owner.command(aliases=['store', 'monetize', 'merch'])
    async def merchant(self, ctx):
        """
        Entry point for merchant system
        """
        merchant_nfo = Embed(title=':convenience_store: __Merchant System Commands__ :convenience_store: ',
                             description='Basic explanation on what is merchant system.',
                             colour=Colour.blue())
        merchant_nfo.add_field(name=':mega: About Merchant System:mega:',
                               value='Merchant is part of the Crypto Link eco system and provides owners of the '
                                     'community an opportunity to monetize perks/roles. Once role, of custom duration'
                                     ' and value successfully registered and activated, it can be offered to '
                                     'Discord members for purchase. System handles role management automatically,'
                                     'transfer of funds to server owners account, and role removal upon expiration'
                                     ' date (subjected to role length and date of purchase)',
                               inline=False)
        merchant_nfo.add_field(name=':scroll: Fees',
                               value='Activation and integration of merchant system is free of charge, however once '
                                     'owner wants to withdraw funds from merchant account'
                                     'to his own, a dynamic fee is applied.',
                               inline=False)
        merchant_nfo.add_field(name=':rocket: Get Started with Merchant :rocket: ',
                               value=f":one: Register yourself {self.bot.user.name} account with "
                                     f"`{self.command_string}register`\n"
                                     f":two: Register your guild into the {self.bot.user.name} system "
                                     f"with`{self.command_string}owner register`\n"
                                     f":three: Initiate the merchant with `{self.command_string}merchant_initiate`\n"
                                     f":four: Familiarize yourself with merchant system through command `{self.command_string}merchant`",
                               inline=False)
        merchant_nfo.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.author.send(embed=merchant_nfo, delete_after=500)

    @owner.command(aliases=['link', 'up_link'])
    async def uplink(self, ctx):
        """
        Entry point for merchant system
        """
        uplink_nfo = nextcord.Embed(title=':convenience_store: Uplink System Commands__ :convenience_store: ',
                                    description='Basic explanation on what is merchant system',
                                    colour=nextcord.Color.blue())
        uplink_nfo.add_field(name=':mega: About Up-Link :mega:',
                             value=' Crypto Link Up-Link is a service, allowing Discord Guild Owner to opt-in one '
                                   'of the text channels available for updates on Crypto Link activity. It serves'
                                   'as a "explorer" of activity. As soon as someone purchases role, or makes '
                                   'p2p transaction, a Discord Wide messages will be sent to channels opted in for'
                                   'service.  ',
                             inline=False)
        uplink_nfo.add_field(name=':rocket: Get Started with Up-Link :rocket: ',
                             value=f':one: `{self.command_string}owner uplink apply <#discord.TextChannel>`\n'
                                   f':two: Watch the magic happen on next activity\n'
                                   f':three: For further references use `{self.command_string}owner uplink`',
                             inline=False)

        uplink_nfo.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.author.send(embed=uplink_nfo, delete_after=500)

    @help.command(aliases=['hor', 'network', 'explorer'])
    async def horizon(self, ctx):
        """
        Entry point for merchant system
        """
        horizon_info = nextcord.Embed(title=':sunrise: __ Stellar Horizon Access__ :sunrise:  ',
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
