# -*- coding: utf-8 -*-

import time
from datetime import datetime
import tweepy
from re import search
from stellar_sdk import Server
from datetime import datetime, timezone

import nextcord
from nextcord import Embed, Color
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from colorama import Fore, init

from cogs.utils.systemMessaages import CustomMessages
from utils.tools import Helpers

init(autoreset=True)
custom_messages = CustomMessages()
helper = Helpers()
channels = helper.read_json_file(file_name='autoMessagingChannels.json')

MERCHANT_PREFIX = "MER"

def get_time():
    """
    Get local time on the computer
    """
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time


class PeriodicTasks:
    def __init__(self, backoffice, bot, main_net: bool):
        self.backoffice = backoffice
        self.twitter_cred = self.backoffice.twitter_details
        self.notification_channels = self.backoffice.auto_messaging_channels["depositNotifications"]
        self.bot = bot
        self.main_net = main_net
        self.twitter_acc = self.backoffice.twitter_details
        auth = tweepy.OAuthHandler(self.twitter_cred["apiKey"], self.twitter_cred["apiSecret"])
        auth.set_access_token(self.twitter_cred["accessToken"], self.twitter_cred["accessSecret"])
        self.twitter_messages = tweepy.API(auth)

    async def _assign_role(self, guild: nextcord.Guild, user_id: int, role_id:int):
        """
        Function to give user the role automatically"""
        role = guild.get_role(role_id)
        if role is None:
            try:
                roles = await guild.fetch_roles()
                role = next((r for r in roles if r.id == role_id), None)
            except Exception:
                role = None

        if role is None:
            print(f'Role with {role_id} not found in {guild.name}')
            return
        
        if role.managed:
            print("❌ Target role is managed (integration) and cannot be assigned.")
            return

        me = guild.me

        if me is None:
            print("❌ Could not resolve bot member in guild.")
            return

        if not me.guild_permissions.manage_roles:
            print( "❌ Missing 'Manage Roles' permission.")
            return

        if me.top_role <= role:
            print("❌ Bot's top role is not above the target role.")
            return

        # member 
        member = guild.get_member(user_id)
        if member is None:
            try:
                member = await guild.fetch_member(user_id)
            except nextcord.NotFound:
                print("❌ User is not in this server.")
            except Exception as e:
                print(f"❌ Could not fetch member: {e}")
        
        if me.top_role <= member.top_role:
            print("❌ Bot's top role is not above the member's top role.")
            return 

        if role in member.roles:
            print("ℹ️ Member already has the role.")
            return

        try:
            await member.add_roles(role, reason="Automated assignment after verified deposit")
            print(f"✅ Assigned '{role.name}' to {member.display_name}.")
            return
        
        except nextcord.Forbidden:
            print("❌ Forbidden by Discord (permission/hierarchy).")
            return
        
        except nextcord.HTTPException as e:
            print(f"❌ Discord API error: {e}")
            return
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return 


    async def global_bot_stats_update(self, tx):
        bot_stats = {
            "depositCount": 1,
            "depositAmount": float(round(int(tx['asset_type']["amount"]) / (10 ** 7)))
        }
        await self.backoffice.stats_manager.update_cl_on_chain_stats(ticker=tx['asset_type']['code'].lower(),
                                                                     stat_details=bot_stats)

    def filter_transaction(self, new_transactions: list):
        # Building list of deposits if memo included
        tx_with_memo_special = [tx for tx in new_transactions if
                                'memo' in tx.keys() and helper.check_for_special_char(tx["memo"])]
        tx_with_memo = [tx for tx in new_transactions if 'memo' in tx.keys() and not helper.check_for_special_char(
            tx["memo"])]  # GET Transactions who have memo
        tx_with_no_memo = [tx for tx in new_transactions if tx not in tx_with_memo]  # GET transactions without memo
        tx_with_registered_memo = [tx for tx in tx_with_memo if
                                   self.backoffice.stellar_manager.check_if_stellar_memo_exists(
                                       tx_memo=tx['memo'])]  # GET tx with registered memo
        tx_with_not_registered_memo = [tx for tx in tx_with_memo if
                                       tx not in tx_with_registered_memo]  # GET tx with not registered memo
        
        tx_with_merchant_memo = [
            tx for tx in tx_with_not_registered_memo
            if isinstance(tx.get("memo"), str) and tx["memo"].startswith(MERCHANT_PREFIX)
        ]

        tx_with_not_registered_non_merchant = [
            tx for tx in tx_with_not_registered_memo
            if tx not in tx_with_merchant_memo
        ]

        return (
            tx_with_registered_memo,
            tx_with_not_registered_non_merchant,
            tx_with_no_memo,
            tx_with_memo_special,
            tx_with_merchant_memo,
        )

    async def process_tx_with_no_memo(self, channel, no_memo_transaction):

        for tx in no_memo_transaction:
            if not self.bot.backoffice.stellar_manager.check_if_deposit_hash_processed_unprocessed_deposits(
                    tx_hash=tx['hash']):
                if self.bot.backoffice.stellar_manager.stellar_deposit_history(deposit_type=2, tx_data=tx):
                    await self.global_bot_stats_update(tx=tx)
                    await custom_messages.send_unidentified_deposit_msg(channel=channel, tx_details=tx)
                else:
                    print(Fore.RED + f'There has been an issue while processing tx with no memo \n'
                                     f'HASH{tx["hash"]}')
            else:
                print(Fore.YELLOW + 'Unknown processed already')

    async def process_tx_with_memo(self, channel, memo_transactions):
        for tx in memo_transactions:
            # check if processed if not process them
            if not self.bot.backoffice.stellar_manager.check_if_deposit_hash_processed_succ_deposits(tx['hash']):
                if self.bot.backoffice.stellar_manager.stellar_deposit_history(deposit_type=1, tx_data=tx):
                    # Update balance based on incoming asset
                    if not helper.check_for_special_char(tx["memo"]):
                        if self.bot.backoffice.wallet_manager.update_coin_balance_by_memo(memo=tx['memo'],
                                                                                          coin=tx['asset_type'][
                                                                                              "code"].lower(),
                                                                                          amount=int(tx['asset_type'][
                                                                                                         "amount"])):
                            # If balance updated successfully send the message to user of processed deposit
                            user_id = self.bot.backoffice.wallet_manager.get_discord_id_from_memo(
                                memo=tx['memo'])  # Return usr int number
                            dest = await self.bot.fetch_user(int(user_id))

                            on_chain_stats = {
                                f"{tx['asset_type']['code'].lower()}.depositsCount": 1,
                                f"{tx['asset_type']['code'].lower()}.totalDeposited": round(
                                    int(tx['asset_type']["amount"]) / 10000000,
                                    7)}

                            await self.bot.backoffice.stats_manager.update_user_on_chain_stats(user_id=dest.id,
                                                                                               stats_data=on_chain_stats)

                            await self.global_bot_stats_update(tx=tx)

                            await custom_messages.deposit_notification_message(recipient=dest, tx_details=tx)

                            # Channel system message on deposit
                            await custom_messages.sys_deposit_notifications(channel=channel,
                                                                            user=dest, tx_details=tx)

                            # # Explorer messages
                            # load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                            #                  self.bot.backoffice.guild_profiles.get_all_explorer_applied_channels()]
                            #
                            # explorer_msg = f':inbox_tray: Someone deposited {round(tx["asset_type"]["amount"] / (10 ** 7), 7)} ' \
                            #                f'{tx["asset_type"]["code"].upper()} to {self.bot.user}'
                            #
                            # await custom_messages.explorer_messages(applied_channels=load_channels,
                            #                                         message=explorer_msg)

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
        for tx in no_registered_memo:
            if not self.bot.backoffice.stellar_manager.check_if_deposit_hash_processed_unprocessed_deposits(
                    tx_hash=tx['hash']):
                if not helper.check_for_special_char(tx["memo"]):
                    if self.bot.backoffice.stellar_manager.stellar_deposit_history(deposit_type=2, tx_data=tx):
                        await self.global_bot_stats_update(tx=tx)
                        await custom_messages.send_unidentified_deposit_msg(channel=channel, tx_details=tx)
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
    
    async def process_merchant_order_memo(self, channel, new_transactions: list[dict]):
        for tx in new_transactions:
            tx_hash = tx.get("hash")
            memo = tx.get("memo")

            if not tx_hash or not memo:
                continue
            
            if not isinstance(memo, str) or not memo.startswith("MER"):
                continue
            
            # Check if it is not  already in the history
            if self.bot.backoffice.stellar_manager.check_if_deposit_hash_processed_merchant_payments(tx_hash):
                continue
            
            # get the order detail of the user
            order_details = self.bot.backoffice.merchant_manager.get_merchant_order_by_memo(payment_reference=memo)
            
            # what to do if the order can not be found
            if not order_details:
                # TODO resove this function before libe Optional: store as unidentified or just log
                await custom_messages.send_unidentified_deposit_msg(channel=channel, tx_details=tx)
                continue
        
        
             # If already processed order, mark tx as processed and skip
            if int(order_details.get("status", 0)) == 1:
                self.bot.backoffice.stellar_manager.store_processed_merchant_tx_hash(tx_hash)
                continue

            user_id = order_details["userId"]
            community_id = order_details["communityId"]
            role_id = order_details["roleId"]
            
            expected_stroops = int(order_details.get("value", 0))  # if no value its 0 to avoid crash
            expected_currency = str(order_details.get("currency", "xlm")).lower()
                
            # validating the transaction
            try:
                tx_code = str(tx["asset_type"]["code"]).lower()
                tx_amount_stroops = int(tx["asset_type"]["amount"])
            except Exception:
                await custom_messages.send_unidentified_deposit_msg(channel=channel, tx_details=tx)
                continue

            if tx_code != expected_currency:
                await custom_messages.send_unidentified_deposit_msg(channel=channel, tx_details=tx)
                continue
            
            if tx_amount_stroops != expected_stroops:
                # You may want a tolerance or manual review bucket, but don't grant role
                await custom_messages.send_unidentified_deposit_msg(channel=channel, tx_details=tx)
                continue
            
            guild = self.bot.get_guild(community_id)
            if not guild:
                print(f"Guild {community_id} not found in cache")
                continue
            
            assigned = await self._assign_role(guild=guild, user_id=user_id, role_id=role_id)
            if not assigned:
                # don’t mark processed if role assignment failed
                continue
            
            # ---- Mark tx + order processed ----
            now = datetime.now(timezone.utc)

            #TODO this function need to be updated. Where tx to store 
            self.bot.backoffice.stellar_manager.store_processed_merchant_tx_hash(tx_hash)


            self.bot.backoffice.merchant_manager.mark_order_processed(
                payment_reference=memo,
                processed_time=now,
                tx_hash=tx_hash,
            )
        
            # Optional: send confirmation
            try:
                user = await self.bot.fetch_user(user_id)  # The role was granted
                
                #TODO send user a message that he/she has been granted a role with details
                await custom_messages.deposit_notification_message(recipient=user, tx_details=tx)
                
            except Exception:
                pass
           
            try:
                # TODO send the guild owner that someone has purchased the role 
                pass
            except Exception:
                
                
            # TODO send to explorer that someon ehas purchased a role
            pass

        
    async def check_stellar_hot_wallet(self):
        """
        Functions initiates the check for stellar incoming deposits and processes them
        """

        print(Fore.GREEN + f"{get_time()} --> CHECKING STELLAR CHAIN FOR DEPOSITS")
        if not self.main_net:
            file_name = 'stellarPagTest.json'
            pag = helper.read_json_file(file_name)
        else:
            file_name = 'stellarPag.json'
            pag = helper.read_json_file(file_name)

        new_transactions = self.backoffice.stellar_wallet.get_incoming_transactions(pag=int(pag['pag']))

        if new_transactions and isinstance(new_transactions, list):
            
            tx_with_registered_memo, tx_with_not_registered_non_merchant, tx_with_no_memo, tx_with_memo_special, tx_with_merchant_memo = \
                self.filter_transaction(new_transactions)

            if tx_with_registered_memo:
                channel = self.bot.get_channel(int(self.notification_channels['memoRegistered']))
                await self.process_tx_with_memo(channel=channel, memo_transactions=tx_with_registered_memo)

            if tx_with_merchant_memo:
                channel = self.bot.get_channel(int(self.notification_channels['memoNotRegistered']))
                await self.process_merchant_order_memo(channel=channel, new_transactions=tx_with_merchant_memo)

            if tx_with_not_registered_non_merchant:
                channel = self.bot.get_channel(int(self.notification_channels['memoNotRegistered']))
                await self.process_tx_with_not_registered_memo(channel=channel, no_registered_memo=tx_with_not_registered_non_merchant)

            if tx_with_no_memo:
                channel = self.bot.get_channel(int(self.notification_channels['memoNone']))
                await self.process_tx_with_no_memo(channel=channel, no_memo_transaction=tx_with_no_memo)

            if tx_with_memo_special:
                channel = self.bot.get_channel(int(self.notification_channels['memoSpecialChar']))
                await self.process_tx_with_special_chart(channel=channel)


            last_checked_pag = new_transactions[-1]["paging_token"]

            if helper.update_json_file(file_name=file_name, key='pag', value=int(last_checked_pag)):
                print(Fore.GREEN + f'Peg updated successfully from {pag} --> {last_checked_pag}')
            else:
                print(Fore.RED + 'There was an issue with updating pag')

            print(Fore.GREEN + '==============DONE=================\n'
                               '==========GOING TO SLEEP FOR 1 MINUTE=====')
        else:
            print(Fore.CYAN + 'No new incoming transactions in range...Going to sleep for 60 seconds')
            print('==============================================')

    async def send_marketing_messages(self):
        print(Fore.GREEN + f"{get_time()} --> Sending report to Discord ")
        stats = self.backoffice.stats_manager.get_all_stats()
        off_chain_xlm = stats["xlm"]["offChain"]
        total_tx = off_chain_xlm["totalTx"]
        total_moved = round(off_chain_xlm["totalMoved"], 7)

        on_chain_xlm = stats["xlm"]["onChain"]
        deposits = on_chain_xlm["depositCount"]
        withdrawals = on_chain_xlm["withdrawalCount"]
        deposit_amount = on_chain_xlm["depositAmount"]
        withdrawal_amount = on_chain_xlm["withdrawnAmount"]

        stats_chn = self.bot.get_channel(self.backoffice.auto_messaging_channels["stats"])
        total_wallets = await self.backoffice.stats_manager.count_total_registered_wallets()

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
                        value=f'{total_tx}',
                        inline=False)
        stats.add_field(name='Σ XLM Moved',
                        value=f'{total_moved}',
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
        return

    async def twitter_message(self):
        print(Fore.GREEN + f"{get_time()} --> Sending report to Twitter ")
        stats = self.backoffice.stats_manager.get_all_stats()
        off_chain_xlm = stats["xlm"]["offChain"]
        total_tx = off_chain_xlm["totalTx"]
        total_moved = round(off_chain_xlm["totalMoved"], 7)

        total_wallets = await self.backoffice.stats_manager.count_total_registered_wallets()
        print(Fore.GREEN + f"{get_time()} --> Sending Twitter")
        # Twitter message
        rocket = '\U0001F680'
        bridges = '\U0001F309'
        sent_transactions = '\U0001F4E8'
        total_xlm_moved = '\U0001F4B8'
        total_reach = len(self.bot.users)
        utc_now = datetime.utcnow()
        reach_performance = round((total_wallets / total_reach) * 100, 2)
        try:
            self.twitter_messages.update_status(
                f"{rocket}Crypto Link Status on {utc_now.year}.{utc_now.month}.{utc_now.day}{rocket}\n"
                f"Serving {len(self.bot.guilds)} #DiscordServer with "
                f"potential reach to {total_reach} #Discord users. Current coverage is {reach_performance}% "
                f"with {total_wallets} {bridges} built to #StellarFamily."
                f"{sent_transactions} {total_tx} payments have been processed and moved {total_xlm_moved}"
                f" {total_moved} $XLM in total! #Stellar #StellarGlobal #XLM")
        except Exception as e:
            print(Fore.RED + f"{e} ")
        return

    async def send_builder_ranks(self):
        stats = self.backoffice.stats_manager.get_top_builders(limit=5)
        bridges = '\U0001F309'
        string = ''
        rank = 1
        for user in stats:
            try:
                username = user['userName']
                bridge_counts = user["bridges"]
                line = f'{rank}.' + ' ' + f'{username}' + ' ' + f'\n{bridge_counts}' + ' \n'
                string += line
                rank += 1
            except KeyError:
                pass

        self.twitter_messages.update_status(f"{bridges} Bridge Builders Hall of Fame {bridges}\n" + f'{string}')

        stats_chn = self.bot.get_channel(self.backoffice.auto_messaging_channels["stats"])
        stats = Embed(title="Builders Hall of Fame",
                      description='Top 5 bridge builders of all time',
                      color=Color.green())
        stats.add_field(name=':tools: Ranks :tools:  ',
                        value=f'{string}',
                        inline=False)
        await stats_chn.send(embed=stats)
        return


def start_scheduler(timed_updater):
    scheduler = AsyncIOScheduler()
    print(Fore.LIGHTBLUE_EX + 'Started Chron Monitors')
    # scheduler.add_job(timed_updater.check_stellar_hot_wallet,
    #                   CronTrigger(second='00'),
    #                   misfire_grace_time=10,
    #                   max_instances=20)
    scheduler.add_job(timed_updater.check_stellar_hot_wallet,
                      CronTrigger(minute='02,07, 12, 17,22,27,32,37,42,47,52,57'),
                      misfire_grace_time=10,
                      max_instances=20)
    scheduler.add_job(timed_updater.send_marketing_messages, CronTrigger(
        hour='17'), misfire_grace_time=10, max_instances=20)

    scheduler.add_job(timed_updater.send_builder_ranks,
                      CronTrigger(day_of_week='sun', hour='17', minute='58', second='15'),
                      misfire_grace_time=7, max_instances=20)

    scheduler.add_job(timed_updater.twitter_message,
                      CronTrigger(day='30'),
                      misfire_grace_time=7, max_instances=20)

    scheduler.start()
    print(Fore.LIGHTBLUE_EX + 'Started Chron Monitors : DONE')
    return scheduler
