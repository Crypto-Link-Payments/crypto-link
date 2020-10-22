"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from backOffice.stellarOnChainHandler import StellarWallet
from cogs.utils.systemMessaages import CustomMessages
from discord.ext.commands.errors import CommandInvokeError
from utils.tools import Helpers

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'
stellar_chain = StellarWallet()


class HorizonAssets(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()

    @staticmethod
    async def send_asset_details(ctx, data, request: str):
        """

        'asset_type': 'credit_alphanum4',
        """
        from pprint import pprint
        pprint(data)
        toml_access = data['_embedded']['records'][0]['_links']['toml']['href']
        record = data['_embedded']['records'][0]

        asset_info = Embed(title=f':bank: Issuer Details :bank:',
                           description=f'Bellow is represent information for requested {request}.',
                           colour=Colour.lighter_gray())
        asset_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                             value=f'[Horizon]({data["_links"]["self"]["href"]})')

        if not toml_access:
            toml_data = None
            toml_link = ''
        else:
            toml_data = "Access link"
            toml_link = toml_access

        asset_info = Embed(title=" :bank: __Issuer Details__ :bank:",
                           description=f'TOML access: [{toml_data}]({toml_link})',
                           colour=Colour.lighter_gray())
        asset_info.add_field(name=f':regional_indicator_c: Asset Code :regional_indicator_c:',
                             value=f'{record["asset_code"]}',
                             inline=False)
        asset_info.add_field(name=f':gem: Asset Type :gem:',
                             value=f'{record["asset_type"]}',
                             inline=False)
        asset_info.add_field(name=f':map: Issuing Account :map: ',
                             value=f'```{record["asset_issuer"]}```',
                             inline=False)
        asset_info.add_field(name=f':moneybag: Issued Amount :moneybag: ',
                             value=f'`{record["amount"]} {record["asset_code"]}`',
                             inline=False)
        asset_info.add_field(name=f':cowboy: Account Count :cowboy: ',
                             value=f'`{record["num_accounts"]}`',
                             inline=False)
        asset_info.add_field(name=f':triangular_flag_on_post: Account Flags :triangular_flag_on_post: ',
                             value=f'Immutable: {record["flags"]["auth_immutable"]} \n'
                                   f'Required:  {record["flags"]["auth_required"]}\n'
                                   f'Revocable:  {record["flags"]["auth_revocable"]}\n',
                             inline=False)
        asset_info.add_field(name=f':white_circle: Paging Token :white_circle:',
                             value=f'```{record["paging_token"]}```',
                             inline=False)
        await ctx.author.send(embed=asset_info)

    async def send_multi_asset_case(self, ctx, data):
        records = data['_embedded']['records']

        asset_info = Embed(title=f':gem: Multiple Assets Found :gem: ',
                           description=f'Please use `{self.command_string}assets issuer <issuer address >` to'
                                       f' obtain full details',
                           colour=Colour.lighter_gray())
        asset_info.add_field(name=f':sunrise: Horizon Link :sunrise:',
                             value=f'[Horizon]({data["_links"]["self"]["href"]})',
                             inline=False)
        asset_info.add_field(name=f' Total Found ',
                             value=f'{len(records)} assets with code {records[0]["asset_code"]}',
                             inline=False)
        asset_count = 1
        for asset in records:

            if not asset['_links']['toml']['href']:
                toml_data = None
                toml_link = ''
            else:
                toml_data = "Access link"
                toml_link = asset['_links']['toml']['href']

            asset_info.add_field(name=f'{asset_count}. Asset',
                                 value=f':map: Issuer :map: \n'
                                       f'```{asset["asset_issuer"]}```\n'
                                       f':moneybag: Amount Issued :moneybag: \n'
                                       f'`{asset["amount"]} {asset["asset_code"]}`\n'
                                       f':globe_with_meridians: toml access :globe_with_meridians: \n'
                                       f'[{toml_data}]({toml_link})',
                                 inline=False)
            asset_count += 1

        await ctx.author.send(embed=asset_info)

    @commands.group()
    async def assets(self, ctx):
        title = ':gem: __Horizon Assets Queries__ :gem:'
        description = 'Representation of all available commands available to interact with ***Assets*** Endpoint on ' \
                      'Stellar Horizon Server'
        list_of_commands = [
            {"name": f':regional_indicator_c: Query by code :regional_indicator_c: ',
             "value": f'`{self.command_string}assets code <alphanumeric string>`'},
            {"name": f':map: Query by Issuer Address :map:',
             "value": f'`{self.command_string}assets issuer <Issuer address>`'}
        ]

        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @assets.command()
    async def code(self, ctx, code: str):
        data = stellar_chain.get_asset_by_code(asset_code=code.upper())

        if data:
            records = data['_embedded']['records']
            # If only one asset code found
            if len(records) == 1:
                await self.send_asset_details(ctx=ctx, data=records[0], request='asset code')

            else:
                await self.send_multi_asset_case(ctx=ctx, data=data)
        else:
            message = f'No Asset with code {code} found. Please try again'
            print(message)

    @assets.command()
    async def issuer(self, ctx, issuer_addr: str):
        data = stellar_chain.get_asset_by_issuer(issuer=issuer_addr)
        if data:
            await self.send_asset_details(ctx=ctx, data=data, request='issuer')
        else:
            message = f' Issuer with address `{issuer_addr} does not exist. Please recheck address and try again'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title='Issuer Does Not Exist')

    @code.error
    async def code_error(self, ctx, error):
        if isinstance(error, CommandInvokeError):
            print('Code is allowed to constructed only from alphanumeric characters')


def setup(bot):
    bot.add_cog(HorizonAssets(bot))
