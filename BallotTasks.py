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

    async def send_ballot_report(self, desc, ballot: dict):
        """
        Ballot notification report once closed
        """
        ballot_report = Embed(title=f':tada: Ballot finished',
                              description=desc,
                              colour=Color.green())
        ballot_report.add_field(name=":id: Ballot ID",
                                value=f'{ballot["ballotId"]}')
        ballot_report.add_field(name=":id: Ballot ID",
                                value=f'{ballot["ballotId"]}')
        ballot_report.add_field(name=":coin: Ballot Asset ",
                                value=f'{ballot["ballotId"]}')
        ballot_report.add_field(name=f'Vote result',
                                value=f'```For: {int(ballot["voterFor"] / (10 ** 7))}\n'
                                      f'Against: {int(ballot["voterFor"] / (10 ** 7))}\n'
                                      f'Total voted: {len(ballot["voterFor"]) + len(ballot["voterAgainst"])}```',
                                inline=False)

        dest = await self.bot.fetch_user(user_id=int(ballot["creatorId"]))  # Owner
        await dest.send(embed=ballot_report)

        channel = self.bot.get_channel(id=int(ballot["notificationChannelId"]))
        if channel:
            await channel.send(embed=ballot_report)
        else:
            pass
        return

    async def distribute_votes_to_users(self, ballot: dict):
        for user in ballot["voterFor"]:
            self.bot.backoffice.wallet_manager.update_coin_balance(coin=ballot["assetCode"].lower(),
                                                                   user_id=user["voterId"],
                                                                   amount=int(user["votePwr"]),
                                                                   direction=1)
        for user in ballot["voterAgainst"]:
            self.bot.backoffice.wallet_manager.update_coin_balance(coin=ballot["assetCode"].lower(),
                                                                   user_id=user["voterId"],
                                                                   amount=int(user["votePwr"]),
                                                                   direction=1)
        return

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
        owner_text = f'Ballot you have initiated has expired. Below are presented results and details.'
        channel_text = f'Ballot has finished and all votes have been distributed back to users'
        if overdue_ballots:
            for ballot in overdue_ballots:
                await self.send_ballot_report(desc=owner_text, ballot=ballot)  # Send ballot report to owner
                await self.send_ballot_report(desc=channel_text, ballot=ballot)  # Report to channel origin

                if self.bot.backoffice.voting_manager.remove_overdue_ballot(ballot_id=ballot["ballotId"],
                                                                            guild_id=ballot["guildId"]):
                    print(Fore.GREEN + f'{ballot["ballotId"]} Remove from live collection')

                    if self.bot.backoffice.voting_manager.store_ballot_to_history(ballot=ballot):
                        print(Fore.GREEN + f'{ballot["ballotId"]} Moved to history')
                    else:
                        print(Fore.RED + f'{ballot["ballotId"]} Could not be stored in history')
                else:
                    print(Fore.RED + f'{ballot["ballotId"]} Could not be removed')

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
