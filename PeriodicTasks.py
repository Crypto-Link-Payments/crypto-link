import time
from datetime import datetime
import tweepy
from re import search

import discord
from discord import Embed, Color
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from colorama import Fore, init

from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

init(autoreset=True)
custom_messages = CustomMessages()
helper = Helpers()
channels = helper.read_json_file(file_name='autoMessagingChannels.json')


def get_time():
    """
    Get local time on the computer
    """
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time


class PeriodicTasks:
    def __init__(self, backoffice, bot):
        self.backoffice = backoffice
        self.notification_channels = self.backoffice.auto_messaging_channels["depositNotifications"]
        self.bot = bot
        self.twitter_acc = self.backoffice.twitter_details

    async def global_bot_stats_update(self, tx):
        bot_stats = {
            "depositCount": 1,
            "depositAmount": float(round(int(tx['asset_type']["amount"]) / 10000000))
        }
        await self.backoffice.stats_manager.update_cl_on_chain_stats(ticker=tx['asset_type']['code'].lower(),
                                                                     stat_details=bot_stats)

    def filter_transaction(self, new_transactions: list):
        # Building list of deposits if memo included
        stellar_manager = self.backoffice.stellar_manager
        tx_with_memo_special = [tx for tx in new_transactions if 'memo' in tx.keys() and helper.check_for_special_char(tx["memo"])]
        tx_with_memo = [tx for tx in new_transactions if 'memo' in tx.keys() and not helper.check_for_special_char(tx["memo"])]  # GET Transactions who have memo
        tx_with_no_memo = [tx for tx in new_transactions if tx not in tx_with_memo]  # GET transactions without memo
        tx_with_registered_memo = [tx for tx in tx_with_memo if stellar_manager.check_if_stellar_memo_exists(
            tx_memo=tx['memo'])]  # GET tx with registered memo
        tx_with_not_registered_memo = [tx for tx in tx_with_memo if
                                       tx not in tx_with_registered_memo]  # GET tx with not registered memo
        return tx_with_registered_memo, tx_with_not_registered_memo, tx_with_no_memo,tx_with_memo_special

    async def process_tx_with_no_memo(self, channel, no_memo_transaction):
        stellar_manager = self.backoffice.stellar_manager
        for tx in no_memo_transaction:
            if not stellar_manager.check_if_deposit_hash_processed_unprocessed_deposits(tx_hash=tx['hash']):
                if stellar_manager.stellar_deposit_history(deposit_type=2, tx_data=tx):
                    await custom_messages.send_unidentified_deposit_msg(channel=channel, tx_details=tx)
                    await self.global_bot_stats_update(tx=tx)
                else:
                    print(Fore.RED + f'There has been an issue while processing tx with no memo \n'
                                     f'HASH{tx["hash"]}')
            else:
                print(Fore.YELLOW + 'Unknown processed already')

    async def process_tx_with_memo(self, channel, memo_transactions):
        bot = self.bot
        stellar_manager = self.backoffice.stellar_manager
        stats_manager = self.backoffice.stats_manager
        wallet_manager = self.backoffice.wallet_manager
        guild_profiles = self.backoffice.guild_profiles
        for tx in memo_transactions:
            # check if processed if not process them
            if not stellar_manager.check_if_deposit_hash_processed_succ_deposits(tx['hash']):
                if stellar_manager.stellar_deposit_history(deposit_type=1, tx_data=tx):
                    # Update balance based on incoming asset
                    if not helper.check_for_special_char(tx["memo"]):
                        if wallet_manager.update_coin_balance_by_memo(memo=tx['memo'], coin=tx['asset_type']["code"],
                                                                      amount=int(tx['asset_type']["amount"])):
                            # If balance updated successfully send the message to user of processed deposit
                            user_id = wallet_manager.get_discord_id_from_memo(memo=tx['memo'])  # Return usr int number
                            dest = await bot.fetch_user(user_id=int(user_id))

                            await custom_messages.deposit_notification_message(recipient=dest, tx_details=tx)

                            # Channel system message on deposit
                            await custom_messages.sys_deposit_notifications(channel=channel,
                                                                            user=dest, tx_details=tx)

                            # Explorer messages
                            load_channels = [bot.get_channel(id=int(chn)) for chn in
                                             guild_profiles.get_all_explorer_applied_channels()]

                            explorer_msg = f':inbox_tray: Someone deposited {round(tx["asset_type"]["amount"] / 10000000, 7)} ' \
                                           f'{tx["asset_type"]["code"].upper()} to {bot.user}'

                            await custom_messages.explorer_messages(applied_channels=load_channels,
                                                                    message=explorer_msg,
                                                                    on_chain=True, tx_type='deposit')

                            on_chain_stats = {
                                f"{tx['asset_type']['code'].lower()}.depositsCount": 1,
                                f"{tx['asset_type']['code'].lower()}.totalDeposited": round(
                                    int(tx['asset_type']["amount"]) / 10000000,
                                    7)}

                            await stats_manager.update_user_on_chain_stats(user_id=dest.id, stats_data=on_chain_stats)

                            await self.global_bot_stats_update(tx=tx)

                        else:
                            print(Fore.RED + f'TX Processing error: \n'
                                             f'{tx}')
                    else:
                        print(Fore.RED + f'Special characters in Memo write to file: \n'
                                         f'{tx}')
                        await custom_messages.send_special_char_notification(channel=channel, tx=tx)

                else:
                    print(Fore.RED + 'Could not store to history')
            else:
                print(Fore.LIGHTCYAN_EX + 'No new legit tx')

    async def process_tx_with_not_registered_memo(self, channel, no_registered_memo):
        stellar_manager = self.backoffice.stellar_manager
        for tx in no_registered_memo:
            if not stellar_manager.check_if_deposit_hash_processed_unprocessed_deposits(tx_hash=tx['hash']):
                if not helper.check_for_special_char(tx["memo"]):
                    if stellar_manager.stellar_deposit_history(deposit_type=2, tx_data=tx):
                        await custom_messages.send_unidentified_deposit_msg(channel=channel, tx_details=tx)
                        await self.global_bot_stats_update(tx=tx)
                    else:
                        print(Fore.RED + f'There has been an issue while processing tx with no memo \n'
                                         f'HASH{tx["hash"]}')
                else:
                    print(Fore.RED + f'Special characters in Memo write to file: \n'
                                     f'{tx}')
                    await custom_messages.send_special_char_notification(channel=channel, tx=tx)
            else:
                print(Fore.YELLOW + 'Unknown processed already')

    async def process_tx_with_special_chart(self, channel):
        pass


    async def check_stellar_hot_wallet(self):
        """
        Functions initiates the check for stellar incoming deposits and processes them
        """
        bot = self.bot
        print(Fore.GREEN + f"{get_time()} --> CHECKING STELLAR CHAIN FOR DEPOSITS")
        pag = helper.read_json_file('stellarPag.json')
        new_transactions = self.backoffice.stellar_wallet.get_incoming_transactions(pag=int(pag['pag']))
        channel_id = self.backoffice.auto_messaging_channels["stellar"]  # Sys channel where details are sent
        if new_transactions:
            # Filter transactions

            tx_with_registered_memo, tx_with_not_registered_memo, tx_with_no_memo,tx_with_memo_special= self.filter_transaction(
                new_transactions)
            if tx_with_registered_memo:
                channel = bot.get_channel(id=int(self.notification_channels['memoRegistered']))
                await self.process_tx_with_memo(channel=channel, memo_transactions=tx_with_registered_memo)
            if tx_with_not_registered_memo:
                channel = bot.get_channel(id=int(self.notification_channels['memoNotRegistered']))
                await self.process_tx_with_not_registered_memo(channel=channel,
                                                               no_registered_memo=tx_with_not_registered_memo)
            if tx_with_no_memo:
                channel = bot.get_channel(id=int(self.notification_channels['memoNone']))
                await self.process_tx_with_no_memo(channel=channel, no_memo_transaction=tx_with_no_memo)
                
            if tx_with_memo_special:
                channel = bot.get_channel(id=int(self.notification_channels['memoSpecialChar']))
                await self.process_tx_with_special_chart(channel=channel)

            last_checked_pag = new_transactions[-1]["paging_token"]
            if helper.update_json_file(file_name='stellarPag.json', key='pag', value=int(last_checked_pag)):
                print(Fore.GREEN + f'Peg updated successfully from {pag} --> {last_checked_pag}')
            else:
                print(Fore.RED + 'There was an issue with updating pag')

            print(Fore.GREEN + '==============DONE=================\n'
                               '==========GOING TO SLEEP FOR 1 MINUTE=====')
        else:
            print(Fore.CYAN + 'No new incoming transactions in range...Going to sleep for 60 seconds')
            print('==============================================')

    async def check_expired_roles(self):
        """
        Function checks for expired users on community nad removes them if necessary
        """
        print(Fore.GREEN + f"{get_time()} --> CHECKING FOR USERS WITH EXPIRED ROLES ")
        now = datetime.utcnow().timestamp()  # Gets current time of the system in unix format
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
                    guild = bot.get_guild(id=mem_role_community_id)
                    member = guild.get_member(mem_id)
                    # Check if member still exists
                    if member in guild.members:
                        role = guild.get_role(role_id=mem_role_id)  # Get the role
                        if role:
                            if role in member.roles:
                                await member.remove_roles(role, reason='Merchant notification -> Role expired')
                                if merchant_manager.remove_overdue_user_role(community_id=mem_role_community_id,
                                                                             role_id=mem_role_id, user_id=mem_id):
                                    expired = discord.Embed(name='Expired Role',
                                                            title='__Role Expiration Notification__',
                                                            description=' You have received this notification, '
                                                                        'because the role you have purchased has expired'
                                                                        ' and has been therefore removed. More details '
                                                                        'bellow.')

                                    expired.set_thumbnail(url=bot.user.avatar_url)
                                    expired.add_field(name='Community',
                                                      value=guild.name,
                                                      inline=False)
                                    expired.add_field(name="Expired Role",
                                                      value=role.name)

                                    await member.send(embed=expired)
                                else:
                                    channel_sys = channels["merchant"]
                                    # send notification to merchant for system if user could not be removed from database
                                    expired_sys = discord.Embed(
                                        title='__Expired user could not be removed from system__',
                                        colour=discord.Color.red())
                                    expired_sys.set_thumbnail(url=bot.user.avatar_url)
                                    expired_sys.add_field(name='Community',
                                                          value=guild.name,
                                                          inline=False)
                                    expired_sys.add_field(name="Expired Role",
                                                          value=role.name)
                                    expired_sys.add_field(name="User details",
                                                          value=f'Role ID: {mem_role_id}\n'
                                                                f'Community ID: {mem_role_community_id}\n'
                                                                f'Member ID: {mem_id}')
                                    merch_channel = bot.get_channel(id=int(channel_sys))
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
                    merchant_manager.bulk_user_clear(community_id=mem_role_community_id, role_id=mem_role_id)
                    merchant_manager.remove_all_monetized_roles(guild_id=mem_role_community_id)

        else:
            print(Fore.GREEN + 'There are no overdue members in the system going to sleep!')
            print('===========================================================')

    async def send_marketing_messages(self):
        stats = self.backoffice.stats_manager.get_all_stats()
        """
                data = {"xlm": {"offChain": off_chain_xlm,
                                "onChain": on_chain_xlm}}"""
        off_chain_xlm = stats["xlm"]["offChain"]
        total_tx = off_chain_xlm["totalTx"]
        total_moved = off_chain_xlm["totalMoved"]

        on_chain_xlm = stats["xlm"]["onChain"]
        deposits = on_chain_xlm["depositCount"]
        withdrawals = on_chain_xlm["withdrawalCount"]
        deposit_amount = on_chain_xlm["depositAmount"]
        withdrawal_amount = on_chain_xlm["withdrawalAmount"]

        stats_chn = self.bot.get_channel(id=self.backoffice.auto_messaging_channels["stats"])
        total_wallets = self.backoffice.stats_manager.count_total_registered_wallets()

        stats = Embed(title="Crypto Link Stats",
                      description='Snapshot of the system ',
                      color=Color.green())
        stats.add_field(name='Live on:',
                        value=f'{len(self.bot.guilds)} servers',
                        inline=False)
        stats.add_field(name='Σ Registered Wallets',
                        value=f'{total_wallets}',
                        inline=False)
        stats.add_field(name='Σ Transactions Level 1',
                        value=f'{total_moved}',
                        inline=False)
        stats.add_field(name='Σ XLM Moved',
                        value=f'{total_tx}',
                        inline=False)
        stats.add_field(name='Σ Deposits',
                        value=f'{deposits}',
                        inline=False)
        stats.add_field(name='Σ XLM Deposits',
                        value=f'{deposit_amount} XLM',
                        inline=False)
        stats.add_field(name='Withdrawals',
                        value=f'{withdrawals}',
                        inline=False)
        stats.add_field(name='Σ XLM Withdrawals ',
                        value=f'{withdrawal_amount} XLM',
                        inline=False)
        await stats_chn.send(embed=stats)


def start_scheduler(timed_updater):
    scheduler = AsyncIOScheduler()
    print(Fore.LIGHTBLUE_EX + 'Started Chron Monitors')

    scheduler.add_job(timed_updater.check_stellar_hot_wallet,
                      CronTrigger(second='00'), misfire_grace_time=10, max_instances=20)
    scheduler.add_job(timed_updater.check_expired_roles, CronTrigger(
        second='00'), misfire_grace_time=10, max_instances=20)

    scheduler.add_job(timed_updater.send_marketing_messages, CronTrigger(
        hour='00'), misfire_grace_time=10, max_instances=20)

    scheduler.start()
    print(Fore.LIGHTBLUE_EX + 'Started Chron Monitors : DONE')
    return scheduler
