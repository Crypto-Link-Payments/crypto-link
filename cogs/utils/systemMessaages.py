from datetime import datetime

import nextcord
from colorama import Fore

from nextcord import errors
from nextcord import Role, Embed, Colour, TextChannel, User

CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_HASH_STR = ':hash: Transaction Hash :hash: '


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
    def filter_message(message, tx_type: str):
        msg_streamed = ''
        if tx_type == 'public':
            msg_streamed += message

        elif tx_type == 'private':
            msg_streamed += ":detective:"

        elif tx_type == 'role_purchase':
            msg_streamed = f":man_juggling: {message}"
        return msg_streamed

    @staticmethod
    def get_emoji(tx_type):
        if tx_type == 'public':
            emoji = ':cowboy:'
        elif tx_type == 'private':
            emoji = ':detective:'
        return emoji

    @staticmethod
    async def sys_deposit_notifications(channel, user: User, tx_details: dict):
        """
        Sending message to user on successful processed deposit
        """

        notify = Embed(title='System Deposit Notification',
                       description='Deposit has been processed',
                       timestamp=datetime.utcnow())
        notify.add_field(name='User details',
                         value=f'{user} ID; {user.id}',
                         inline=False)
        notify.add_field(name='From',
                         value=f'{tx_details["source_account"]}', inline=False)
        notify.add_field(name=CONST_HASH_STR,
                         value=f'{tx_details["hash"]}')
        notify.add_field(name='Deposit Value',
                         value=f"Amount: {int(tx_details['asset_type']['amount']) / 10000000:9.7f} {tx_details['asset_type']['code']}",
                         inline=False)
        try:
            await channel.send(embed=notify)
        except errors.Forbidden as e:
            print(Fore.RED + f"{e}")

    @staticmethod
    async def send_unidentified_deposit_msg(channel, tx_details: dict):
        """
        deposit or memo could not be identifies
        """

        notify = Embed(title=':warning: System Deposit Notification :warning:',
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
    async def embed_builder(interaction, title, description, data: list, destination=None, thumbnail=None, c: Colour = None):
        if not c:
            c = Colour.gold()

        embed = Embed(title=title, description=description, colour=c)
        for d in data:
            embed.add_field(name=d['name'], value=d['value'], inline=False)

        try:
            # First, always acknowledge the interaction if not done yet
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed,  delete_after=40, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            print("Error while sending embed:", e)
            try:
                await interaction.user.send(embed=embed)
            except:
                pass


    @staticmethod
    async def bridge_notification(ctx, recipient):
        bridge_info = Embed(title=f':bridge_at_night: New Bridge Created :bridge_at_night: ',
                            description=f":construction_worker: You have successfully created new bridge between "
                                        f"Discord user and Stellar. ",
                            colour=Colour.green())
        bridge_info.add_field(name=f'Destination',
                              value=f'{recipient} (ID: {recipient.id})',
                              inline=False)
        bridge_info.add_field(name=f':information_source: Explanation :information_source: ',
                              value=f'Since recipient did not have wallet yet in the system, it has been '
                                    f'automatically created in order for the payment to reach its destination. '
                                    f'With every new account bridges are established and adoption of Stellar increased.'
                                    f' Keep on building')
        await ctx.author.send(embed=bridge_info)

    @staticmethod
    async def system_message(interaction, message: str, color_code, sys_msg_title: str = None,
                            embed_title: str = None, destination: int = 0):
        """
        Custom System Messages
        """
        # Color filtering
        if isinstance(color_code, Colour):
            c = color_code
            emoji = ":robot:"
        else:
            c = 0x319f6b if color_code == 0 else Colour.red()
            emoji = ":robot:" if color_code == 0 else ":warning:"

        if embed_title is None:
            embed_title = 'System Message'

        sys_embed = Embed(title=f"{emoji}{embed_title}",
                        description=sys_msg_title,
                        colour=c)
        sys_embed.add_field(name=':information_source:', value=f'```{message}```')
        sys_embed.set_footer(text='Message will self-destruct in 15 seconds!')

        try:
            if destination == 0:
                await interaction.response.send_message(embed=sys_embed, ephemeral=True)
            else:
                await interaction.channel.send(embed=sys_embed, delete_after=15) 
        except Exception as e:
            print(f"system_message error: {e}")

    @staticmethod
    async def system_message_pref(ctx, message: str, color_code, sys_msg_title: str = None,
                                embed_title: str = None, destination: int = 0):
        """
        Custom System Messages for prefix-based commands (ctx).
        """
        # Color filtering
        if isinstance(color_code, Colour):
            c = color_code
            emoji = ":robot:"
        else:
            c = 0x319f6b if color_code == 0 else Colour.red()
            emoji = ":robot:" if color_code == 0 else ":warning:"

        if embed_title is None:
            embed_title = 'System Message'

        sys_embed = Embed(title=f"{emoji}{embed_title}",
                        description=sys_msg_title,
                        colour=c)
        sys_embed.add_field(name=':information_source:', value=f'```{message}```')
        sys_embed.set_footer(text='Message will self-destruct in 15 seconds!')

        try:
            if destination == 0:
                await ctx.author.send(embed=sys_embed, delete_after=15)
            else:
                await ctx.channel.send(embed=sys_embed, delete_after=15)
        except Exception as e:
            print(f"system_message_pref error: {e}")

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
            col = Colour.red()
            destination_txt = f'{tx_type_emoji} Recipient {tx_type_emoji} '
            value_emoji = ":money_with_wings: "

        elif direction == 1:
            title = f':inbox_tray: Incoming {tx_type_emoji} {tx_type.title()} transaction :inbox_tray: '
            col = Colour.green()
            destination_txt = ':postbox: Sender :postbox: '
            value_emoji = ":moneybag: "

        tx_report = Embed(title=title,
                          colour=col,
                          timestamp=datetime.utcnow())
        tx_report.add_field(name=f'{destination_txt}',
                            value=f'```{user}```',
                            inline=False)
        tx_report.add_field(name=':post_office: Guild Origin :post_office: ',
                            value=f'```{ctx.message.guild} ({ctx.message.guild.id})```',
                            inline=False)
        tx_report.add_field(name=':love_letter: Note :love_letter: ',
                            value=f'```{message}```')
        tx_report.add_field(name=f'{value_emoji} Transaction value {value_emoji}',
                            value=f'```{transaction_data["amount"]:.7f} {transaction_data["assetCode"].upper()}\n'
                                  f'(${transaction_data["conversion"]})```',
                            inline=False)
        if transaction_data["conversion"] != 0:
            tx_report.add_field(name=':currency_exchange: Conversion Rate :currency_exchange: ',
                                value=f'${transaction_data["conversionRate"]:.4f}/{transaction_data["assetCode"].upper()}',
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
    async def deposit_notification_message(recipient: User, tx_details: dict):

        sys_embed = Embed(title=":inbox_tray: __Deposit Processed__ :inbox_tray: ",
                          description=f'Deposit processed successfully!',
                          colour=Colour.dark_purple(),
                          timestamp=datetime.utcnow())
        sys_embed.add_field(name=':map: From :map: ',
                            value=f'{tx_details["source_account"]}', inline=False)
        sys_embed.add_field(name=CONST_HASH_STR,
                            value=f'{tx_details["hash"]}',
                            inline=False)
        sys_embed.add_field(name=f':gem: Asset :gem: ',
                            value=f'{tx_details["asset_type"]["code"]}')
        sys_embed.add_field(name=":moneybag: Amount :moneybag: ",
                            value=f"{int(tx_details['asset_type']['amount']) / 10000000:9.7f}",
                            inline=False)
        try:
            await recipient.send(embed=sys_embed)
        except Exception as e:
            print(e)

    @staticmethod
    async def withdrawal_notify(interaction, withdrawal_data: dict, fee, memo=None):
        notify = Embed(title=":outbox_tray: Withdrawal Notification :outbox_tray:",
                       description=f'Withdrawal Successfully processed',
                       timestamp=datetime.utcnow(),
                       colour=Colour.green())

        notify.add_field(name=":calendar: Time of withdrawal :calendar: ",
                         value=str(datetime.utcnow()),
                         inline=False)
        notify.add_field(name=':map: Destination :map: ',
                         value=f'```{withdrawal_data["destination"]}```',
                         inline=False)
        notify.add_field(name=':pencil: MEMO :pencil:',
                         value=f'```{memo}```',
                         inline=False)
        notify.add_field(name=CONST_HASH_STR,
                         value=f'`{withdrawal_data["hash"]}`',
                         inline=False)
        notify.add_field(name=':receipt: Withdrawal asset details :receipt: ',
                         value=f'`{round(withdrawal_data["amount"] / 10000000, 7):.7f} {withdrawal_data["asset"]}`',
                         inline=False)
        notify.add_field(name=':money_mouth: Crypto Link Fee charged :money_mouth: ',
                         value=f'`{fee}`',
                         inline=False)
        notify.add_field(name=':sunrise: Horizon Access Link :sunrise: ',
                         value=f"[Complete Details]({withdrawal_data['explorer']})",
                         inline=False)
        try:
            await interaction.user.send_message(embed=notify)

        except Exception:
            print(Fore.RED + f'Can not send deposit notidfication to user')

    @staticmethod
    async def withdrawal_notification_channel(interaction, channel, withdrawal_data):
        # create withdrawal notification for channel
        notify = Embed(title='Stellar Withdrawal Notification',
                       description='Withdrawal has been processed',
                       colour=Colour.gold())
        if isinstance(interaction.channel, TextChannel):
            notify.add_field(name='Origin',
                             value=f'{interaction.guild} ID; {interaction.guild.id}',
                             inline=False)
        else:
            notify.add_field(name='Origin',
                             value=f'DM with bot',
                             inline=False)
        notify.add_field(name='User details',
                         value=f'{interaction.user} \nID; {interaction.user.id}',
                         inline=False)
        notify.add_field(name='Withdrawal details',
                         value=f'Time: {withdrawal_data["time"]}\n'
                               f'Destination: {withdrawal_data["destination"]}\n'
                               f'Amount: {round(withdrawal_data["amount"] / 10000000, 7)} {withdrawal_data["asset"]}',
                         inline=False)
        await channel.send(embed=notify)

    @staticmethod
    async def cl_staff_incoming_funds_notification(sys_channel: TextChannel, incoming_fees: str):
        notify = Embed(title='Bot Stellar Wallet Activity',
                       description='Bot Wallet has been credited because user '
                                   'has initiated on-chain withdrawal',
                       color=Colour.blurple())
        notify.add_field(name='Value',
                         value=f'{incoming_fees}')
        await sys_channel.send(embed=notify)

    @staticmethod
    async def user_role_purchase_msg(ctx, role: Role, role_details: dict):
        # # Send notification to user
        # role_embed = Embed(title=':man_juggling: Congratulations on '
        #                          'obtaining the role',
        #                    description='You have received this notification because you have successfully '
        #                                'purchased role on the community. Please see details below.',
        #                    colour=Colour.blue())
        # role_embed.set_thumbnail(url=ctx.message.guild.icon_url)
        # role_embed.add_field(name=':convenience_store: Community :convenience_store:',
        #                      value=f'```{ctx.message.guild}  \n'
        #                            f'ID:{ctx.message.guild.id}```',
        #                      inline=False)
        # role_embed.add_field(name=':japanese_ogre: Role: :japanese_ogre: ',
        #                      value=f'```Name:{role.name}  \nID:{role.id}```',
        #                      inline=False)
        # role_embed.add_field(name=f':calendar: Role Purchase Date :calendar: ',
        #                      value=f'```{role_details["roleStart"]}```')
        # role_embed.add_field(name=':timer: Role Expiration :timer: ',
        #                      value=f'```{role_details["roleEnd"]} (in: {role_details["roleLeft"]})```',
        #                      inline=False)
        # role_embed.add_field(name=':money_with_wings: Payment Slip :money_with_wings: ',
        #                      value=f'```Fiat:{role_details["dollarValue"]} $ \n'
        #                            f'Crypto: {role_details["roleRounded"]} XLM\n'
        #                            f'Rate: {role_details["usdRate"]} / 1 XLM```',
        #                      inline=False)
        try:
            await ctx.channel.send(content=f'{ctx.message.guild.owner.mention} {ctx.author.mention}'
                                          f' you have successfully purchased membership {role} in value of '
                                           f'{role_details["roleRounded"]} XLM (${role_details["dollarValue"]}). '
                                          f'It will expire on {role_details["roleEnd"]} (in: {role_details["roleLeft"]})')
        except nextcord.Forbidden as e:
            print(Fore.RED + f'{e}')
        # try:
        #     await ctx.author.send(embed=role_embed)
        # except Exception as e:
        #     print(e)
        #     await ctx.channel.send(embed=role_embed, delete_after=10)

    @staticmethod
    async def guild_owner_role_purchase_msg(ctx, role: Role, role_details: dict):
        incoming_funds = Embed(title=':convenience_store:__Incoming funds to corporate '
                                     'wallet___:convenience_store:',
                               description=f'Role has been purchased on your community '
                                           f'at __{role_details["roleStart"]}__.',
                               colour=Colour.green())

        incoming_funds.add_field(name=':japanese_ogre: Role Purchased :japanese_ogre: ',
                                 value=f"```Name: {role.name}\n"
                                       f"Id: {role.id}```",
                                 inline=False)

        incoming_funds.add_field(name=':money_with_wings: Role Value :money_with_wings: ',
                                 value=f'```Fiat: ${role_details["dollarValue"]}\n'
                                       f'Crypto: {role_details["roleRounded"]} XLM\n'
                                       f'Rate: {role_details["usdRate"]} / 1 XLM```',
                                 inline=False)
        incoming_funds.add_field(name=':cowboy: User Details :cowboy: ',
                                 value=f"```User: {ctx.message.author}\n"
                                       f"Id: {ctx.message.author.id}```",
                                 inline=False)

        incoming_funds.add_field(name=':clipboard: Role Duration Details :clipboard:  ',
                                 value=f'```{role_details["roleDetails"]}```',
                                 inline=False)

        await ctx.message.guild.owner.send(embed=incoming_funds)

    @staticmethod
    async def wallet_overall_stats(ctx, utc_now, transaction_stats: dict):
        tx_stats = Embed(title='__Global Account Statistics__',
                         timestamp=utc_now,
                         colour=Colour.blue())
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
    async def stellar_wallet_overall(interaction, coin_stats: dict, utc_now):

        try:
            bridges = coin_stats['bridges']
        except KeyError:
            bridges = 0

        building_bridges = Embed(title=f':construction_site:  Building Bridges :construction_site:',
                                 description="Your Input on bridging the Stellar Network with Discord "
                                             "Users through Crypto Link.",
                                 colour=Colour.gold(),
                                 timestamp=utc_now)
        building_bridges.add_field(name=f':bridge_at_night: Created Bridges :bridge_at_night: ',
                                   value=f'```{int(bridges)}```')
        await interaction.user.send(embed=building_bridges)

        for k, v in coin_stats.items():
            if k in ["xlm"]:
                coin_stats = Embed(title=f'{k.upper()} wallet statistics',
                                   description=f':bar_chart: ***__Statistical Data on Stellar Lumen Discord Wallet__*** '
                                               f':bar_chart:',
                                   colour=Colour.light_grey(),
                                   timestamp=utc_now)
                coin_stats.add_field(name=f':inbox_tray: Total Deposits :inbox_tray:',
                                     value=f'Deposited ***{v["depositsCount"]}*** with total '
                                           f'***{v["totalDeposited"]}*** ')
                coin_stats.add_field(name=f'\u200b',
                                     value='\u200b')
                coin_stats.add_field(name=f':outbox_tray: Total Withdrawals :outbox_tray: ',
                                     value=f'Withdrawn ***{v["withdrawalsCount"]}*** withdrawals with '
                                           f'total ***{v["totalWithdrawn"]}*** ')
                coin_stats.add_field(name=f':family_man_woman_boy: Public Tx :family_man_woman_boy:',
                                     value=f':incoming_envelope: `{v["publicTxSendCount"]}`\n'
                                           f':money_with_wings: `{(int(v["publicSent"] * (10 ** 7))) / (10 ** 7):.7f}`\n'
                                           f':envelope_with_arrow: `{v["publicTxReceivedCount"]}`\n'
                                           f':money_mouth: `{(int(v["publicReceived"] * (10 ** 7))) / (10 ** 7):.7f}`')
                coin_stats.add_field(name=f':detective: Private Tx :detective:',
                                     value=f':incoming_envelope: `{v["privateTxSendCount"]}`\n'
                                           f':money_with_wings: `{(int(v["privateSent"] * (10 ** 7))) / (10 ** 7):.7f}`\n'
                                           f':envelope_with_arrow: `{v["privateTxReceivedCount"]}`\n'
                                           f':money_mouth: `{(int(v["privateReceived"] * (10 ** 7))) / (10 ** 7):.7f}` ')
                coin_stats.add_field(name=f':convenience_store: Merchant purchases :convenience_store: ',
                                     value=f':man_juggling:` `{v["roleTxCount"]}`\n'
                                           f':money_with_wings: `{(int(v["spentOnRoles"] * (10 ** 7))) / (10 ** 7): .7f}`\n',

                                     inline=False)
                await interaction.user.send(embed=coin_stats)

    async def explorer_messages(self, applied_channels: list, message: str):
        """
        Transactin reports to all explorer applied channels
        """

        for explorer_channel in applied_channels:
            if explorer_channel is not None:
                await explorer_channel.send(message)

    async def transaction_report_to_channel(self, ctx, message: str, tx_type: str):
        """
        Discord Transaction report to the channel
        """
        msg_streamed = self.filter_message(message=message, tx_type=tx_type)
        await ctx.channel.send(content=msg_streamed)
        # await ctx.channel.send(content=msg_streamed, delete_after=360)

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
        :return: nextcord.Embed
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
