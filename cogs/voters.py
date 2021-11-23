import time
from datetime import datetime
import json
import decimal
from bson.decimal128 import Decimal128
from re import sub
from datetime import timedelta
from discord.ext import commands
from discord import TextChannel, Embed, Colour, Role
from utils.customCogChecks import is_owner, is_public, guild_has_stats, has_wallet, has_ballot_access
from cogs.utils.systemMessaages import CustomMessages
from random import randint

custom_messages = CustomMessages()


class VoterCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(is_public)
    @commands.check(has_wallet)
    async def voter(self, ctx):
        """
        Ballot entry point
        """
        if ctx.invoked_subcommand is None:
            self.guild_string = self.bot.get_prefix_help(ctx.guild.id)
            title = ':joystick: __Welcome to Ballot voting system__ :joystick: '
            description = "Below are all presented command which allow you to participate in " \
                          "community voting with your balance."
            list_of_values = [
                {"name": ":information_source: About ballot system",
                 "value": f"```{self.guild_string}ballot about```"},
                {"name": ":ballot_box: Check Ballot Details",
                 "value": f"```{self.guild_string}ballot```"},
                {"name": ":ballot_box: Cast vote to project",
                 "value": f"```{self.guild_string}voter vote FOR/AGAINST <ballot ID> <amount>```"},

            ]
            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                c=Colour.dark_gold())

    @voter.command()
    async def vote(self, ctx, direction: str, ballot_id: int, amount: int):
        """
        Casting a vote
        """
        vote = direction.upper()
        if vote in ["FOR", "AGAINST"]:
            # Check if ballot ID exists
            if self.bot.backoffice.voting_manager.check_ballot_id(ballot_id=ballot_id):
                ballot_data = self.bot.backoffice.voting_manager.get_ballot_data(ballot_id=ballot_id,
                                                                                 server_id=ctx.guild.id)

                if not ctx.author.id in ballot_data["votersList"]:
                    # Get the user balance
                    user_balance = self.bot.backoffice.wallet_manager.get_ticker_balance(
                        asset_code=ballot_data["assetCode"].lower(),
                        user_id=ctx.message.author.id)
                    # Converting amount to atomic
                    amount_atomic = amount * (10 ** 7)
                    if amount_atomic < user_balance:
                        # deduct the balance due to the vote
                        if self.bot.backoffice.wallet_manager.update_coin_balance(coin=ballot_data["assetCode"].lower(),
                                                                                  user_id=ctx.message.author.id,
                                                                                  amount=int(amount_atomic),
                                                                                  direction=2):

                            # Make data ready for mongo update
                            new_ballot_data = dict()
                            if vote == "FOR":
                                new_ballot_data.update({"toIncrement": {"votesFor": amount_atomic}})

                                ballot_data["voterFor"].append({"voterId": int(ctx.author.id),
                                                                "voterName": f'{ctx.author}',
                                                                "votePwr": amount_atomic})
                                ballot_data["votersList"].append(int(ctx.author.id))
                                new_ballot_data.update({"toUpdate": {"voterFor": ballot_data["voterFor"],
                                                                     "votersList": ballot_data["votersList"]}})
                            else:
                                new_ballot_data.update({"toIncrement": {"votesAgainst": amount_atomic}})

                                ballot_data["voterAgainst"].append({"voterId": int(ctx.author.id),
                                                                    "voterName": f'{ctx.author}',
                                                                    "votePwr": amount_atomic})
                                ballot_data["votersList"].append(int(ctx.author.id))
                                new_ballot_data.update({"toUpdate": {"voterAgainst": ballot_data["voterAgainst"],
                                                                     "votersList": ballot_data["votersList"]}})

                                # Update new ballot box state
                            if self.bot.backoffice.voting_manager.update_ballot_box(ballot_id=ballot_id,
                                                                                    guild_id=ctx.guild.id,
                                                                                    new_ballot_data=new_ballot_data):

                                message = f'You have successfully casted {amount:.7f} {ballot_data["assetCode"].upper()} ' \
                                          f'votes {vote.upper()} for ballot box with ID {ballot_id}. Votes ' \
                                          f'will be returned to your wallet on {ballot_data["endBallot"]}.'
                                await custom_messages.system_message(ctx=ctx, color_code=0, message=message,
                                                                     destination=1,
                                                                     sys_msg_title="Vote received successfully")
                            else:
                                message = f'Ballot box could not be update. Please try again later'
                                await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                     destination=0,
                                                                     sys_msg_title="Vote error")
                                self.bot.backoffice.wallet_manager.update_coin_balance(
                                    coin=ballot_data["assetCode"].lower(),
                                    user_id=ctx.message.author.id,
                                    amount=int(amount_atomic),
                                    direction=1)
                        else:
                            message = f'Votes could not be deducted from your wallet. Please try again later or ' \
                                      f'contact Crypto Link Staff. '
                            await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                                 destination=0,
                                                                 sys_msg_title="Vote error")
                    else:
                        message = f'Your vote count has exceeded your wallet balance. Current wallet balance' \
                                  f' is {user_balance / (10 ** 7)} {ballot_data["assetCode"].upper()} while your' \
                                  f' vote amount is {amount} {ballot_data["assetCode"].upper()}'
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                             destination=0,
                                                             sys_msg_title="Vote error")
                else:
                    message = f'You have already submitted your votes to Ballot box with ID {ballot_id}'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                         destination=0,
                                                         sys_msg_title="Vote error")
            else:
                message = f'Ballot box with ID {ballot_id} could not be found in the system. Please' \
                          f'recheck the ID again. If the issue persists, please contact staff of Crypto Link team.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                     destination=0,
                                                     sys_msg_title="Vote error")
        else:
            message = f'Vote direction can be either FOR or AGAINST. Please try again. '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message,
                                                 destination=0,
                                                 sys_msg_title="Vote error")


def setup(bot):
    bot.add_cog(VoterCommands(bot))
