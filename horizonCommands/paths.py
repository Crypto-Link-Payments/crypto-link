"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers
from cogs.utils.securityChecks import check_stellar_address
from horizonCommands.horizonAccess.horizon import server
from stellar_sdk import Asset, PathPayment

custom_messages = CustomMessages()
helper = Helpers()
auto_channels = helper.read_json_file(file_name='autoMessagingChannels.json')

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
CONST_ACCOUNT_ERROR = '__Account Not Registered__'


class HorizonPaths(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.command_string = bot.get_command_str()
        self.server = server

    async def send_record(self, ctx, data: dict):
        record_info = Embed(title=':record_button: Record Info :record_button: ',
                            colour=Colour.lighter_gray())
        record_info.add_field(name=f':gem: Source Asset :gem:',
                              value=f'`{data["source_asset_code"]}`',
                              inline=False)
        record_info.add_field(name=f':gem: Destination Asset :gem:',
                              value=f'`{data["destination_asset_code"]}`',
                              inline=False)
        record_info.add_field(name=f':money_with_wings:  Destination Amount :money_with_wings: ',
                              value=f'`{data["destination_amount"]} {data["destination_asset_code"]}`')

        counter = 0

        path_str = str()
        for p in data["path"]:
            if p["asset_type"] == 'native':
                path_str += f'***{counter}.*** `XLM`\n========\n'
            else:
                path_str += f'***{counter}.*** `{p["asset_code"]}`\n ```{p["asset_issuer"]}```========\n'
            counter += 1
        record_info.add_field(name=':railway_track: Paths :railway_track: ',
                              value=path_str,
                              inline=False)
        await ctx.author.send(embed=record_info)

    @commands.group()
    async def paths(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        title = ':railway_track:  __Horizon Trades Queries__ :railway_track:'
        description = 'Representation of all available commands available to interact with ***Paths*** Endpoint on ' \
                      'Stellar Horizon Server'
        list_of_commands = [
            {"name": f':service_dog: Find Strict Send Payment Paths',
             "value": f'`{self.command_string}paths send <to address> <amount> <asset> <issuer>`\n'
                      f'***__Note__***: Issuer can be None if asset is Native'},
            {"name": f':mag_right:  Find Strict Receive Payment Paths :mag:',
             "value": f'`{self.command_string}paths find <from address> <amount> <asset_codes> <asset isser>`\n'
                      f'***__Note__***: Issuer can be None if asset is Native'},
        ]
        if ctx.invoked_subcommand is None:
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @paths.command()
    async def check(self, ctx):

        query = {
            "_embedded": {
                "records": [
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "BB1",
                        "destination_asset_issuer": "GD5J6HLF5666X4AZLTFTXLY46J5SW7EXRKBLEYPJP33S33MXZGV6CWFN",
                        "destination_amount": "87.6373649",
                        "path": [
                            {
                                "asset_type": "native"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "BB1",
                        "destination_asset_issuer": "GD5J6HLF5666X4AZLTFTXLY46J5SW7EXRKBLEYPJP33S33MXZGV6CWFN",
                        "destination_amount": "36.0841597",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "EURT",
                                "asset_issuer": "GAP5LETOV6YIE62YAM56STDANPRDO7ZFDBGSNHJQIYGGKSMOZAHOOS2S"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "BB1",
                        "destination_asset_issuer": "GD5J6HLF5666X4AZLTFTXLY46J5SW7EXRKBLEYPJP33S33MXZGV6CWFN",
                        "destination_amount": "16.2264000",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "BTC",
                                "asset_issuer": "GBVOL67TMUQBGL4TZYNMY3ZQ5WGQYFPFD5VJRWXR72VA33VFNL225PL5"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "BB1",
                        "destination_asset_issuer": "GD5J6HLF5666X4AZLTFTXLY46J5SW7EXRKBLEYPJP33S33MXZGV6CWFN",
                        "destination_amount": "13.9424750",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "USD",
                                "asset_issuer": "GDUKMGUGDZQK6YHYA5Z6AY2G4XDSZPSZ3SW5UN3ARVMO6QSRDWP5YLEX"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "CNY",
                        "destination_asset_issuer": "GAREELUB43IRHWEASCFBLKHURCGMHE5IF6XSE7EXDLACYHGRHM43RFOX",
                        "destination_amount": "499.8384123",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "ULT",
                                "asset_issuer": "GC76RMFNNXBFDSJRBXCABWLHXDK4ITVQSMI56DC2ZJVC3YOLLPCKKULT"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "CNY",
                        "destination_asset_issuer": "GAREELUB43IRHWEASCFBLKHURCGMHE5IF6XSE7EXDLACYHGRHM43RFOX",
                        "destination_amount": "498.1069097",
                        "path": [
                            {
                                "asset_type": "native"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "CNY",
                        "destination_asset_issuer": "GAREELUB43IRHWEASCFBLKHURCGMHE5IF6XSE7EXDLACYHGRHM43RFOX",
                        "destination_amount": "494.5886542",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "XCN",
                                "asset_issuer": "GCNY5OXYSY4FKHOPT2SPOQZAOEIGXB5LBYW3HVU3OWSTQITS65M5RCNY"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "CNY",
                        "destination_asset_issuer": "GAREELUB43IRHWEASCFBLKHURCGMHE5IF6XSE7EXDLACYHGRHM43RFOX",
                        "destination_amount": "490.0780598",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "USD",
                                "asset_issuer": "GDUKMGUGDZQK6YHYA5Z6AY2G4XDSZPSZ3SW5UN3ARVMO6QSRDWP5YLEX"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "CNY",
                        "destination_asset_issuer": "GAREELUB43IRHWEASCFBLKHURCGMHE5IF6XSE7EXDLACYHGRHM43RFOX",
                        "destination_amount": "280.2909824",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "USD",
                                "asset_issuer": "GBUYUAI75XXWDZEKLY66CFYKQPET5JR4EENXZBUZ3YXZ7DS56Z4OKOFU"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "EURT",
                        "destination_asset_issuer": "GAP5LETOV6YIE62YAM56STDANPRDO7ZFDBGSNHJQIYGGKSMOZAHOOS2S",
                        "destination_amount": "63.1883029",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "USD",
                                "asset_issuer": "GDUKMGUGDZQK6YHYA5Z6AY2G4XDSZPSZ3SW5UN3ARVMO6QSRDWP5YLEX"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "EURT",
                        "destination_asset_issuer": "GAP5LETOV6YIE62YAM56STDANPRDO7ZFDBGSNHJQIYGGKSMOZAHOOS2S",
                        "destination_amount": "63.1472796",
                        "path": [
                            {
                                "asset_type": "native"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "EURT",
                        "destination_asset_issuer": "GAP5LETOV6YIE62YAM56STDANPRDO7ZFDBGSNHJQIYGGKSMOZAHOOS2S",
                        "destination_amount": "62.9386895",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "NGNT",
                                "asset_issuer": "GAWODAROMJ33V5YDFY3NPYTHVYQG7MJXVJ2ND3AOGIHYRWINES6ACCPD"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "EURT",
                        "destination_asset_issuer": "GAP5LETOV6YIE62YAM56STDANPRDO7ZFDBGSNHJQIYGGKSMOZAHOOS2S",
                        "destination_amount": "6.7649849",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "WSD",
                                "asset_issuer": "GDSVWEA7XV6M5XNLODVTPCGMAJTNBLZBXOFNQD3BNPNYALEYBNT6CE2V"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "EURT",
                        "destination_asset_issuer": "GAP5LETOV6YIE62YAM56STDANPRDO7ZFDBGSNHJQIYGGKSMOZAHOOS2S",
                        "destination_amount": "0.0498106",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "CNY",
                                "asset_issuer": "GAREELUB43IRHWEASCFBLKHURCGMHE5IF6XSE7EXDLACYHGRHM43RFOX"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "NGNT",
                        "destination_asset_issuer": "GAWODAROMJ33V5YDFY3NPYTHVYQG7MJXVJ2ND3AOGIHYRWINES6ACCPD",
                        "destination_amount": "25155.3452034",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "USD",
                                "asset_issuer": "GDUKMGUGDZQK6YHYA5Z6AY2G4XDSZPSZ3SW5UN3ARVMO6QSRDWP5YLEX"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "NGNT",
                        "destination_asset_issuer": "GAWODAROMJ33V5YDFY3NPYTHVYQG7MJXVJ2ND3AOGIHYRWINES6ACCPD",
                        "destination_amount": "25146.7108397",
                        "path": [
                            {
                                "asset_type": "native"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "NGNT",
                        "destination_asset_issuer": "GAWODAROMJ33V5YDFY3NPYTHVYQG7MJXVJ2ND3AOGIHYRWINES6ACCPD",
                        "destination_amount": "24986.8616583",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "BTC",
                                "asset_issuer": "GAUTUYY2THLF7SGITDFMXJVYH3LHDSMGEAKSBU267M2K7A3W543CKUEF"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "NGNT",
                        "destination_asset_issuer": "GAWODAROMJ33V5YDFY3NPYTHVYQG7MJXVJ2ND3AOGIHYRWINES6ACCPD",
                        "destination_amount": "24948.9784843",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "XCN",
                                "asset_issuer": "GCNY5OXYSY4FKHOPT2SPOQZAOEIGXB5LBYW3HVU3OWSTQITS65M5RCNY"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "NGNT",
                        "destination_asset_issuer": "GAWODAROMJ33V5YDFY3NPYTHVYQG7MJXVJ2ND3AOGIHYRWINES6ACCPD",
                        "destination_amount": "24930.7854717",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "EURT",
                                "asset_issuer": "GAP5LETOV6YIE62YAM56STDANPRDO7ZFDBGSNHJQIYGGKSMOZAHOOS2S"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "USD",
                        "destination_asset_issuer": "GDUKMGUGDZQK6YHYA5Z6AY2G4XDSZPSZ3SW5UN3ARVMO6QSRDWP5YLEX",
                        "destination_amount": "69.7123752",
                        "path": [
                            {
                                "asset_type": "native"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "USD",
                        "destination_asset_issuer": "GDUKMGUGDZQK6YHYA5Z6AY2G4XDSZPSZ3SW5UN3ARVMO6QSRDWP5YLEX",
                        "destination_amount": "68.9785993",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "EURT",
                                "asset_issuer": "GAP5LETOV6YIE62YAM56STDANPRDO7ZFDBGSNHJQIYGGKSMOZAHOOS2S"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "USD",
                        "destination_asset_issuer": "GDUKMGUGDZQK6YHYA5Z6AY2G4XDSZPSZ3SW5UN3ARVMO6QSRDWP5YLEX",
                        "destination_amount": "68.6731854",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "NGNT",
                                "asset_issuer": "GAWODAROMJ33V5YDFY3NPYTHVYQG7MJXVJ2ND3AOGIHYRWINES6ACCPD"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "USD",
                        "destination_asset_issuer": "GDUKMGUGDZQK6YHYA5Z6AY2G4XDSZPSZ3SW5UN3ARVMO6QSRDWP5YLEX",
                        "destination_amount": "63.5394120",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "USD",
                                "asset_issuer": "GBUYUAI75XXWDZEKLY66CFYKQPET5JR4EENXZBUZ3YXZ7DS56Z4OKOFU"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "credit_alphanum4",
                        "destination_asset_code": "USD",
                        "destination_asset_issuer": "GDUKMGUGDZQK6YHYA5Z6AY2G4XDSZPSZ3SW5UN3ARVMO6QSRDWP5YLEX",
                        "destination_amount": "39.6691360",
                        "path": [
                            {
                                "asset_type": "native"
                            },
                            {
                                "asset_type": "credit_alphanum4",
                                "asset_code": "HEX",
                                "asset_issuer": "GCGBSZ3DSSH6PRHCOD4JXFNNZXCTKBDFRT4JR2HIAC6FQZU4YK7GPHEX"
                            }
                        ]
                    },
                    {
                        "source_asset_type": "credit_alphanum4",
                        "source_asset_code": "BRL",
                        "source_asset_issuer": "GDVKY2GU2DRXWTBEYJJWSFXIGBZV6AZNBVVSUHEPZI54LIS6BA7DVVSP",
                        "source_amount": "400.0000000",
                        "destination_asset_type": "native",
                        "destination_amount": "1226.9231099",
                        "path": []
                    }
                ]
            }
        }

        query_info = Embed(title=f':mag_right: Strict Send Payment Search :mag:',
                           description='Bellow is information for 3 results returned from network',
                           colour=Colour.lighter_gray())
        query_info.add_field(name=f':map: To Address :map:',
                             value=f'```GAYOLLLUIZE4DZMBB2ZBKGBUBZLIOYU6XFLW37GBP2VZD3ABNXCW4BVA```',
                             inline=False)
        query_info.add_field(name=f':gem: Destination Asset :gem: ',
                             value=f'`BB1`',
                             inline=False)
        await ctx.author.send(embed=query_info)

        last_three_records = query["_embedded"]["records"][:3]
        for r in last_three_records:
            await self.send_record(ctx, data=r)

    @paths.command()
    async def send(self, ctx, to_address: str, source_amount: float, source_asset: str, issuer: str = None):
        atomic_value = (int(source_amount * (10 ** 7)))
        normal = (atomic_value / (10 ** 7))

        # Validate stellar address structure
        if check_stellar_address(address=to_address) and check_stellar_address(issuer):
            if source_asset.upper() != 'XLM':
                source_asset = Asset(code=source_asset.upper(), issuer=issuer)
            else:
                source_asset = Asset(code='XLM').native()

            data = self.server.strict_send_paths(source_asset=source_asset, source_amount=normal,
                                                 destination=to_address).call()
            last_three_records = data["_embedded"]["records"][:3]

            query_info = Embed(title=f':mag_right: Strict Send Payment Search :mag:',
                               description='Bellow is information for 3 results returned from network',
                               colour=Colour.lighter_gray())
            query_info.add_field(name=f':map: To Address :map:',
                                 value=f'```{to_address}```',
                                 inline=False)
            query_info.add_field(name=f':moneybag: Source Asset :moneybag: ',
                                 value=f'`{normal} {source_asset}`',
                                 inline=False)

            if issuer:
                query_info.add_field(name=f':bank: Issuer :bank:',
                                     value=f'```{issuer}```',
                                     inline=False)
            await ctx.author.send(embed=query_info)

            for r in last_three_records:
                await self.send_record(ctx, data=r)

    @paths.command()
    async def receive(self, ctx, from_address: str, received_amount: float, asset_code: str, asset_issuer: str = None):

        atomic_value = (int(received_amount * (10 ** 7)))
        normal = (atomic_value / (10 ** 7))

        # Validate stellar address structure
        if check_stellar_address(address=from_address) and check_stellar_address(asset_issuer):
            if asset_code.upper() != 'XLM':
                destination_asset = Asset(code=asset_code.upper(), issuer=asset_issuer)
            else:
                destination_asset = Asset(code='XLM').native()

            data = self.server.strict_receive_paths(destination_asset=destination_asset,
                                                    destination_amount=normal).call()
            last_three_records = data["_embedded"]["records"][:3]

            query_info = Embed(title=f':mag_right: Strict Send Payment Search :mag:',
                               description='Bellow is information for 3 results returned from network',
                               colour=Colour.lighter_gray())
            query_info.add_field(name=f':map: From Address :map:',
                                 value=f'```{from_address}```',
                                 inline=False)
            query_info.add_field(name=f':moneybag: Source Asset :moneybag: ',
                                 value=f'`{normal} {asset_code}`',
                                 inline=False)

            if asset_issuer:
                query_info.add_field(name=f':bank: Issuer :bank:',
                                     value=f'```{asset_issuer}```',
                                     inline=False)
            await ctx.author.send(embed=query_info)

            for r in last_three_records:
                await self.send_record(ctx, data=r)


def setup(bot):
    bot.add_cog(HorizonPaths(bot))
