"""
Cogs to handle commands for licensing with the bot

Owners of the community can pay a one time monthly fee which allows them to make unlimited transfers
from Merchant wallet to their won upon withdrawal.
"""

from discord.ext import commands
from discord import Embed, Colour
from cogs.utils.systemMessaages import CustomMessages
from horizonCommands.horizonAccess.horizon import server
from cogs.utils.securityChecks import check_stellar_address
from utils.tools import Helpers
from stellar_sdk import TransactionBuilder, Network, Server, Account
from stellar_sdk.exceptions import NotFoundError

helper = Helpers()
integrated_coins = helper.read_json_file(file_name='integratedCoins.json')
custom_messages = CustomMessages()
helper = Helpers()


class Layer3AccountCommands(commands.Cog):
    """
    Discord Commands dealing with Merchant Licensing
    """

    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()
        self.server = Server(horizon_url="https://horizon-testnet.stellar.org")
        self.supported = list(integrated_coins.keys())

    @commands.group(aliases=['hot_wallet'])
    async def personal(self, ctx):
        """
        Entry for
        """
        if ctx.invoked_subcommand is None:
            pass

    @personal.command()
    async def payment(self, ctx, amount: float, token: str, from_address: str, to_address: str, memo: str = None):
        try:
            from_account = self.server.load_account(account_id=from_address)
        except NotFoundError:
            pass

        if token != 'xlm':
            if token not in self.supported:
                pass
            else:
                print('Token supported by system get the issuer')
                asset_issuer = integrated_coins[token.lower()]["assetIssuer"]

        else:
            asset_issuer = None

        tx = TransactionBuilder(
            source_account=from_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=self.server.fetch_base_fee()).append_payment_op(
            asset_issuer=asset_issuer,
            destination=to_address, asset_code=token.upper(), amount=str(amount))
        if memo:
            tx.add_text_memo(memo_text=memo)

        xdr_envelope = tx.set_timeout(360).build().to_xdr()

        # Inform user
        xdr_info = Embed(title=f'Payment as XDR',
                         description='Bellow is the XDR envelope of payment with provided details',
                         colour=Colour.magenta())
        xdr_info.add_field(name="From Address",
                           value=f'```{from_address}```',
                           inline=False)
        xdr_info.add_field(name="To Address",
                           value=f'```{to_address}```',
                           inline=False)
        xdr_info.add_field(name="Token and Amount",
                           value=f'{amount} {token}',
                           inline=False)
        if token != 'xlm':
            xdr_info.add_field(name="Asset Issuer",
                               value=f'```{asset_issuer}```',
                               inline=False)

        xdr_info.add_field(name="XDR Envelope",
                           value=f'```{xdr_envelope}```',
                           inline=False)

        xdr_info.add_field(name=":warning: Note :warning:",
                           value=f'Copy the XDR envelope to application which allows __importing of '
                                 f' a transaction envelope in XDR format and follow procedures there.'
                                 f'If you do not have access to such application than you can use as well\n'
                                 f'[Stellar Laboratory Transaction Signer](https://laboratory.stellar.org/#txsigner?network=test)',
                           inline=False)

        await ctx.author.send(embed=xdr_info)


def setup(bot):
    bot.add_cog(Layer3AccountCommands(bot))
