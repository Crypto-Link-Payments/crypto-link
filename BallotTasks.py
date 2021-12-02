from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from colorama import Fore, init
from datetime import datetime
from nextcord import Color, Embed
from utils.tools import Helpers
from pprint import pprint

import time

helper = Helpers()
init(autoreset=True)
channels = helper.read_json_file(file_name='autoMessagingChannels.json')


class BallotTasks:
    def __init__(self, backoffice, bot):
        self.backoffice = backoffice
        self.twitter_cred = self.backoffice.twitter_details
        self.bot = bot

    async def send_ballot_report(self, ballot: dict):
        """
        Ballot notification report once closed
        """
        if int(ballot["votesFor"]) > ballot["votesAgainst"]:
            c = Color.green()
            result = 'FOR'
        elif int(ballot["votesFor"]) < ballot["votesAgainst"]:
            c = Color.red()
            result = 'AGAINST'
        elif int(ballot["votesFor"]) == ballot["votesAgainst"]:
            c = Color.dark_green()
            result = 'UNDECIDED'

        ballot_report = Embed(title=f':tada: Ballot finished',
                              description="Ballot has finished. Below is result analysis. ",
                              colour=c)
        ballot_report.add_field(name=":id: Ballot ID",
                                value=f'{ballot["ballotId"]}')
        ballot_report.add_field(name=":coin: Ballot Asset ",
                                value=f'{ballot["assetCode"]}')
        ballot_report.add_field(name=":bar_chart: Vote count ",
                                value=f'```Votes FOR {int(ballot["votesFor"] / (10 ** 7))}\n'
                                      f'Votes AGAINST {int(ballot["votesAgainst"] / (10 ** 7))}\n'
                                      f'----------------------------\n'
                                      f'Winner: {result}```',
                                inline=False)
        ballot_report.add_field(name=f':receipt: Ballot Voter Metrics',
                                value=f'```For: {len(ballot["voterFor"])}\n'
                                      f'Against: {len(ballot["voterFor"])}\n'
                                      f'Total voted: {len(ballot["voterFor"]) + len(ballot["voterAgainst"])}```',
                                inline=False)

        try:
            dest = await self.bot.fetch_user(int(ballot["creatorId"]))  # Owner
            await dest.send(embed=ballot_report)
        except Exception as e:
            print(e)

        channel_id = ballot["notificationChannelId"]
        if channel_id:
            channel = self.bot.get_channel(int(ballot["notificationChannelId"]))
            try:
                await channel.send(embed=ballot_report)
            except Exception as e:
                print(e)
        else:
            pass

    async def distribute_votes_to_users(self, ballot: dict):
        """
        Distribute money back to voters
        """
        for user in ballot["voterFor"]:
            if self.bot.backoffice.wallet_manager.update_coin_balance(coin=ballot["assetCode"].lower(),
                                                                      user_id=user["voterId"],
                                                                      amount=int(user["votePwr"]),
                                                                      direction=1):
                print(Fore.RED + f'Voter {user["voterName"]} ({user["voterId"]}) votes returned ')

            else:
                print(Fore.RED + f'Voter {user["voterName"]} ({user["voterId"]}) votes could not be returned ')
        for user in ballot["voterAgainst"]:
            if self.bot.backoffice.wallet_manager.update_coin_balance(coin=ballot["assetCode"].lower(),
                                                                      user_id=user["voterId"],
                                                                      amount=int(user["votePwr"]),
                                                                      direction=1):
                print(Fore.RED + f'Voter {user["voterName"]} ({user["voterId"]}) votes returned ')
            else:
                print(Fore.RED + f'Voter {user["voterName"]} ({user["voterId"]}) votes could not be returned ')

        return

    async def send_ballot_snapshot(self, ballot: dict, destination=None):
        """
        Creating ballot snapshot
        """
        author = await self.bot.fetch_user(user_id=int(ballot["creatorId"]))

        ending_time = datetime.fromtimestamp(int(ballot['expirationTs']))
        count_left = ending_time - datetime.utcnow()

        total_voted = len(ballot["voterFor"]) + len(ballot["voterAgainst"])
        total_votes = ballot["votesAgainst"] + ballot["votesFor"]

        ballot_data = Embed(title=f':ballot_box: Ballot snapshot data',
                            description="Ballot box vote count 24h snapshot",
                            colour=Color.dark_gold())
        ballot_data.add_field(name=f':coin: Ballot voting asset',
                              value=f'`{ballot["assetCode"]}`')
        ballot_data.add_field(name=f':id: Ballot ID',
                              value=f'`{ballot["ballotId"]}`')
        ballot_data.add_field(name=f':calendar: Ballot timeframe',
                              value=f'```Start: {ballot["startBallot"]}\n'
                                    f'End: {ballot["endBallot"]}\n'
                                    f'Left: {count_left}```',
                              inline=False)
        ballot_data.add_field(name=f':bar_chart: Current state',
                              value=f'```Users Voted: {total_voted}\n'
                                    f'Total votes: {int(total_votes / (10 ** 7))}\n'
                                    f'====================\n'
                                    f'Votes For: {int(ballot["votesFor"] / (10 ** 7))}\n'
                                    f'Votes Against: {int(ballot["votesAgainst"] / (10 ** 7))}```',
                              inline=False)
        ballot_data.set_footer(text=f"Ballot box creator: {author}")
        if not destination:
            channel = self.bot.get_channel(int(ballot["notificationChannelId"]))
            try:
                await channel.send(embed=ballot_data)
            except Exception as e:
                print(Fore.RED + f"BALLOT SNAPSHOT ERROR {e}")
                pass
        else:
            try:
                await destination.send(embed=ballot_data)
            except Exception as e:
                print(Fore.RED + f"BALLOT SNAPSHOT ERROR {e}")
                pass

    async def check_expired_boxes(self):
        """
        Check the expiration times of live ballots
        """
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(Fore.CYAN + f"{current_time} --> CHECKING BALLOT BOXES ")

        now = datetime.utcnow().timestamp()  # Gets current time of the system in unix format
        overdue_ballots = self.bot.backoffice.voting_manager.get_overdue_ballots(timestamp=int(now))
        if overdue_ballots:
            for ballot in overdue_ballots:
                await self.send_ballot_report(ballot=ballot)  # Send ballot report to owner
                if self.bot.backoffice.voting_manager.remove_overdue_ballot(ballot_id=ballot["ballotId"],
                                                                            guild_id=ballot["guildId"]):
                    await self.distribute_votes_to_users(ballot=ballot)
                    print(Fore.GREEN + f'{ballot["ballotId"]} Remove from live collection')
                    if self.bot.backoffice.voting_manager.store_ballot_to_history(ballot=ballot):
                        print(Fore.GREEN + f'{ballot["ballotId"]} Moved to history')
                    else:
                        print(Fore.RED + f'{ballot["ballotId"]} Could not be stored in history')
                else:
                    print(Fore.RED + f'{ballot["ballotId"]} Could not be removed')
        else:
            print(Fore.BLUE + f'No expired ballot boxes')

    async def ballot_state_notifications(self):
        """
        Ballot box state snapshot trigger
        """
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(Fore.CYAN + f"{current_time} --> SENDING BALLOT SNAPSHOTS")
        now = datetime.utcnow().timestamp()  # Gets current time of the system in unix format
        live_ballots = self.bot.backoffice.voting_manager.get_live_ballots(timestamp=int(now))
        if live_ballots:
            for ballot in live_ballots:
                ballot_channel = ballot["notificationChannelId"]
                if ballot_channel:
                    await self.send_ballot_snapshot(ballot=ballot)
                else:
                    guild = self.bot.get_guild(ballot["guildId"])
                    member = guild.get_member(ballot["creatorId"])
                    await self.send_ballot_snapshot(ballot=ballot, destination=member)

                    print(Fore.YELLOW + f"Ballot ID: {ballot['ballotId']} has not active notification"
                                        f" channels")
        else:
            print(Fore.BLUE + f'There is no live ongoing ballots currently')


def start_ballot_scheduler(timed_updater):
    scheduler = AsyncIOScheduler()
    print(Fore.LIGHTBLUE_EX + 'Started ballot monitor')
    scheduler.add_job(timed_updater.ballot_state_notifications,
                      CronTrigger(hour='00', minute='01'), misfire_grace_time=10, max_instances=20)
    scheduler.add_job(timed_updater.check_expired_boxes,
                      CronTrigger(minute='00', second='25'), misfire_grace_time=10, max_instances=20)
    scheduler.start()
    print(Fore.LIGHTBLUE_EX + 'Start ballot corn Monitors : DONE')
    return scheduler
