"""
COGS which handle explanation  on commands available to communicate with the Paths Horizon Endpoints from Discord
"""

from discord.ext import commands
from discord import Colour
from cogs.utils.systemMessaages import CustomMessages
from stellar_sdk.exceptions import BadRequestError
from horizonCommands.utils.customMessages import send_paths_records_details, send_paths_entry_details, horizon_error_msg
from horizonCommands.utils.tools import get_asset

custom_messages = CustomMessages()


class HorizonPaths(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_string = bot.get_command_str()
        self.server = self.bot.backoffice.stellar_wallet.server
        self.help_functions = bot.backoffice.helper

    @commands.group()
    async def paths(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        if ctx.invoked_subcommand is None:
            title = ':railway_track:  __Horizon Paths Queries__ :railway_track:'
            description = 'Representation of all available commands available to interact with ***Paths*** Endpoint on ' \
                          'Stellar Horizon Server.Commands can be used 1/30 seconds/ per user.'
            list_of_commands = [
                {"name": f':service_dog: Find Strict Send Payment Paths',
                 "value": f'```{self.command_string}paths send <to address> <amount> <asset code> <asset issuer>```\n'
                          f'***__Note__***: Issuer can be None if asset is Native'},
                {"name": f':mag_right: Find Strict Receive Payment Paths :mag:',
                 "value": f'```{self.command_string}paths find <from address> <amount> <asset code> <asset issuer>```\n'
                          f'***__Note__***: Issuer can be None if asset is Native'},
            ]
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @paths.command()
    async def send(self, ctx, to_address: str, source_amount: float, asset_code: str, asset_issuer: str):
        atomic_value = (int(source_amount * (10 ** 7)))
        normal = (atomic_value / (10 ** 7))

        # Validate stellar address structure
        if self.help_functions.check_public_key(address=to_address) and self.help_functions.check_public_key(
                asset_issuer):
            asset_obj = get_asset(asset_code=asset_code.upper(), asset_issuer=asset_issuer)
            try:
                data = self.server.strict_send_paths(source_asset=asset_obj, source_amount=normal,
                                                     destination=to_address).call()
                records = data["_embedded"]["records"]

                if records:
                    await send_paths_entry_details(destination=ctx.message.author,
                                                   details={"direction": "To",
                                                            "type": "Send",
                                                            "address": to_address,
                                                            "amount": normal,
                                                            "asset": asset_code,
                                                            "issuer": asset_issuer})

                    for r in records[:3]:
                        await send_paths_records_details(destination=ctx.message.author, data=r)
                else:
                    message = f'No records for provided details found:\n' \
                              f'To address: `{to_address}`\n' \
                              f'Amount: `{source_amount}`\n' \
                              f'Source Asset: `{asset_code}`\n' \
                              f'"Issuer: `{asset_issuer}`'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                         sys_msg_title=":ledger: No Records for Path found :ledger:")
            except BadRequestError as e:
                await horizon_error_msg(destination=ctx.message.author, error=e.extras["reason"])

        else:
            message = f'One of the addresses provided does not match the Stellar Public Address structure.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title="Address error")

    @paths.command()
    async def receive(self, ctx, from_address: str, received_amount: float, asset_code: str, asset_issuer: str):

        atomic_value = (int(received_amount * (10 ** 7)))
        normal = (atomic_value / (10 ** 7))

        # Validate stellar address structure
        if self.help_functions.check_public_key(address=from_address) and self.help_functions.check_public_key(
                asset_issuer):
            asset_boj = get_asset(asset_code=asset_code, asset_issuer=asset_issuer)

            try:
                data = self.server.strict_receive_paths(destination_asset=asset_boj,
                                                        destination_amount=normal).call()
                records = data["_embedded"]["records"][:3]

                if records:

                    await send_paths_entry_details(destination=ctx.message.author,
                                                   details={"direction": "From",
                                                            "type": "receive",
                                                            "address": from_address,
                                                            "amount": normal,
                                                            "asset": asset_code,
                                                            "issuer": asset_issuer})

                    for r in records:
                        await send_paths_records_details(destination=ctx.message.author, data=r)

            except BadRequestError as e:
                await horizon_error_msg(destination=ctx.message.author, error=e.extras["reason"])
        else:
            message = f'One of the addresses provided does not match the Stellar Public Address structure.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title="Address error")


def setup(bot):
    bot.add_cog(HorizonPaths(bot))
