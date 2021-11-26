import discord.ext.commands
from discord.ext import commands
from asyncio import TimeoutError, sleep

from discord import Member as DiscordMember
from discord import Embed, Colour, Role
from discord.ext.commands import Greedy
from re import search
from datetime import datetime
from utils.customCogChecks import is_public, has_wallet
from cogs.utils.systemMessaages import CustomMessages
from asyncio import gather

custom_messages = CustomMessages()
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_TX_ERROR_TITLE = ":exclamation: __Special Payment Error__ :exclamation: "


def process_message(message):
    """
    Filter message so it is not too long for transaction report
    """
    if message:
        if len(message) > 50:
            message = message[:98] + '...'
    else:
        message = 'None'

    return message


def check(author):
    def inner_check(message):
        if message.author == author:
            return True
        else:
            return False

    return inner_check


class SpecialPaymentCommands(commands.Cog):
    """
    Class handling off-chain discord transactions
    """

    def __init__(self, bot):
        self.bot = bot
        self.session_message = {}

    async def stats_updating(self, ctx, asset_code, total_amount, single_payment, payments_count, tx_type,
                             recipient_list):
        """
        Type of special transactions
        Airdrop = Airdrop, MultiTx = Multi
        """

        if tx_type in ["multi", "loyalty"]:
            processed = {"globalBot": {"totalTx": int(payments_count),
                                       'totalMoved': total_amount,
                                       f"total{tx_type.capitalize()}Count": 1,
                                       f"total{tx_type.capitalize()}Moved": total_amount},
                         "senderStats": {f"{asset_code}.{tx_type}TxCount": 1,
                                         f"{asset_code}.publicSent": total_amount,
                                         f"{asset_code}.publicTxSendCount": payments_count,
                                         f"{asset_code}.{tx_type}Sent": total_amount,
                                         },
                         "recipientStats": {f"{asset_code.lower()}.publicTxReceivedCount": 1,
                                            f"{asset_code.lower()}.publicReceived": single_payment,
                                            },
                         "guildStats": {
                             f'{asset_code}.{tx_type.lower()}TxCount': 1,
                             f'{asset_code}.publicCount': payments_count,
                             f"{asset_code}.txCount": 1,
                             f"{asset_code}.volume": total_amount
                         }
                         }

        #
        await self.bot.backoffice.stats_manager.update_cl_off_chain_stats(ticker=asset_code.lower(),
                                                                          ticker_stats=processed["globalBot"])
        #
        await self.bot.backoffice.stats_manager.update_usr_tx_stats(user_id=ctx.message.author.id,
                                                                    tx_stats_data=processed['senderStats'])

        for recipient in recipient_list:
            await self.bot.backoffice.stats_manager.update_usr_tx_stats(user_id=recipient.id,
                                                                        tx_stats_data=processed["recipientStats"])

        await self.bot.backoffice.stats_manager.update_guild_stats(guild_id=ctx.message.guild.id,
                                                                   guild_stats_data=processed['guildStats'])

    async def recipient_report(self, ctx, recipient, tx_time: str, total_amount: float, asset_code: str, subject: str,
                               tx_type, tx_emoji):
        special_embed = Embed(title=f':inbox_tray: Incoming Payment',
                              description=f'You have received payment, check for details below!',
                              colour=Colour.green())
        special_embed.add_field(name=':map: Special payment type',
                                value=f'{tx_emoji} ***{tx_type}***',
                                inline=False)
        special_embed.add_field(name=':map: Location details',
                                value=f'Server: {ctx.message.guild}\n'
                                      f'Channel: {ctx.message.channel.mention}\n'
                                      f'[Link to channel](http://discord.com/channels/{ctx.guild.id}/{ctx.channel.id})')
        special_embed.add_field(name=':calendar: Date and time of payment',
                                value=tx_time,
                                inline=False)
        special_embed.add_field(name=':cowboy: Sender',
                                value=f'{ctx.author} (ID: {ctx.author.id})',
                                inline=False)
        special_embed.add_field(name=':mega: Subject of payment',
                                value=f"```{subject}```",
                                inline=False)
        special_embed.add_field(name=':envelope: Payment Slip',
                                value=f'```Total received: {total_amount:,.7f} {asset_code}\n```',
                                inline=False)
        special_embed.set_footer(text='Dont forget to say thanks!.')
        try:
            await recipient.send(embed=special_embed)
        except Exception:
            pass

    async def sender_report(self, ctx, tx_type: str, tx_time: str, total_value: float, asset_code: str,
                            recipients_list: list, subject: str, tx_emoji):
        recipients = '\n'.join(f'{recipient}' for recipient in recipients_list)
        special_embed = Embed(title=f':outbox_tray: Special outgoing Payment',
                              description=f'You have executed special payment on {ctx.message.guild} '
                                          f'channel {ctx.message.channel}.',
                              colour=Colour.red())
        special_embed.add_field(name=':pager: payment type',
                                value=f'{tx_emoji}{tx_type}',
                                inline=True)
        special_embed.add_field(name=':calendar: Date and time of payment',
                                value=tx_time,
                                inline=True)
        special_embed.add_field(name=':mega: Subject of payment',
                                value=f"```{subject}```",
                                inline=False)
        special_embed.add_field(name=':envelope:  __**Payment Slip**__',
                                value=f'```Per user:{total_value / len(recipients_list):,.7f} {asset_code}\n'
                                      f'Total Count: {len(recipients_list)}\n'
                                      f'-----------------------------------------\n'
                                      f'Total sent: {total_value:,.7f} {asset_code}\n```',
                                inline=False)
        special_embed.add_field(name=':busts_in_silhouette: **__All recipients__**',
                                value=f'```{recipients}```',
                                inline=False)
        special_embed.set_footer(text='Thank you for using Crypto Link.')
        await ctx.author.send(embed=special_embed)

    async def bridges_notification(self, ctx, recipients_count):
        bridge_info = Embed(title=f':bridge_at_night: New Bridges Created :bridge_at_night: ',
                            description=f":construction_worker: You have successfully created new bridges between "
                                        f"***Discord users*** and ***Stellar***. ",
                            colour=Colour.green())
        bridge_info.add_field(name=f':new: Amount of created bridges',
                              value=f'{recipients_count}',
                              inline=False)
        bridge_info.add_field(name=f':information_source: Explanation :information_source: ',
                              value=f'Everytime you send someone payment and he/she are not registered in '
                                    f'Crypto Link system, a new wallet is created.'
                                    f'With every new wallet registered, bridge is established bringing another '
                                    f'user to the Stellar. \n'
                                    f' Keep on building!')
        await ctx.author.send(embed=bridge_info)

    def check_recipients_wallets(self, recipients: list):
        count_new = 0
        new_recipients = list()
        for rec in recipients:
            if not self.bot.backoffice.account_mng.check_user_existence(user_id=rec.id):
                if self.bot.backoffice.account_mng.register_user(discord_id=rec.id,
                                                                 discord_username=f'{rec}'):
                    # Notify on new wallet
                    new_recipients.append(rec)
                    count_new += 1
                else:
                    print("There has been an issue")
            else:
                print(f'{rec} already has a wallet')
        return count_new, new_recipients

    async def special_payment(self, ctx, recipients_list: list, amount_micro_recipient: int, asset_code: str,
                              total_amount_micro: int, tx_type: str, emoji: str,
                              channel_msg: str, uplink_message: str,
                              subject: str = None):
        """
        FUnction to handle special payments
        """
        tx_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Check wallets of recipients
        count_new, new_recipients = self.check_recipients_wallets(recipients=recipients_list)

        # Load registered channel for crypto link
        up_link_channels = [self.bot.get_channel(id=int(chn)) for chn in
                            self.bot.backoffice.guild_profiles.get_all_explorer_applied_channels()]

        if count_new > 0:
            # Updating registered user stats for guild
            await self.bot.backoffice.stats_manager.update_batch_registered_users(
                guild_id=ctx.message.guild.id, count=count_new)

            # Updating users stats for created bridges
            await self.bot.backoffice.stats_manager.create_bridges(
                user_id=ctx.message.author.id,
                count=count_new)

            # Notify sender on new bridges
            await self.bridges_notification(ctx, count_new)

            # TODO remove this from the system so it descreased API calls

            # Send messages on new account to uplink
            current_total = self.bot.backoffice.account_mng.count_registrations()
            explorer_msg = f':new: {count_new} user/s registered into ***{self.bot.user} System*** ' \
                           f' through special payments on {ctx.message.guild} (Σ {current_total})'

            for chn in up_link_channels:
                if chn is not None:
                    await chn.send(content=explorer_msg)

        # deducting total amount from sender
        if self.bot.backoffice.wallet_manager.update_coin_balance(coin=asset_code,
                                                                  user_id=ctx.message.author.id,
                                                                  amount=int(total_amount_micro),
                                                                  direction=2):
            batch_payments_lists = [
                self.bot.backoffice.wallet_manager.as_update_coin_balance(
                    coin=asset_code.lower(),
                    user_id=recipient.id,
                    amount=int(amount_micro_recipient),
                    direction=1) for recipient
                in recipients_list]
            await gather(*batch_payments_lists)

            # Send report to recipients
            subject = process_message(subject)

            await ctx.channel.send(content=channel_msg)

            # Report to sender
            await self.sender_report(ctx=ctx, tx_type=tx_type, tx_time=tx_time,
                                     total_value=total_amount_micro / (10 ** 7),
                                     asset_code=asset_code.upper(),
                                     recipients_list=recipients_list,
                                     subject=subject, tx_emoji=emoji)

            # report to recipients
            batch_reports = [
                self.recipient_report(ctx=ctx, recipient=recipient, tx_time=tx_time,
                                      total_amount=amount_micro_recipient / (10 ** 7),
                                      asset_code=asset_code.upper(), subject=subject,
                                      tx_type=tx_type, tx_emoji=emoji)
                for recipient in recipients_list]
            await gather(*batch_reports)

            # Update stats
            await self.stats_updating(ctx=ctx, asset_code=asset_code, total_amount=total_amount_micro / (10 ** 7),
                                      single_payment=amount_micro_recipient / (10 ** 7),
                                      payments_count=len(recipients_list), tx_type=tx_type,
                                      recipient_list=recipients_list)

            for chn in up_link_channels:
                if chn is not None:
                    await chn.send(content=uplink_message)
        else:
            await ctx.author.send(content='System could not deduct from sender')

    @commands.command()
    @commands.check(is_public)
    @commands.check(has_wallet)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def give(self, ctx, recipients: Greedy[DiscordMember], amount: float, asset_code, *, subject: str = None):
        asset_code = asset_code.lower()
        if amount > 0:
            if not search("[~!#$%^&*()_+{}:;\']", asset_code) and asset_code in [x["assetCode"] for x in
                                                                                 self.bot.backoffice.token_manager.get_all_tokens()]:
                amount_micro = amount * (10 ** 7)
                # Process recipients
                recipients_list = [recipient for recipient in recipients if
                                   recipient != ctx.author and not recipient.bot]
                if 0 < len(recipients_list) <= 5:
                    total_micro = amount_micro * len(recipients_list)
                    # Check balance
                    if total_micro <= self.bot.backoffice.wallet_manager.get_ticker_balance(asset_code=asset_code,
                                                                                            user_id=ctx.message.author.id):

                        message_content = f"{ctx.message.author.mention} are you sure that you would like to give " \
                                          f"{total_micro / (10 ** 7):,.7f} {asset_code.upper()} distributed equally amongst " \
                                          f"{len(recipients_list)} users?\n" \
                                          f"Answer with either ***yes*** or ***no*** ... Request will be cancelled in " \
                                          f"***10*** seconds if no response received."

                        verification = await ctx.channel.send(content=message_content)
                        try:
                            msg_usr = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=10)

                            if str(msg_usr.content.lower()) == 'yes':
                                # Channel Message for payment
                                recipients = ' '.join(rec.mention for rec in recipients_list)
                                channel_message = f":gift: {recipients}, user ***{ctx.message.author}*** " \
                                                  f" gave you a gift worth ***{amount_micro / (10 ** 7):,.7f} " \
                                                  f"{asset_code.upper()}***."

                                "Member on Crypto Link channel testing-grounds has given in total of 2.0000000 XLM to 2 users"

                                # Uplink messages for payment
                                uplink_message = f":gift: Gift has been given on " \
                                                 f"***{ctx.guild}***'s channel ***#{ctx.message.channel}***" \
                                                 f" in value of ***{amount_micro / (10 ** 7):,.7f} " \
                                                 f"{asset_code.upper()}*** to" \
                                                 f" {len(recipients_list)} users."

                                await self.special_payment(ctx=ctx, recipients_list=recipients_list,
                                                           amount_micro_recipient=amount_micro,
                                                           asset_code=asset_code,
                                                           total_amount_micro=total_micro, tx_type='multi',
                                                           emoji=":gift:",
                                                           channel_msg=channel_message,
                                                           uplink_message=uplink_message,
                                                           subject=subject)
                            else:
                                msg = f'You have successfully cancelled payment request.'
                                await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                                     destination=1,
                                                                     sys_msg_title=CONST_TX_ERROR_TITLE)

                            await ctx.message.channel.delete_messages([verification, msg_usr])
                        except TimeoutError:
                            msg = "Time has run out. Please be faster next time when providing answer to the system"
                            await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                                 destination=1,
                                                                 sys_msg_title=CONST_TX_ERROR_TITLE)
                            await ctx.message.channel.delete_messages([verification])
                    else:
                        msg = f'You have insufficient balance to give away {total_micro / (10 ** 7)} {asset_code.upper()}' \
                              f' to {len(recipients_list)} members.'
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                             destination=1,
                                                             sys_msg_title=CONST_TX_ERROR_TITLE)
                else:
                    msg = 'Recipients list needs to be greater than 0 and less than 10'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                         destination=1,
                                                         sys_msg_title=CONST_TX_ERROR_TITLE)
            else:
                msg = 'Asset code either includes special characters or has not been integrated'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                     destination=1,
                                                     sys_msg_title=CONST_TX_ERROR_TITLE)

        else:
            msg = "Amount you are willing to send to each user needs to be greater than 0"
            await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                 destination=1,
                                                 sys_msg_title=CONST_TX_ERROR_TITLE)

    @commands.command()
    @commands.check(is_public)
    @commands.check(has_wallet)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def loyalty(self, ctx, user_count: int, amount: float, asset_code, *, subject: str = None):
        asset_code = asset_code.lower()
        if amount > 0:
            if 0 < user_count <= 10:
                # Check asset
                if not search("[~!#$%^&*()_+{}:;\']", asset_code) and asset_code in [x["assetCode"] for x in
                                                                                     self.bot.backoffice.token_manager.get_all_tokens()]:
                    # Produce the list of last n historically active
                    msgs = await ctx.channel.history(limit=100).flatten()  # Getting all the messages
                    list_of_recipients = []
                    for msg in msgs:
                        if len(list_of_recipients) < int(user_count):
                            if msg.author.id != int(ctx.author.id) and not msg.author.bot:
                                if msg.author not in list_of_recipients:
                                    list_of_recipients.append(msg.author)
                        else:
                            break

                    if len(list_of_recipients) > 0:  # Check if recipients exist
                        amount_micro = amount * (10 ** 7)  # Converting total amount to micro
                        total_micro = amount_micro * len(list_of_recipients)  # Multiplying amount by total recipients

                        # CHeckin senders availabale balance
                        if total_micro <= self.bot.backoffice.wallet_manager.get_ticker_balance(asset_code=asset_code,
                                                                                                user_id=ctx.message.author.id):
                            message_content = f"{ctx.message.author.mention} are you sure you would like to give " \
                                              f"latest ***{len(list_of_recipients)}*** active users {amount_micro / (10 ** 7):,.7f} {asset_code.upper()} each?" \
                                              f"Answer with either ***yes*** or ***no*** ... Request will be cancelled in " \
                                              f"***10*** seconds if no response received."

                            verification = await ctx.channel.send(content=message_content)
                            try:
                                msg_usr = await self.bot.wait_for('message', check=check(ctx.message.author),
                                                                  timeout=10)

                                if str(msg_usr.content.lower()) == 'yes':

                                    # Channel Message for payment
                                    recipients = ' '.join(rec.mention for rec in list_of_recipients)
                                    channel_message = f":military_medal: {recipients}, user ***{ctx.message.author}***" \
                                                      f" thanked you with ***{amount_micro / (10 ** 7):,.7f} " \
                                                      f"{asset_code.upper()}*** for being a loyal and active member."

                                    # Uplink messages for payment
                                    uplink_message = f":military_medal: Loyalty distributed on " \
                                                     f"***{ctx.guild}*** channel ***{ctx.message.channel}***" \
                                                     f" in value of ***{total_micro / (10 ** 7):,.7f} " \
                                                     f"{asset_code.upper()}*** amongst" \
                                                     f" {len(list_of_recipients)} users."

                                    await self.special_payment(ctx=ctx, recipients_list=list_of_recipients,
                                                               amount_micro_recipient=amount_micro,
                                                               asset_code=asset_code,
                                                               total_amount_micro=total_micro, tx_type='loyalty',
                                                               emoji=":military_medal:",
                                                               channel_msg=channel_message,
                                                               uplink_message=uplink_message,
                                                               subject=subject,
                                                               )

                                else:
                                    msg = f'You have successfully cancelled payment request.'
                                    await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                                         destination=1,
                                                                         sys_msg_title=CONST_TX_ERROR_TITLE)
                                await ctx.message.channel.delete_messages([verification, msg_usr])
                            except TimeoutError:
                                await ctx.message.channel.delete_messages([verification])
                                msg = "Time has run out. Please be faster next time when providing answer to the system"
                                await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                                     destination=1,
                                                                     sys_msg_title=CONST_TX_ERROR_TITLE)
                        else:
                            msg = 'Insufficient wallet balance'
                            await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                                 destination=1,
                                                                 sys_msg_title=CONST_TX_ERROR_TITLE)
                    else:
                        msg = 'After processing, Crypto Link could not find suitable ' \
                              ' recipients. Please try again later. '
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                             destination=1,
                                                             sys_msg_title=CONST_TX_ERROR_TITLE)
                else:
                    msg = 'Asset code either includes special characters or has not been integrated'
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                         destination=1,
                                                         sys_msg_title=CONST_TX_ERROR_TITLE)
            else:
                msg = 'The amount of recipients needs to be in the range 1-10.'
                await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                     destination=1,
                                                     sys_msg_title=CONST_TX_ERROR_TITLE)


        else:
            msg = "Amount you are willing to send to each user needs to be greater than 0"
            await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                 destination=1,
                                                 sys_msg_title=CONST_TX_ERROR_TITLE)

    @commands.command()
    @commands.check(is_public)
    @commands.check(has_wallet)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def to_role(self, ctx, role: Role, amount: int, asset_code: str, *, subject=None):
        """
        Role payments
        """
        amount_atomic = amount * (10 ** 7)
        asset_code = asset_code.lower()
        if ctx.guild.owner_id == ctx.author.id or ctx.author.id == 360367188432912385:
            if amount_atomic > 0:
                if not search("[~!#$%^&*()_+{}:;\']", asset_code) and asset_code in [x["assetCode"] for x in
                                                                                     self.bot.backoffice.token_manager.get_all_tokens()]:
                    filtered_members = [m for m in role.members if not m.bot]

                    if filtered_members:
                        total_atomic = amount_atomic * len(filtered_members)  # Total to send
                        if total_atomic <= self.bot.backoffice.wallet_manager.get_ticker_balance(asset_code=asset_code,
                                                                                                 user_id=ctx.message.author.id):
                            message_content = f"{ctx.message.author.mention} are you sure you would like to " \
                                              f"send in total of {total_atomic / (10 ** 7)} {asset_code.upper()} " \
                                              f"({amount_atomic / (10 ** 7)}/member) amongst {len(filtered_members)}" \
                                              f"members part of role {role.mention}?"
                            verification = await ctx.channel.send(content=message_content)
                            try:
                                msg_usr = await self.bot.wait_for('message', check=check(ctx.message.author),
                                                                  timeout=10)

                                if str(msg_usr.content.lower()) == "yes":
                                    # Check balance of the author
                                    count_new, new_recipients = self.check_recipients_wallets(
                                        recipients=filtered_members)

                                    # Send batch payments
                                    batch_payments_lists = [
                                        self.bot.backoffice.wallet_manager.as_update_coin_balance(
                                            coin=asset_code.lower(),
                                            user_id=recipient.id,
                                            amount=int(amount_atomic),
                                            direction=1) for recipient in filtered_members]

                                    await gather(*batch_payments_lists)

                                    channel_message = f":mortar_board: {ctx.message.author.mention} sent " \
                                                      f"members with role {role.mention} " \
                                                      f"{total_atomic / (10 ** 7)} {asset_code.upper()} " \
                                                      f"({amount_atomic / (10 ** 7)}/member)"
                                    await ctx.channel.send(embed=channel_message)

                                    # Report to sender
                                    special_embed = Embed(title=f':outbox_tray: Special outgoing Payment',
                                                          description=f'You have executed special '
                                                                      f'payment on {ctx.message.guild} '
                                                                      f'channel {ctx.message.channel}.',
                                                          colour=Colour.red())
                                    special_embed.add_field(name=':pager: payment type',
                                                            value=f':mortar_board: Payment to Role',
                                                            inline=True)
                                    special_embed.add_field(name=':calendar: Date and time of payment',
                                                            value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                            inline=True)
                                    special_embed.add_field(name=':mega: Subject of payment',
                                                            value=f"```{subject}```",
                                                            inline=False)
                                    special_embed.add_field(name=':envelope:  __**Payment Slip**__',
                                                            value=f'```Per user:{amount_atomic / (10 ** 7):,.7f}'
                                                                  f' {asset_code}\n'
                                                                  f'Total Recipients: {len(filtered_members)}\n'
                                                                  f'-----------------------------------------\n'
                                                                  f'Total sent: '
                                                                  f'{total_atomic / (10 ** 7):,.7f} {asset_code}\n```',
                                                            inline=False)
                                    special_embed.set_footer(text='Thank you for using Crypto Link.')
                                    try:
                                        await ctx.author.send(embed=special_embed)
                                    except Exception:
                                        await ctx.channel.send(content=f'{ctx.author.mention} Crypto Link could '
                                                                       f'not deliver the payment report as DMs are blocked',
                                                               delete_after=10)

                                    # Distribute uplink messages
                                    explorer_msg = f":mortar_board: members with role {role} on " \
                                                   f"***{ctx.guild}*** channel ***{ctx.message.channel}***" \
                                                   f" received {total_atomic / (10 ** 7)} {asset_code.upper()}*** "
                                    up_link_channels = [self.bot.get_channel(id=int(chn)) for chn in
                                                        self.bot.backoffice.guild_profiles.get_all_explorer_applied_channels()]
                                    for chn in up_link_channels:
                                        if chn is not None:
                                            await chn.send(content=explorer_msg)

                                    # TODO update bot and server stats


                            except TimeoutError:
                                await ctx.message.channel.delete_messages([verification])
                                msg = "Time has run out. Please be faster next time when providing answer to the system."
                                await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                                     destination=1,
                                                                     sys_msg_title=CONST_TX_ERROR_TITLE)

                        else:
                            msg = f'{ctx.author.mention} You have insufficient balance to make the payment. Please ' \
                                  f'recheck your balance. '
                            await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                                 destination=1,
                                                                 sys_msg_title=CONST_TX_ERROR_TITLE)

                    else:
                        msg = f'Role {role.mention} has no members after processing. This might result if role members ' \
                              f'are only Bots, or the role itself is empty'
                        await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                             destination=1,
                                                             sys_msg_title=CONST_TX_ERROR_TITLE)
                else:
                    msg = f'Asset with code {asset_code.upper()} does not exist or has not been integrated into the ' \
                          f'system yet. '
                    await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                         destination=1,
                                                         sys_msg_title=CONST_TX_ERROR_TITLE)

            else:
                msg = f"Amount you are willing to send to each user needs to be greater than 0 {asset_code}"
                await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                     destination=1,
                                                     sys_msg_title=CONST_TX_ERROR_TITLE)

        else:
            msg = f"This payment type is currently available oonly to owner of the {ctx.guild} {ctx.guild.owner}"
            await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                 destination=1,
                                                 sys_msg_title=CONST_TX_ERROR_TITLE)

    @give.error
    async def give_error(self, ctx, error):
        pass

    @to_role.error
    async def to_role_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            title = f'__System Transaction Error__'
            message = f'In order to execute P2P transaction you need to be registered into the system, and ' \
                      f'transaction request needs to be executed on one of the text public text channels ' \
                      f'on {ctx.message.guild}'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)
        elif isinstance(error, commands.CommandOnCooldown):
            title = f'__Command on cool-down__!'
            message = f'{error}. Please try again after {error.retry_after}s'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)

        elif isinstance(error, commands.MissingRequiredArgument):
            title = f'__Missing Required Argument Error __'
            message = f'{str(error)}. The command structure is \n' \
                      f'`{self.bot.get_command_str()}to_role <@discord.Role> <amount> <asset_code>`'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)


def setup(bot):
    bot.add_cog(SpecialPaymentCommands(bot))
