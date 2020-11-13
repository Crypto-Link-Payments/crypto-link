"""
COGS which handle explanation  on commands available to communicate with the Offers Horizon Endpoints from Discord
"""


from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from horizonCommands.utils.customMessages import offer_details, horizon_error_msg, send_offers
from stellar_sdk.exceptions import BadRequestError

custom_messages = CustomMessages()


class HorizonOffers(commands.Cog):
    """
    Discord Commands to access Offers
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.hor_offers = self.bot.backoffice.stellar_wallet.server.offers()

    @commands.group()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def offers(self, ctx):
        """
        Effects entry point to horizon endpoints
        """
        if ctx.invoked_subcommand is None:
            title = ':handshake: __Horizon Offers Queries__ :handshake:  '
            description = 'Representation of all available commands available to interact with ***Effects***' \
                          ' Endpoint on Stellar Horizon Server.  Commands can be used 1/30 seconds/ per user.'
            list_of_commands = [
                {"name": f':id: Single Offer Query :id:',
                 "value": f'```{self.command_string}offers single <offer id>```\n'
                          f'`Aliases: id`'},
                {"name": f' :map: Offers by Account :map: ',
                 "value": f'```{self.command_string}offers account <Account public address>```\n'
                          f'`Aliases: addr`'}
            ]
            await custom_messages.embed_builder(ctx=ctx, title=title, data=list_of_commands,
                                                description=description,
                                                destination=1, c=Colour.lighter_gray())

    @offers.command(aliases=['id'])
    async def single(self, ctx, offer_id: int):
        try:
            data = self.hor_offers.offer(offer_id=offer_id).call()
            await offer_details(destination=ctx.message.author, offer=data)
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @offers.command(aliases=["addr"])
    async def address(self, ctx, address: str):
        try:
            data = self.hor_offers.account(account_id=address).limit(100).order(desc=True).call()

            if data["_embedded"]["records"]:
                await send_offers(destination=ctx.message.author, address=address,
                                  offers_link=data["_links"]["self"]["href"])

                counter = 0
                for offer in data['_embedded']["records"]:
                    if counter <= 2:
                        await offer_details(destination=ctx.message.author, offer=offer)
                        counter += 1
            else:
                message = f'Account with address `{address}` has no active offers at this moment'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title=':handshake: No Active Offers :handshake:')
        except BadRequestError as e:
            extras = e.extras
            await horizon_error_msg(destination=ctx.message.author, error=extras["reason"])

    @single.error
    async def single_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            message = f'Offer Id parameter is required to be integer number. Please try again'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title=':id:  Wrong Offer ID :id: ')


def setup(bot):
    bot.add_cog(HorizonOffers(bot))
