from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from colorama import Fore, init
from datetime import datetime
from discord import Color, Embed
from utils.tools import Helpers

import time

helper = Helpers()
init(autoreset=True)
channels = helper.read_json_file(file_name='autoMessagingChannels.json')


class MerchantTasks:
    def __init__(self, backoffice, bot):
        self.backoffice = backoffice
        self.twitter_cred = self.backoffice.twitter_details
        self.bot = bot

    async def distribute_votes_to_users(self, voter_details: dict):
        # Get use from system
        # Get vote amount
        # distribute to wallet
        pass

    async def send_ballot_snapshot(self, ballot: dict):
        """
        Creating ballot snapshot
        """
        author = await self.bot.fetch_user(user_id=int(ballot["creatorId"]))

        ending_time = datetime.fromtimestamp(int(ballot['expirationTs']))
        count_left = ending_time - datetime.utcnow()

        total_voted = len(ballot["voterFor"]) + len(ballot["voterAgainst"])
        total_votes = ballot["votesAgainst"] + ballot["votesFor"]

        ballot_data = Embed(title=f':id: {ballot["ballotId"]}Ballot snapshot data',
                            description="Ballot box vote count snapshot",
                            colour=Color.dark_gold())
        ballot_data.add_field(name=f':calendar: Ballot timeframe',
                              value=f'```Start: {ballot["startBallot"]}\n'
                                    f'End: {ballot["endBallot"]}\n'
                                    f'Left: {count_left}```')
        ballot_data.add_field(name=f':ballot_box: Current state',
                              value=f'```Voted: {total_voted}\n'
                                    f'Votes: {total_votes}\n'
                                    f'====================\n'
                                    f'Votes For: {ballot["votesFor"]}\n'
                                    f'Votes Against: {ballot["votesAgainst"]}')
        ballot_data.set_footer(text=f"Ballot box creator: {author}")
        channel = self.bot.get_channel(id=int(ballot["notificationChannelId"]))
        try:
            await channel.send(embed=ballot_data)
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
        overdue_ballots = self.backoffice.voting_manager.get_overdue_ballots(timestamp=int(now))

        if overdue_ballots:
            bot_guilds = [guild for guild in self.bot.guilds]
            for ballot in overdue_ballots:
                ballot_guild = self.bot.get_guild(id=ballot["guildId"])  # Ballot guild
                dest = await self.bot.fetch_user(user_id=int(ballot["ballotId"]))

    async def ballot_state_notifications(self):
        """
        Ballot box state snapshot trigger
        """
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(Fore.CYAN + f"{current_time} --> SENDING BALLOT SNAPSHOTS")
        now = datetime.utcnow().timestamp()  # Gets current time of the system in unix format
        live_ballots = self.backoffice.voting_manager.get_live_ballots(timestamp=int(now))
        if live_ballots:
            for ballot in live_ballots:
                ballot_channel = ballot["notificationChannelId"]
                if ballot_channel:
                    await self.send_ballot_snapshot(ballot=ballot)
                else:
                    print(Fore.YELLOW + f"Ballot ID: {ballot['ballotId']} has not active notification"
                                        f" channels")
        else:
            print(Fore.BLUE + f'There is no live ongoing ballots currently')


def start_merchant_scheduler(timed_updater):
    scheduler = AsyncIOScheduler()
    print(Fore.LIGHTBLUE_EX + 'Started merchant monitor')
    scheduler.add_job(timed_updater.ballot_state_notifications,
                      CronTrigger(second='00'), misfire_grace_time=10, max_instances=20)
    scheduler.start()
    print(Fore.LIGHTBLUE_EX + 'Starte merchant corn Monitors : DONE')
    return scheduler
