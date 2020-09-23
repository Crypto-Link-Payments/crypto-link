from datetime import datetime

import discord

from cogs.utils.monetaryConversions import convert_to_usd

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'


class CustomMessages:
    def __init__(self):
        pass

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
        else:
            pass

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
    async def transaction_report_to_user(ctx, user, destination, amount, symbol, direction: int, message:str = None):
        """
        Transaction report to user
        :param user:
        :param destination:
        :param amount:
        :param symbol:
        :param direction:
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
            avatar= user.avatar_url

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
                             icon_url='https://static.coingecko.com/s/thumbnail-007177f3eca19695592f0b8b0eabbdae282b54154e1be912285c9034ea6cbaf2.png')
        try:
            await destination.send(embed=tx_report)
        except Exception as e:
            print('Transaction report to user could not be send due to:')
            print(e)
            print('========================')
            pass

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
    async def coin_withdrawal_notification(coin, recipient: discord.User, amount, fee, thumbnail,hash, destination, link, ledger: int):
        notify = discord.Embed(title="Withdrawal Notification",
                               description=f' {coin} withdrawal Successfully processed',
                               colour=discord.Colour.green())

        notify.add_field(name="Time of withdrawal",
                         value=str(datetime.utcnow()),
                         inline=False)
        notify.add_field(name='Destination',
                         value=destination,
                         inline=False)
        notify.add_field(name='Transaction hash',
                         value=hash,
                         inline=False)
        notify.add_field(name='Withdrawed amount',
                         value=f'{amount} {CONST_STELLAR_EMOJI}',
                         inline=False)
        notify.add_field(name='Crypto Link Fee',
                         value=fee,
                         inline=False)
        notify.add_field(name='Ledger',
                         value=str(ledger),
                         inline=False)
        notify.add_field(name='Explorer Link',
                         value=link,
                         inline=False)
        notify.set_thumbnail(url=thumbnail)
        await recipient.send(embed=notify)
