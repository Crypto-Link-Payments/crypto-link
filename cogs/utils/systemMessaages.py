from datetime import datetime

import discord
from discord import errors
from discord import Role, Embed, Colour, TextChannel
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

    def filter_message(self, message, tx_type: str):
        msg_streamed = ''
        if tx_type == 'public':
            msg_streamed += message

        elif tx_type == 'private':
            msg_streamed += ":detective:"

        elif tx_type == 'emoji':
            pass

        elif tx_type == 'multi':
            pass

        elif tx_type == 'squad':
            pass

        elif tx_type == 'role_purchase':
            pass

        return msg_streamed

    def get_emoji(self, tx_type):
        if tx_type == 'public':
            emoji = ':cowboy:'
        elif tx_type == 'private':
            emoji = ':detective:'
        return emoji

    @staticmethod
    async def sys_deposit_notifications(channel, user: discord.User, tx_details: dict):
        """
        Sending message to user on successful processed deposit
        """

        notify = discord.Embed(title='System Deposit Notification',
                               description='Deposit has been processed',
                               timestamp=datetime.utcnow())
        notify.set_thumbnail(url=user.avatar_url)
        notify.add_field(name='User details',
                         value=f'{user} ID; {user.id}',
                         inline=False)
        notify.add_field(name='From',
                         value=f'{tx_details["source_account"]}', inline=False)
        notify.add_field(name='Tx hash',
                         value=f'{tx_details["hash"]}')
        notify.add_field(name='Deposit Value',
                         value=f"Amount: {int(tx_details['asset_type']['amount']) / 10000000:9.7f} {tx_details['asset_type']['code']}",
                         inline=False)
        await channel.send(embed=notify)

    @staticmethod
    async def send_unidentified_deposit_msg(channel, tx_details: dict):
        """
        deposit or memo could not be identifies
        """

        notify = discord.Embed(title=':warning: System Deposit Notification :warning:',
                               description='Unidentified Deposit',
                               timestamp=datetime.utcnow(),
                               colour=Colour.red())
        notify.add_field(name='From',
                         value=f'{tx_details["source_account"]}', inline=False)
        notify.add_field(name='Tx hash',
                         value=f'{tx_details["hash"]}')
        notify.add_field(name='Deposit Value',
                         value=f"Amount: {int(tx_details['asset_type']['amount']) / 10000000:9.7f} {tx_details['asset_type']['code']}",
                         inline=False)
        await channel.send(embed=notify)

    @staticmethod
    async def embed_builder(ctx, title, description, data: list, destination=None, thumbnail=None, c: Colour = None):
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

        if not c:
            c = discord.Colour.gold()

        embed = discord.Embed(title=title,
                              description=description,
                              colour=c)
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
    async def system_message(ctx, message: str, color_code, destination: int, sys_msg_title: str = None):
        """
        Custom System Messages
        """
        if isinstance(color_code,Colour):
            emoji = "robot"
            c = color_code
        else:
            if color_code == 0:
                c = 0x319f6b
                emoji = ":robot: "
            else:
                c = discord.Colour.red()
                emoji = ":warning:"

        if sys_msg_title is None:
            sys_msg_title = 'System Message'

        sys_embed = discord.Embed(title=f"{emoji} System Message {emoji}",
                                  description=sys_msg_title,
                                  colour=c)
        sys_embed.add_field(name='Message',
                            value=message)

        if destination == 0:
            await ctx.author.send(embed=sys_embed)
        else:
            await ctx.channel.send(embed=sys_embed, delete_after=100)

    async def transaction_report_to_user(self, ctx, user, destination, transaction_data: dict, direction: int,
                                         tx_type: str,
                                         message: str = None):
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
        tx_type_emoji = self.get_emoji(tx_type=tx_type)

        if direction == 0:
            title = f':outbox_tray: Outgoing {tx_type_emoji} **__{tx_type.title()}__** transaction :outbox_tray: '
            col = discord.Colour.red()
            destination_txt = f'{tx_type_emoji} Recipient {tx_type_emoji} '
            avatar = user.avatar_url

        elif direction == 1:
            title = f':inbox_tray: Incoming {tx_type_emoji} {tx_type.title()} transaction :inbox_tray: '
            col = discord.Colour.green()
            destination_txt = ':postbox:  Sender :postbox: '
            avatar = destination.avatar_url

        tx_report = discord.Embed(title=title,
                                  colour=col,
                                  timestamp=datetime.utcnow())
        tx_report.set_thumbnail(url=avatar)
        tx_report.add_field(name=f'{destination_txt}',
                            value=f'{user}',
                            inline=False)
        tx_report.add_field(name=':post_office: Guild Origin :post_office: ',
                            value=f'{ctx.message.guild} ({ctx.message.guild.id})',
                            inline=False)
        tx_report.add_field(name=':love_letter: Note :love_letter: ',
                            value=message)
        tx_report.add_field(name='Transaction value',
                            value=f'{transaction_data["amount"]} {transaction_data["emoji"]} (${transaction_data["conversion"]})',
                            inline=False)
        if transaction_data["conversion"] != 0:
            tx_report.add_field(name='Conversion Rate',
                                value=f'${transaction_data["conversionRate"]}/{transaction_data["ticker"]}',
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
    async def deposit_notification_message(recipient: discord.User, tx_details: dict):

        sys_embed = discord.Embed(title=":inbox_tray: __Deposit Processed__ :inbox_tray: ",
                                  description=f'Deposit processed successfully!',
                                  colour=Colour.dark_purple(),
                                  timestamp=datetime.utcnow())
        sys_embed.add_field(name='From',
                            value=f'{tx_details["source_account"]}', inline=False)
        sys_embed.add_field(name='Tx hash',
                            value=f'{tx_details["hash"]}',
                            inline=False)
        sys_embed.add_field(name=f'Asset',
                            value=f'{tx_details["asset_type"]["code"]}')
        sys_embed.add_field(name="Amount",
                            value=f"{int(tx_details['asset_type']['amount']) / 10000000:9.7f}",
                            inline=False)
        await recipient.send(embed=sys_embed)

    @staticmethod
    async def withdrawal_notify(ctx, withdrawal_data: dict, fee):
        notify = discord.Embed(title="Withdrawal Notification",
                               description=f'Withdrawal Successfully processed',
                               timestamp=datetime.utcnow(),
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
        notify.add_field(name='Withdrawal asset details',
                         value=f'{round(withdrawal_data["amount"] / 10000000, 7)} {withdrawal_data["asset"]}',
                         inline=False)
        notify.add_field(name='Crypto Link Fee',
                         value=fee,
                         inline=False)
        notify.add_field(name='Explorer Link',
                         value=withdrawal_data['explorer'],
                         inline=False)
        notify.set_thumbnail(url=ctx.message.author.avatar_url)

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
                                value=withdrawal_data['explorer'])
            error_msg.set_footer(text='This message will self-destruct in 360 seconds')
            await ctx.channel.send(embed=error_msg, content=f'{ctx.message.author.mention}',
                                   delete_after=360)

    @staticmethod
    async def withdrawal_notification_channel(ctx, channel, withdrawal_data):
        # create withdrawal notification for channel
        notify = discord.Embed(title='Stellar Withdrawal Notification',
                               description='Withdrawal has been processed',
                               colour=discord.Colour.gold())
        if isinstance(ctx.channel, TextChannel):
            notify.add_field(name='Origin',
                             value=f'{ctx.message.guild} ID; {ctx.message.guild.id}',
                             inline=False)
        else:
            notify.add_field(name='Origin',
                             value=f'DM with bot',
                             inline=False)
        notify.add_field(name='User details',
                         value=f'{ctx.message.author} \nID; {ctx.message.author.id}',
                         inline=False)
        notify.add_field(name='Withdrawal details',
                         value=f'Time: {withdrawal_data["time"]}\n'
                               f'Destination: {withdrawal_data["destination"]}\n'
                               f'Amount: {round(withdrawal_data["amount"] / 10000000, 7)} {withdrawal_data["asset"]}',
                         inline=False)
        await channel.send(embed=notify)

    @staticmethod
    async def cl_staff_incoming_funds_notification(sys_channel: discord.TextChannel, incoming_fees: str):
        notify = discord.Embed(title='Bot Stellar Wallet Activity',
                               description='Bot Wallet has been credited because user '
                                           'has initiated on-chain withdrawal',
                               color=discord.Colour.blurple())
        notify.add_field(name='Value',
                         value=f'{incoming_fees}')
        await sys_channel.send(embed=notify)

    @staticmethod
    async def user_role_purchase_msg(ctx, role: Role, role_details: dict):
        # Send notification to user
        role_embed = discord.Embed(name=':shopping_cart: __Membership purchase successful__ :shopping_cart: ',
                                   title='Congratulations on '
                                         'obtaining the role',
                                   description='Details on obtained role',
                                   colour=discord.Colour.gold())
        role_embed.set_thumbnail(url=ctx.message.guild.icon_url)
        role_embed.add_field(name=':convenience_store: Community :convenience_store:',
                             value=f'{ctx.message.guild}  \n'
                                   f'ID:{ctx.message.guild.id}',
                             inline=False)
        role_embed.add_field(name=':japanese_ogre: Role: :japanese_ogre: ',
                             value=f'{role.name}  ID:{role.id}',
                             inline=False)
        role_embed.add_field(name=f':calendar: Role Purchase Date :calendar: ',
                             value=f'{role_details["roleStart"]}')
        role_embed.add_field(name=':timer: Role Expiration :timer: ',
                             value=f'{role_details["roleEnd"]} (in: {role_details["roleLeft"]})',
                             inline=False)
        role_embed.add_field(name=':money_with_wings: Role Value :money_with_wings: ',
                             value=f'{role_details["dollarValue"]} $ \n'
                                   f'{role_details["roleRounded"]} {CONST_STELLAR_EMOJI}\n'
                                   f'{role_details["usdRate"]} / 1{CONST_STELLAR_EMOJI}',
                             inline=False)
        try:
            await ctx.author.send(embed=role_embed)
        except Exception as e:
            print(e)
            await ctx.channel.send(embed=role_embed, delete_after=10)

    @staticmethod
    async def guild_owner_role_purchase_msg(ctx, role: Role, role_details: dict):
        incoming_funds = discord.Embed(
            name=':convenience_store: __Merchant system funds credited__ :convenience_store: ',
            title='__Incoming funds to corporate '
                  'wallet___',
            description=f'Role has been purchased on your community '
                        f'at {role_details["roleStart"]}.',
            colour=discord.Colour.green())

        incoming_funds.add_field(name=':japanese_ogre: Role Purchased :japanese_ogre: ',
                                 value=f"Name: {role.name}\n"
                                       f"Id: {role.id}",
                                 inline=False)
        incoming_funds.set_thumbnail(url=f'{ctx.message.author.avatar_url}')
        incoming_funds.add_field(name=':money_with_wings: Role Value :money_with_wings: ',
                                 value=f'${role_details["dollarValue"]}\n'
                                       f'{role_details["roleRounded"]} {CONST_STELLAR_EMOJI}\n'
                                       f'{role_details["usdRate"]} / 1{CONST_STELLAR_EMOJI}',
                                 inline=False)
        incoming_funds.add_field(name=':cowboy: User Details :cowboy: ',
                                 value=f"User: {ctx.message.author}\n"
                                       f"Id: {ctx.message.author.id}",
                                 inline=False)

        incoming_funds.add_field(name=':clipboard: Role Duration Details :clipboard:  ',
                                 value=f'{role_details["roleDetails"]}',
                                 inline=False)

        await ctx.message.guild.owner.send(embed=incoming_funds)

    @staticmethod
    async def wallet_overall_stats(ctx, utc_now, transaction_stats: dict):
        tx_stats = Embed(title='__Global Account Statistics__',
                         timestamp=utc_now,
                         colour=Colour.blue())
        tx_stats.set_thumbnail(url=ctx.author.avatar_url)
        tx_stats.add_field(name=f':abacus: Outgoing ',
                           value=transaction_stats["sentTxCount"] + transaction_stats["rolePurchase"],
                           inline=True)
        tx_stats.add_field(name=f':abacus: Incoming',
                           value=transaction_stats["receivedCount"],
                           inline=True)

        tx_stats.add_field(name=f':incoming_envelope: Sent P2P ',
                           value=transaction_stats["sentTxCount"],
                           inline=True)

        tx_stats.add_field(name=f':slight_smile: Sent P2P ',
                           value=transaction_stats["emojiTxCount"],
                           inline=True)

        tx_stats.add_field(name=f':cloud_rain: Multi Transactions',
                           value=transaction_stats["multiTxCount"],
                           inline=True)

        tx_stats.add_field(name=f':man_juggling: Role Purchases  ',
                           value=transaction_stats["rolePurchase"],
                           inline=True)
        await ctx.author.send(embed=tx_stats)

    @staticmethod
    async def stellar_wallet_overall(ctx, coin_stats: dict, utc_now):
        for k, v in coin_stats.items():
            coin_stats = Embed(title=f'{k.upper()} wallet statistics',
                               description=f':bar_chart: ***__Statistical Data on Stellar Lumen Discord Wallet__*** '
                                           f':bar_chart:',
                               colour=Colour.light_grey(),
                               timestamp=utc_now)
            coin_stats.add_field(name=f':inbox_tray: Total Deposits',
                                 value=f'Deposited ***{v["depositsCount"]}*** with total '
                                       f'***{v["totalDeposited"]}*** ')
            coin_stats.add_field(name=f'\u200b',
                                 value='\u200b')
            coin_stats.add_field(name=f':outbox_tray: Total Withdrawals ',
                                 value=f'Withdrawn ***{v["withdrawalsCount"]}*** withdrawals with '
                                       f'total ***{v["totalWithdrawn"]}*** ')

            coin_stats.add_field(name=f':family_man_woman_boy: Public Tx',
                                 value=f':incoming_envelope:{v["publicTxSendCount"]}\n'
                                       f':money_with_wings:  {v["publicSent"]}\n'
                                       f':envelope_with_arrow:{v["publicTxReceivedCount"]}\n'
                                       f':money_mouth: {v["publicReceived"]} ')
            coin_stats.add_field(name=f':detective: Private Tx',
                                 value=f':incoming_envelope:{v["privateTxSendCount"]}\n'
                                       f':money_with_wings: {v["privateSent"]}\n'
                                       f':envelope_with_arrow: {v["privateTxReceivedCount"]}\n'
                                       f':money_mouth: {v["privateReceived"]}')
            coin_stats.add_field(name=f'Merchant purchases',
                                 value=f':man_juggling: {v["roleTxCount"]}\n'
                                       f':money_with_wings: {v["spentOnRoles"]}\n',
                                 inline=False)
            await ctx.author.send(embed=coin_stats)

    async def explorer_messages(self, applied_channels: list, message: str, tx_type: str, on_chain: bool = None):
        """
        Transactin reports to all explorer applied channels
        """
        if not on_chain:
            msg_streamed = self.filter_message(message=message, tx_type=tx_type)
            for explorer_channel in applied_channels:
                await explorer_channel.send(msg_streamed)
        else:
            for explorer_channel in applied_channels:
                await explorer_channel.send(message)

    async def transaction_report_to_channel(self, ctx, message: str, tx_type: str):
        """
        Discord Transaction report to the channel
        """
        msg_streamed = self.filter_message(message=message, tx_type=tx_type)
        await ctx.channel.send(content=msg_streamed, delete_after=360)

    @staticmethod
    async def send_special_char_notification(channel, tx: dict):
        special_char = Embed(title=':monkey: Business ',
                             description='Special characters have been identified in MEMO',
                             colour=Colour.red())
        special_char.add_field(name='Transaction details',
                               value=f'{tx}')
        await channel.send(embed=special_char)

    async def send_transfer_notification(self, ctx, member, sys_channel, normal_amount, emoji: str,
                                         chain_name: str):
        """
        Function send information to corporate channel on corp wallet activity
        :param ctx: Discord Context
        :param member: Member to where funds have been transferred
        :param channel_id: channel ID applied for notifications
        :param normal_amount: converted amount from atomic
        :param emoji: emoji identification for the currency
        :param chain_name: name of the chain used in transactions
        :return: discord.Embed
        """

        corp_channel = Embed(
            title=f'__{emoji} Corporate account transfer activity__ {emoji}',
            description=f'Notification on corporate funds transfer activity on {chain_name}',
            colour=Colour.greyple())
        corp_channel.add_field(name='Author',
                               value=f'{ctx.message.author}',
                               inline=False)
        corp_channel.add_field(name='Destination',
                               value=f'{member}')
        corp_channel.add_field(name='Amount',
                               value=f'{normal_amount} {emoji}')
        await sys_channel.send(embed=corp_channel)
