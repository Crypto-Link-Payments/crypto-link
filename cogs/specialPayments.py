from discord.ext import commands
from discord import User
from discord import Embed
from discord.ext.commands import command, Cog
from discord_components import DiscordComponents, Button, ButtonStyle

from asyncio import TimeoutError, sleep
from random import choice

from random import choice
from discord import Member as DiscordMember
from discord import Embed, Colour
from discord.ext.commands import Greedy
from discord_components import DiscordComponents, Button, ButtonStyle, SelectOption, Select, InteractionType
from re import search
from cogs.utils import monetaryConversions
from datetime import datetime
from utils.customCogChecks import is_public, has_wallet
from cogs.utils.systemMessaages import CustomMessages
import asyncio

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

    async def recipient_report(self, ctx, recipient, tx_time: str, total_amount: float, asset_code: str, subject: str):
        special_embed = Embed(title=f':inbox_tray:  Incoming Payment',
                              description=f'You have received payment on {ctx.message.guild} '
                                          f'channel {ctx.message.channel}. Check details below.',
                              colour=Colour.green())
        special_embed.add_field(name=':calendar: Date and time of payment',
                                value=tx_time,
                                inline=True)
        special_embed.add_field(name=':cowboy: Sender',
                                value=f'{ctx.author} (ID: {ctx.author.id})',
                                inline=True)
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
                            recipients_list: list, subject: str):
        recipients = '\n'.join(f'{recipient}' for recipient in recipients_list)
        special_embed = Embed(title=f':outbox_tray: Special outgoing Payment',
                              description=f'You have executed special payment on {ctx.message.guild} '
                                          f'channel {ctx.message.channel}.',
                              colour=Colour.red())
        special_embed.add_field(name=':calendar: payment type',
                                value=f'{tx_type}',
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

    @commands.command()
    @commands.check(is_public)
    @commands.check(has_wallet)
    async def give(self, ctx, recipients: Greedy[DiscordMember], amount: float, asset_code, *, subject: str = None):
        asset_code = asset_code.lower()
        tx_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
                                          f"{total_micro / (10 ** 7)} {asset_code.upper()} distributed equally amongst " \
                                          f"{len(recipients_list)} users?\n" \
                                          f"Answer with either ***yes*** or ***no*** ... Request will be cancelled in " \
                                          f"***10*** seconds if no response received."

                        verification = await ctx.channel.send(content=message_content)
                        msg_usr = await self.bot.wait_for('message', check=check(ctx.message.author), timeout=10)

                        if str(msg_usr.content.lower()) == 'yes':
                            # Checking recipients wallet status
                            count_new, new_recipients = self.check_recipients_wallets(recipients=recipients_list)
                            #
                            # Load registered channel for crypto link
                            load_channels = [self.bot.get_channel(id=int(chn)) for chn in
                                             self.bot.backoffice.guild_profiles.get_all_explorer_applied_channels()]
                            # Updating statistics
                            if count_new > 0:
                                # Updating registered user stats for guild
                                await self.bot.backoffice.stats_manager.update_batch_registered_users(
                                    guild_id=ctx.message.guild.id, count=count_new)

                                # Updating users stats for created bridges
                                await self.bot.backoffice.stats_manager.create_bridges(user_id=ctx.message.author.id,
                                                                                       count=count_new)

                                # Notify sender on new bridges
                                await self.bridges_notification(ctx, count_new)

                                # Send messages on new account to uplink
                                current_total = self.bot.backoffice.account_mng.count_registrations()
                                explorer_msg = f':new: {count_new} user/s registered into ***{self.bot.user} System*** ' \
                                               f' through special payments on {ctx.message.guild} (Σ {current_total})'

                                for chn in load_channels:
                                    await chn.send(content=explorer_msg)

                            # deducting total amount from sender
                            if self.bot.backoffice.wallet_manager.update_coin_balance(coin=asset_code,
                                                                                      user_id=ctx.message.author.id,
                                                                                      amount=int(total_micro),
                                                                                      direction=2):
                                batch_payments_lists = [
                                    self.bot.backoffice.wallet_manager.as_update_coin_balance(coin=asset_code.lower(),
                                                                                              user_id=recipient.id,
                                                                                              amount=int(amount_micro),
                                                                                              direction=1) for recipient
                                    in recipients_list]
                                await asyncio.gather(*batch_payments_lists)

                                # Convert total
                                total_normal = total_micro / (10 ** 7)
                                # Send report to recipients
                                subject = process_message(subject)
                                await self.sender_report(ctx=ctx, tx_type='Give', tx_time=tx_time,
                                                         total_value=total_normal,
                                                         asset_code=asset_code.upper(),
                                                         recipients_list=recipients_list,
                                                         subject=subject)

                                # send report for sender
                                batch_reports = [self.recipient_report(ctx=ctx, recipient=recipient, tx_time=tx_time,
                                                                       total_amount=amount_micro / (10 ** 7),
                                                                       asset_code=asset_code.upper(), subject=subject)
                                                 for recipient in recipients_list]

                                await asyncio.gather(*batch_reports)


                            else:
                                msg = 'Payment could not be processed at this moment please try again later'
                                await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                                     destination=1,
                                                                     sys_msg_title=CONST_TX_ERROR_TITLE)
                        else:
                            msg = f'You have successfully cancelled payment request.'
                            await custom_messages.system_message(ctx=ctx, color_code=1, message=msg,
                                                                 destination=1,
                                                                 sys_msg_title=CONST_TX_ERROR_TITLE)

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

    @give.error
    async def give_error(self, ctx, error):
        if isinstance(error, TimeoutError):
            msg = 'Time outed'
            print(msg)


def setup(bot):
    bot.add_cog(SpecialPaymentCommands(bot))
