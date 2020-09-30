"""
Main bot file to bring it online... Run it
"""

import time
from datetime import datetime

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from colorama import Fore, init
from discord.ext import commands

from backOffice.backendCheck import BotStructureCheck
from backOffice.userWalletManager import UserWalletManager
from backOffice.guildServicesManager import GuildProfileManager
from backOffice.merchatManager import MerchantManager
from backOffice.statsManager import StatsManager
from backOffice.stellarActivityManager import StellarManager
from backOffice.stellarOnChainHandler import StellarWallet
from cogs.utils.systemMessaages import CustomMessages
from cogs.utils.monetaryConversions import convert_to_usd
from utils.tools import Helpers

init(autoreset=True)
scheduler = AsyncIOScheduler()
stellar_wallet = StellarWallet()
stellar_manager = StellarManager()
merchant_manager = MerchantManager()
stats_manager = StatsManager()
wallet_manager = UserWalletManager()
guild_profiles = GuildProfileManager()
custom_messages = CustomMessages()
helper = Helpers()
notification_channels = helper.read_json_file(file_name='autoMessagingChannels.json')
d = helper.read_json_file(file_name='botSetup.json')
channels = helper.read_json_file(file_name='autoMessagingChannels.json')
bot = commands.Bot(command_prefix=commands.when_mentioned_or(d['command']))  # Test commands
bot.remove_command('help')  # removing the old help command

CONST_STELLAR_EMOJI = "<:stelaremoji:684676687425961994>"
extensions = ['cogs.generalCogs', 'cogs.transactionCogs', 'cogs.userAccountCogs',
              'cogs.systemMngCogs', 'cogs.withdrawalCogs',
              'cogs.merchantCogs', 'cogs.consumerMerchant', 'cogs.autoMessagesCogs', 'cogs.merchantLicensingCogs',
              'cogs.feeManagementCogs', 'cogs.guildOwnersCmds']


def get_time():
    """
    Get local time on the computer
    """
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time


def filter_transaction(new_transactions: list):
    """
    Filtering transactions
    """

    # Building list of deposits if memo included
    tx_with_memo = [tx for tx in new_transactions if 'memo' in tx.keys()]  # GET Transactions who have memo

    tx_with_no_memo = [tx for tx in new_transactions if tx not in tx_with_memo]  # GET transactions without memo

    tx_with_registered_memo = [tx for tx in tx_with_memo if stellar_manager.check_if_stellar_memo_exists(
        tx_memo=tx['memo'])]  # GET tx with registered memo

    tx_with_not_registered_memo = [tx for tx in tx_with_memo if
                                   tx not in tx_with_registered_memo]  # GET tx with not registered memo

    return tx_with_registered_memo, tx_with_not_registered_memo, tx_with_no_memo


async def process_tx_with_no_memo(channel, no_memo_transaction):
    for tx in no_memo_transaction:
        if not stellar_manager.check_if_deposit_hash_processed_unprocessed_deposits(tx_hash=tx['hash']):
            if stellar_manager.stellar_deposit_history(deposit_type=2, tx_data=tx):
                await custom_messages.send_unidentified_deposit_msg(channel=channel, deposit_details=tx)
                # TODO integrate bot global stats
            else:
                print(Fore.RED + f'There has been an issue while processing tx with no memo \n'
                                 f'HASH{tx["hash"]}')
        else:
            print(Fore.YELLOW + 'Unknown processed already')


async def process_tx_with_memo(msg_channel, memo_transactions):
    for tx in memo_transactions:
        # check if processed if not process them
        if not stellar_manager.check_if_deposit_hash_processed_succ_deposits(tx['hash']):
            if stellar_manager.stellar_deposit_history(deposit_type=1, tx_data=tx):
                # Update balance based on incoming asset
                if wallet_manager.update_coin_balance_by_memo(memo=tx['memo'], coin=tx['asset_type']["code"],
                                                              amount=int(tx['asset_type']["amount"])):

                    # If balance updated successfully send the message to user of processed deposit
                    user_id = wallet_manager.get_discord_id_from_memo(memo=tx['memo'])  # Return usr int number
                    dest = await bot.fetch_user(user_id=int(user_id))

                    await custom_messages.deposit_notification_message(recipient=dest, tx_details=tx)

                    # Channel system message on deposit
                    await custom_messages.sys_deposit_notifications(channel=msg_channel,
                                                                    user=dest, tx_details=tx)

                    # Explorer messages
                    load_channels = [bot.get_channel(id=int(chn)) for chn in
                                     guild_profiles.get_all_explorer_applied_channels()]

                    explorer_msg = f':inbox_tray: Someone deposited {tx["asset_type"]["amount"]} ' \
                                   f'{tx["asset_type"]["code"].upper()} to {bot.user}'

                    await custom_messages.explorer_messages(applied_channels=load_channels,
                                                            message=explorer_msg,
                                                            on_chain=True, tx_type='deposit')

                    on_chain_stats = {
                        f"{tx['asset_type']['code']}.depositsCount": 1,
                        f"{tx['asset_type']['code']}.totalDeposited": round(int(tx['asset_type']["amount"]) / 10000000,
                                                                            7)}

                    await stats_manager.update_user_on_chain_stats(user_id=dest.id, stats_data=on_chain_stats)

                    bot_stats = {
                        "depositCount": 1,
                        "depositAmount": float(round(int(tx['asset_type']["amount"]) / 10000000))
                    }
                    await stats_manager.update_cl_on_chain_stats(ticker=tx['asset_type']['code'].lower(),
                                                                 stat_details=bot_stats)

                else:
                    print(Fore.RED + f'TX Processing error: \n'
                                     f'{tx}')
            else:
                print(Fore.RED + 'Could not store to history')
        else:
            print(Fore.LIGHTCYAN_EX + 'No new legit tx')


async def process_tx_with_not_registered_memo(channel, no_registered_memo):
    for tx in no_registered_memo:
        if not stellar_manager.check_if_deposit_hash_processed_unprocessed_deposits(tx_hash=tx['hash']):
            if stellar_manager.stellar_deposit_history(deposit_type=2, tx_data=tx):
                await custom_messages.send_unidentified_deposit_msg(channel=channel, deposit_details=tx)
                print(Fore.GREEN + 'Processed successfully')
                # TODO integrate stats for deposit processing
            else:
                print(Fore.RED + f'There has been an issue while processing tx with no memo \n'
                                 f'HASH{tx["hash"]}')
        else:
            print(Fore.YELLOW + 'Unknown processed already')


async def check_stellar_hot_wallet():
    """
    Functions initiates the check for stellar incoming deposits and processes them
    """
    print(Fore.GREEN + f"{get_time()} --> CHECKING STELLAR CHAIN FOR DEPOSITS")
    pag = helper.read_json_file('stellarPag.json')
    new_transactions = stellar_wallet.get_incoming_transactions(pag=int(pag['pag']))
    channel_id = notification_channels["stellar"]  # Sys channel where details are sent

    if new_transactions:
        # Filter transactions
        tx_with_registered_memo, tx_with_not_registered_memo, tx_with_no_memo = filter_transaction(new_transactions)
        channel = bot.get_channel(id=int(channel_id))
        if tx_with_registered_memo:
            await process_tx_with_memo(msg_channel=channel, memo_transactions=tx_with_registered_memo)
        if tx_with_not_registered_memo:
            await process_tx_with_not_registered_memo(channel=channel, no_registered_memo=tx_with_not_registered_memo)
        if tx_with_no_memo:
            await process_tx_with_no_memo(channel=channel, no_memo_transaction=tx_with_no_memo)

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


async def check_expired_roles():
    """
    Function checks for expired users on community nad removes them if necessary
    """
    print(Fore.GREEN + f"{get_time()} --> CHECKING FOR USERS WITH EXPIRED ROLES ")
    now = datetime.utcnow().timestamp()  # Gets current time of the system in unix format
    overdue_members = merchant_manager.get_over_due_users(timestamp=int(now))  # Gets all overdue members from database
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
                                expired_sys = discord.Embed(title='__Expired user could not be removed from system__',
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


async def check_merchant_licences():
    """
    Script which checks merchant license situation
    """
    print(Fore.GREEN + f"{get_time()} --> CHECKING FOR COMMUNITIES WITH EXPIRED MERCHANT LICENSE")

    now = datetime.utcnow().timestamp()  # Gets current time of the system in unix format

    overdue_communities = merchant_manager.get_over_due_communities(timestamp=int(now))
    if overdue_communities:
        for community in overdue_communities:
            community_id = community['communityId']
            community_name = community['communityName']
            owner_id = community['ownerId']
            start = community['start']
            end = community['end']
            start_date = datetime.fromtimestamp(int(start))
            end_date = datetime.fromtimestamp(int(end))

            if merchant_manager.remove_over_due_community(discord_id=int(community_id)):

                # Send notification to owner ,
                expired = discord.Embed(title='__Merchant License Expiration Notification!__',
                                        colour=discord.Colour.dark_red(),
                                        description='You have received this notification because '
                                                    '31 day Merchant License for Crypto Link has expired. Thank you '
                                                    ' for using Crypto Link Merchant.')
                expired.set_thumbnail(url=bot.user.avatar_url)
                expired.add_field(name='Community Name of purchase',
                                  value=f'{community_name} (ID:{community_id})')
                expired.add_field(name='Start of the license',
                                  value=f'{start_date}',
                                  inline=False)
                expired.add_field(name='End of the license',
                                  value=f'{end_date}',
                                  inline=False)
                dest = await bot.fetch_user(user_id=int(owner_id))
                await dest.send(embed=expired)

                channel_sys = channels["merchant"]
                # send notification to merchant channel of LPI community
                expired_sys = discord.Embed(title='Merchant license expired and removed successfully!',
                                            colour=discord.Color.red())
                expired_sys.set_thumbnail(url=bot.user.avatar_url)
                expired_sys.add_field(name='Community Name of purchase',
                                      value=f'{community_name} (ID:{community_id})')
                expired_sys.add_field(name='Start of the license',
                                      value=f'{start_date}',
                                      inline=False)
                expired_sys.add_field(name='End of the license',
                                      value=f'{end_date}',
                                      inline=False)

                merch_channel = bot.get_channel(id=int(channel_sys))
                await merch_channel.send(embed=expired_sys)
            else:
                sys_error = discord.Embed(title='__Merchant License System error__!',
                                          description='This error has been triggered because merchant community license'
                                                      ' could not be removed from database. Community details '
                                                      'are presented below',
                                          colour=discord.Color.red())
                sys_error.add_field(name='Community details',
                                    value=f'{community_name} (ID: {community_id})',
                                    inline=False)
                sys_error.add_field(name='Owner ID',
                                    value=f'{owner_id}',
                                    inline=False)
                sys_error.add_field(name='Started @',
                                    value=f'{start_date} (UNIX {start})',
                                    inline=False)
                sys_error.add_field(name='Finished @',
                                    value=f'{end_date} (UNIX {end})',
                                    inline=False)

                channel_id_details = notification_channels['merchant']
                channel_to_send = bot.get_channel(id=int(channel_id_details))
                await channel_to_send.send(embed=sys_error)

    else:
        print(Fore.CYAN + 'No communities with overdue license\n'
                          ' ===================================')


def start_scheduler():
    print(Fore.LIGHTBLUE_EX + 'Started Chron Monitors')

    scheduler.add_job(check_stellar_hot_wallet,
                      CronTrigger(second='00'), misfire_grace_time=10, max_instances=20)
    scheduler.add_job(check_expired_roles, CronTrigger(
        second='00'), misfire_grace_time=10, max_instances=20)
    scheduler.add_job(check_merchant_licences,
                      CronTrigger(minute='00', second='10'), misfire_grace_time=10, max_instances=20)
    scheduler.start()


@bot.event
async def on_ready():
    """
    Print out to console once bot logs in
    :return:
    """

    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Online and ready'))
    print(Fore.GREEN + 'Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print('================================')


if __name__ == '__main__':
    backend_check = BotStructureCheck()
    backend_check.check_collections()
    backend_check.checking_stats_documents()
    backend_check.checking_bot_wallets()

    # Check file system
    backend_check = Fore.GREEN + '+++++++++++++++++++++++++++++++++++++++\n' \
                                 '          Checking backend....        \n'

    print(backend_check)

    notification_str = Fore.GREEN + '+++++++++++++++++++++++++++++++++++++++\n' \
                                    '           LOADING COGS....        \n'
    for extension in extensions:
        try:
            bot.load_extension(extension)
            notification_str += f'| {extension} :smile: \n'
        except Exception as error:
            notification_str += f'| {extension} --> {error}\n'
            raise

    notification_str += '+++++++++++++++++++++++++++++++++++++++'
    print(notification_str)
    start_scheduler()
    # Discord Token
    bot.run(d['token'], reconnect=True)
