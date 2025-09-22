import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from colorama import Fore, init
from datetime import datetime, timezone
from nextcord import Color, Embed
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

    async def check_expired_membership(self):
        """
        Function checks for expired users on community nad removes them if necessary
        """
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(Fore.GREEN + f"{current_time} --> CHECKING FOR USERS WITH EXPIRED ROLES ")

        now = datetime.now(timezone.utc).timestamp()  # Gets current time of the system in unix format
        merchant_manager = self.backoffice.merchant_manager
        overdue_members = merchant_manager.get_over_due_users(
            timestamp=int(now))  # Gets all overdue members from database
        bot = self.bot
        if overdue_members:
            bot_guilds = [guild for guild in bot.guilds]  # get all guilds bot has access to
            for mem in overdue_members:
                mem_id = mem['userId']
                mem_role_id = mem['roleId']
                mem_role_community_id = mem['communityId']

                # Check if community where role was created still has bot
                if [guild.id for guild in bot_guilds if mem_role_community_id == guild.id]:
                    # get guild and member
                    guild = bot.get_guild(mem_role_community_id)
                    member = guild.get_member(mem_id)
                    # Check if member still exists
                    if member in guild.members:
                        role = guild.get_role(mem_role_id)  # Get the role
                        if role:
                            if role in member.roles:
                                print(Fore.YELLOW + f"EXPIRED FOUND:\n"
                                                    f"1. Removing role form user {member}")
                                await member.remove_roles(role, reason='Merchant notification -> Role expired')
                                if merchant_manager.remove_overdue_user_role(community_id=mem_role_community_id,
                                                                             role_id=mem_role_id, user_id=mem_id):
                                    print(Fore.YELLOW + "active membership removed")
                                    expired = Embed(title=':octagonal_sign:  __Role Expired__ :octagonal_sign:',
                                                    description='Your active membership has expired.',
                                                    color=Color.dark_red())
                                    expired.add_field(name=':bank: Origin of role expiration:bank: ',
                                                      value=f'```{guild.name}```',
                                                      inline=False)
                                    expired.add_field(name=":man_juggling: Expired Role :man_juggling: ",
                                                      value=f'```{role.name}```')
                                    expired.add_field(name=":information_source: Information :information_source: ",
                                                      value=" In order to obtain back all privileges please re-purchase"
                                                            " the role directly from the community.",
                                                      inline=False)
                                    expired.set_footer(text="This message was sent to you privately.")
                                    try:
                                        await member.send(embed=expired)
                                    except discord.Forbidden:
                                        pass
                                else:
                                    channel_sys = channels["merchant"]
                                    # send notification to merchant for system if user could not be removed from database
                                    expired_sys = Embed(
                                        title='__Expired user could not be removed from system__',
                                        colour=Color.red())
                                    expired_sys.set_thumbnail(url=bot.user.avatar.url)
                                    expired_sys.add_field(name='Community',
                                                          value=guild.name,
                                                          inline=False)
                                    expired_sys.add_field(name="Expired Role",
                                                          value=role.name)
                                    expired_sys.add_field(name="User details",
                                                          value=f'Role ID: {mem_role_id}\n'
                                                                f'Community ID: {mem_role_community_id}\n'
                                                                f'Member ID: {mem_id}')
                                    merch_channel = bot.get_channel(int(channel_sys))
                                    await merch_channel.send(embed=expired_sys)
                            else:
                                merchant_manager.remove_overdue_user_role(community_id=mem_role_community_id,
                                                                          user_id=mem_id, role_id=mem_role_id)
                        else:
                            merchant_manager.remove_monetized_role_from_system(role_id=mem_role_id,
                                                                               community_id=mem_role_community_id)
                            merchant_manager.bulk_user_clear(community_id=mem_role_community_id, role_id=mem_role_id)
                    else:
                        merchant_manager.delete_user_from_applied(community_id=mem_role_community_id, user_id=mem_id)
                else:
                    pass
        else:
            print(Fore.GREEN + 'There are no overdue members in the system going to sleep!')
            print('===========================================================')


def start_merchant_scheduler(timed_updater):
    scheduler = AsyncIOScheduler()
    print(Fore.LIGHTBLUE_EX + 'Started merchant monitor')
    scheduler.add_job(timed_updater.check_expired_membership,
                      CronTrigger(minute='5,10,15,20,25,30,35,40,45,50,55,00'), misfire_grace_time=10, max_instances=20)
    scheduler.start()
    print(Fore.LIGHTBLUE_EX + 'Starte merchant corn Monitors : DONE')
    return scheduler
