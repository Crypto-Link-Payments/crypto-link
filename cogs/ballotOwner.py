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


class BallotOwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_ballot_id(self):
        """
        Get random ballot ID
        """
        ballot_id = int(randint(0, 100000))
        if not self.bot.backoffice.voting_manager.check_ballot_id(ballot_id=ballot_id):
            return ballot_id
        else:
            return int(randint(0, 100000))

    @commands.group()
    @commands.check(is_public)
    @commands.check(has_ballot_access)
    async def ballot(self, ctx):
        """
        Ballot entry point
        """
        if ctx.invoked_subcommand is None:
            self.guild_string = self.bot.get_prefix_help(ctx.guild.id)
            title = ':joystick: __Ballot Voting System commands for owners__ :joystick: '
            description = "All available commands to operate with guild system."
            list_of_values = [
                {"name": ":bellhop: Create new ballot :bellhop: ",
                 "value": f"`{self.guild_string}ballot new <ballot_name> <voting_asset_code> <days = INT>`"},
            ]
            await custom_messages.embed_builder(ctx=ctx, title=title, description=description, data=list_of_values,
                                                c=Colour.dark_gold())

    @ballot.command()
    async def new(self, ctx, ballot_name: str, voting_asset_code: str, days: int, ballot_channel: TextChannel=None):
        if ballot_channel:
            notify_channel = ballot_channel.id
        else:
            notify_channel = None
        if days >= 1:
            supported = [sup["assetCode"] for sup in self.bot.backoffice.token_manager.get_registered_tokens() if
                         sup["assetCode"] == voting_asset_code.upper()]
            if supported:
                ballot_name = ballot_name.lower()
                if not self.bot.backoffice.helper.check_for_special_char(string=ballot_name):
                    voting_asset_code = voting_asset_code.strip().upper()
                    start = datetime.utcnow()
                    # TODO change this to days on release
                    td = timedelta(minutes=days)
                    end = start + td
                    gap = end - start
                    unix_today = int(time.mktime(start.timetuple()))
                    unix_future = int(time.mktime(end.timetuple()))
                    ballot_id = self.get_ballot_id()
                    ballot_data = {
                        "ballotId": int(ballot_id),
                        "notificationChnId":notify_channel,
                        "notificationChannel": ballot_channel.id,
                        "guildId": ctx.guild.id,
                        "creatorId": ctx.author.id,
                        "assetCode": voting_asset_code.upper(),
                        "votesFor": int(0),
                        "votesAgainst": int(0),
                        "voterFor": list(),
                        "voterAgainst": list(),
                        "createdTs": int(unix_today),
                        "expirationTs": int(unix_future),
                        "startBallot": f'{start} UTC',
                        "endBallot": f'{end} UTC',
                        "ballotLength": gap
                    }

                    if self.bot.backoffice.voting_manager.new_ballot(ballot_data):
                        ballot_embed = Embed(title=f':ballot_box: __Ballot box successfully created__ :ballot_box:',
                                             description=f'You have successfully initiate ballot vote box. Now'
                                                         f' you can start to collect member votes. Once time '
                                                         f'expires system will automatically produce report for you'
                                                         f' and distribute back votes to the voters. ',
                                             colour=Colour.green())
                        ballot_embed.add_field(name=f':bank: Ballot server',
                                               value=f'{ctx.guild}')
                        ballot_embed.add_field(name=f':disguised_face: Ballot manager',
                                               value=f'{ctx.author} ({ctx.author.id})')
                        ballot_embed.add_field(name=f':coin: Ballot voting cryptocurrency',
                                               value=f'{voting_asset_code.upper()}')
                        ballot_embed.add_field(name=f':id: Ballot Box Identifier',
                                               value=f'{ballot_id}',
                                               inline=False)
                        ballot_embed.add_field(name=f':calendar: Length and expiration',
                                               value=f'```Started: {start} UTC\n'
                                                     f'End: {end} UTC\n'
                                                     f'Length: {days} day/s```',
                                               inline=False)
                        ballot_embed.add_field(name=f':information_source: Additional information',
                                               value=f'Members can now cast votes either FOR or AGAINST with'
                                                     f' cryptocurrency {voting_asset_code.upper()} through the command'
                                                     f' `{self.guild_string}vote FOR/AGAINST {ballot_id} <amount>`')
                        await ctx.channel.send(embed=ballot_embed)

                    else:
                        message = f'Ballot could not be create. please try again later,'
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                             sys_msg_title="Ballot creation error!")
                else:
                    message = f'Ballot name either contains special characters or has exceeded maximal name legth.\n' \
                              f'```Allowed length = 15\n' \
                              f'Ballot name length =  {len(ballot_name)}```'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                         sys_msg_title="Ballot creation error!")
            else:
                message = f'{voting_asset_code.upper()} is not supported by Crypto Link, therefore it can ' \
                          f'not be used as the expression of voting power.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                     sys_msg_title="Ballot voting access error!")
        else:
            message = f'Length of the Ballot needs to be at least 1 day '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title="Ballot voting access error!")

    @ballot.error
    async def ballot_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            message = f'You do not have access to Ballot Voting System on {ctx.guild}, or command has been executed' \
                      f' over DM. '
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=0,
                                                 sys_msg_title="Ballot voting access error!")


def setup(bot):
    bot.add_cog(BallotOwnerCommands(bot))
