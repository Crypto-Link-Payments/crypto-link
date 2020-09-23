from datetime import datetime

import discord
from discord import errors

from cogs.utils.monetaryConversions import convert_to_usd
from utils.tools import Helpers

helper = Helpers()
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
notification_channels = helper.read_json_file(file_name='autoMessagingChannels.json')


class CustomMessages:
    """
    Class holding custom messages for Crypto Link system
    """

    def __init__(self):
        """
        For initiation
        """
        pass

    @staticmethod
    async def send_deposit_notification_channel(channel, avatar, user, stroops):
        """
        Sending message to user on successful processed deposit
        """

        notify = discord.Embed(title='System Deposit Notification',
                               description='Deposit has been processed')
        notify.set_thumbnail(url=avatar)
        notify.add_field(name='User details',
                         value=f'{user} ID; {user.id}',
                         inline=False)
        notify.add_field(name='Deposit details',
                         value=f'Amount: {stroops / 10000000:.7f} {CONST_STELLAR_EMOJI}',
                         inline=False)
        await channel.send(embed=notify)

    @staticmethod
    async def send_unidentified_deposit_msg(channel, deposit_details):
        """
        deposit or memo could not be identifies
        """

        deposit_unidentified = f"```json\n{deposit_details}```"

        await channel.send(content=deposit_unidentified)

    @staticmethod
    async def embed_builder(ctx, title, description, data: list, destination=None, thumbnail=None):
        """
        Build embed from data provided
        :param ctx: Discord Context
        :param title: Title for embed
        :param description: Description of embed
        :param data: data as list of dict
        :param destination: where embed is sent
        :param thumbnail: where embed is sent
        :return:
        """
        embed = discord.Embed(title=title,
                              description=description,
                              colour=discord.Colour.gold())
        for d in data:
            embed.add_field(name=d['name'],
                            value=d['value'],
                            inline=False)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if destination:
            await ctx.author.send(embed=embed)
        else:
            await ctx.channel.send(embed=embed, delete_after=40)

    @staticmethod
    async def system_message(ctx, color_code: int, message: str, destination: int, sys_msg_title: str = None):
        """
        Custom System Messages
        """
        if color_code == 0:
            signal = 0x319f6b
            emoji = ":robot: "
        else:
            signal = discord.Colour.red()
            emoji = ":warning:"

        if sys_msg_title is None:
            sys_msg_title = 'System Message'

        sys_embed = discord.Embed(title=f"{emoji} System Message {emoji}",
                                  description=sys_msg_title,
                                  colour=signal)
        sys_embed.add_field(name='Message',
                            value=message)

        if destination == 0:
            await ctx.author.send(embed=sys_embed)
        else:
            await ctx.channel.send(embed=sys_embed, delete_after=100)

    @staticmethod
    async def transaction_report_to_user(ctx, user, destination, amount, symbol, direction: int, message: str = None):
        """
        Transaction report to user
        :param ctx: Discord Context
        :param user:
        :param destination:
        :param amount:
        :param symbol:
        :param direction:
        :param message: Optional user message
        :return:
        """
        title = ''
        if symbol == 'xlm':
            amount_str = f"{amount:9.7f} <:stelaremoji:684676687425961994>"
            in_dollar = convert_to_usd(amount=amount, coin_name='stellar')

        if direction == 0:
            title = 'Outgoing transaction'
            col = discord.Colour.red()
            destination_txt = 'Recipient'
            avatar = user.avatar_url

        elif direction == 1:
            title = 'Incoming transaction'
            col = discord.Colour.green()
            destination_txt = 'Sender:'
            avatar = destination.avatar_url

        tx_report = discord.Embed(title=title,
                                  colour=col,
                                  timestamp=datetime.utcnow())
        tx_report.set_thumbnail(url=avatar)
        tx_report.add_field(name=destination_txt,
                            value=f'{user}',
                            inline=False)
        tx_report.add_field(name='Guild Origin',
                            value=f'{ctx.message.guild} ({ctx.message.guild.id})',
                            inline=False)
        tx_report.add_field(name='Subject',
                            value=message)
        tx_report.add_field(name=f'Transaction value',
                            value=f'{amount_str}',
                            inline=False)
        tx_report.add_field(name=f'Conversion Rate',
                            value=f'{in_dollar["usd"]}$/XLM')
        tx_report.add_field(name=':currency_exchange: Fiat Value :currency_exchange: ',
                            value=f"{in_dollar['total']}$ ({in_dollar['usd']}$/XLM)",
                            inline=False)
        tx_report.set_footer(text='Conversion rates provided by CoinGecko',
                             icon_url='https://static.coingecko.com/s/thumbnail-'
                                      '007177f3eca19695592f0b8b0eabbdae282b54154e1be912285c9034ea6cbaf2.png')
        try:
            await destination.send(embed=tx_report)
        except Exception as e:
            print('Transaction report to user could not be send due to:')
            print(e)
            print('========================')

    @staticmethod
    async def transaction_report_to_channel(ctx, recipient: discord.User, amount, currency):
        """
        Discord Transaction report to the channel
        :param ctx: discord Context
        :param recipient: discord.user
        :param amount: amount in currency
        :param currency: currency symbol
        :return: embed
        """
        if currency == 'xlm':
            amount_str = f"{amount:9.7f} <:stelaremoji:684676687425961994>"
            in_dollar = convert_to_usd(amount=amount, coin_name='stellar')

        message = f'{recipient.mention} user {ctx.message.author} just sent you {amount_str} ({in_dollar["total"]}$)'
        await ctx.channel.send(content=message, delete_after=360)

    @staticmethod
    async def coin_activity_notification_message(coin, recipient: discord.User, memo, tx_hash, source_acc, amount,
                                                 color_code: int):
        if color_code == 0:
            signal = 0x319f6b
        else:
            signal = discord.Colour.red()

        sys_embed = discord.Embed(title="Deposit Notification",
                                  description=f' {coin} deposit with deposit id{memo} has been successfully processed',
                                  colour=signal)
        sys_embed.add_field(name='From',
                            value=source_acc, inline=False)
        sys_embed.add_field(name='Tx hash',
                            value=tx_hash,
                            inline=False)
        sys_embed.add_field(name="Amount",
                            value=f"{amount / 10000000:9.7f} <:stelaremoji:684676687425961994>",
                            inline=False)

        await recipient.send(embed=sys_embed)

    @staticmethod
    async def withdrawal_notify(ctx, withdrawal_data: dict, coin, fee, thumbnail,
                                link):
        notify = discord.Embed(title="Withdrawal Notification",
                               description=f' {coin} withdrawal Successfully processed',
                               colour=discord.Colour.green())

        notify.add_field(name="Time of withdrawal",
                         value=str(datetime.utcnow()),
                         inline=False)
        notify.add_field(name='Destination',
                         value=withdrawal_data["destination"],
                         inline=False)
        notify.add_field(name='Transaction hash',
                         value=withdrawal_data["hash"],
                         inline=False)
        notify.add_field(name='Withdrawal amount',
                         value=f'{withdrawal_data["amount"]} {CONST_STELLAR_EMOJI}',
                         inline=False)
        notify.add_field(name='Crypto Link Fee',
                         value=fee,
                         inline=False)
        notify.add_field(name='Explorer Link',
                         value=link,
                         inline=False)
        notify.set_thumbnail(url=thumbnail)

        try:
            await ctx.author.send(embed=notify)

        except errors.DiscordException:
            error_msg = discord.Embed(title=f'Withdrawal Notification',
                                      description=f'You have received this message because'
                                                  f' withdrawal notification could not be'
                                                  f' send to DM. Please allow bot to send'
                                                  f' you messages',
                                      colour=discord.Colour.green())
            error_msg.add_field(name='Explorer Link',
                                value=link)
            error_msg.set_footer(text='This message will self-destruct in 360 seconds')
            await ctx.channel.send(embed=error_msg, content=f'{ctx.message.author.mention}',
                                   delete_after=360)

    @staticmethod
    async def withdrawal_notification_channel(ctx, channel, withdrawal_data):
        # create withdrawal notification for channel
        notify = discord.Embed(title='Stellar Withdrawal Notification',
                               description='Withdrawal has been processed',
                               colour=discord.Colour.gold())
        notify.add_field(name='Guild',
                         value=f'{ctx.message.guild} ID; {ctx.message.guild.id}',
                         inline=False)
        notify.add_field(name='User details',
                         value=f'{ctx.message.author} \nID; {ctx.message.author.id}',
                         inline=False)
        notify.add_field(name='Withdrawal details',
                         value=f'Time: {withdrawal_data["time"]}\n'
                               f'Destination: {withdrawal_data["destination"]}\n'
                               f'Amount: {withdrawal_data["amount"]} {CONST_STELLAR_EMOJI}',
                         inline=False)
        await channel.send(embed=notify)

    @staticmethod
    async def cl_staff_incoming_funds_notification(sys_channel: discord.TextChannel, amount):
        notify = discord.Embed(title='Bot Stellar Wallet Activity',
                               description='Bot Wallet has been credited because user '
                                           'has initiated on-chain withdrawal',
                               color=discord.Colour.blurple())
        notify.add_field(name='Value',
                         value=f'{amount / 10000000}{CONST_STELLAR_EMOJI}')
        await sys_channel.send(embed=notify)
