"""
COG: Dealing with automatic messages to Discord Community and single users.
"""

import os
import sys

from colorama import Fore
from discord import Embed, Colour
from discord.ext import commands
from discord.errors import HTTPException
from datetime import datetime
import traceback
import json
from cogs.utils.systemMessaages import CustomMessages

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

custom_messages = CustomMessages()


class AutoFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot_channels = bot.backoffice.auto_messaging_channels
        self.bot = bot
        self.animus_id = bot.backoffice.creator_id
        self.command_string = bot.get_command_str()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        """
        Global error for on command error
        """
        try:
            await ctx.message.delete()
        except Exception:
            pass

        if isinstance(exception, commands.CommandNotFound):
            title = '__Command Error__'
            message = f'Command `{ctx.message.content}` is not implemented/active yet or it does not exist! Please' \
                      f'type `{self.command_string}help` to check available commands.'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)
        elif isinstance(exception, commands.CommandOnCooldown):
            message = f'`{exception}`. In order to prevent abuse and unwanted delays, we have implemented cool down ' \
                      f' into various commands. Thank you for your understanding.'
            await custom_messages.system_message(ctx=ctx, color_code=Colour.blue(), message=message, destination=0,
                                                 sys_msg_title=':sweat_drops: Cool-Down :sweat_drops: ')

        elif isinstance(exception, commands.MissingRequiredArgument):
            await custom_messages.system_message(ctx=ctx, color_code=Colour.orange(), message=f'{exception}',
                                                 destination=0,
                                                 sys_msg_title=':sweat_drops: Missing Required Argument :sweat_drops: ')
        elif isinstance(exception, HTTPException):
            title = 'Discord API Error'
            message = f'We could not process your command due to the connection error with Discord API server. ' \
                      f'Please try again later'
            await custom_messages.system_message(ctx=ctx, color_code=1, message=message, destination=1,
                                                 sys_msg_title=title)
        else:
            if isinstance(exception, commands.CheckFailure):
                print("Check has failed")
            else:
                bug_channel = self.bot.get_channel(id=int(self.bot_channels["bug"]))

                animus = await self.bot.fetch_user(user_id=int(self.animus_id))
                bug_info = Embed(title=f':new: :bug: :warning: ',
                                 description='New command error found',
                                 colour=Colour.red(),
                                 timestamp=datetime.utcnow())
                bug_info.add_field(name=f'Command Author',
                                   value=f'{ctx.message.author}')
                bug_info.add_field(name=f'Channel',
                                   value=ctx.message.channel)
                bug_info.add_field(name=f':joystick: Command Executed :joystick:',
                                   value=f'```{ctx.message.content}```',
                                   inline=False)
                bug_info.add_field(name=f':interrobang: Error Details :interrobang: ',
                                   value=f'```{exception}```',
                                   inline=False)

                await bug_channel.send(embed=bug_info, content=f"{animus.mention}")

                stack_trace = ''.join(
                    traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
                await bug_channel.send(content=stack_trace)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass

    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     """
    #     When member joins a message will be sent to newly joined user
    #     :param member:
    #     :return:
    #     """
    #     if not member.bot:
    #         join_info = Embed(title='__Crypto Link System Message__',
    #                           colour=Colour.green())
    #         join_info.add_field(name="Welcome!",
    #                             value=f"Welcome to the {member.guild}, This discord is powered by "
    #                                   f" {self.bot.user.name}, where you can make payments,"
    #                                   f" donations, or tips over Discord on Stellar Crypto Currency Chain. "
    #                                   f"System Allows as well to purchase guild"
    #                                   f" roles so contact owner to find more info."
    #                                   f"and other discord users. To get started use command ***{self.command_string}"
    #                                   f"help*** or ***{self.command_string}help get_started***.",
    #                             inline=False)
    #         join_info.add_field(name="Terms Of Service",
    #                             value="By accessing or using any part of this bot, "
    #                                   "you agree to be bound by these Terms of Service. "
    #                                   "If you do not agree to all the terms and conditions "
    #                                   "of this agreement, then you may not use any services "
    #                                   "of this bot. These Terms of Service apply to all users of the bot,"
    #                                   " including without limitation users who are visitors, browsers, "
    #                                   "vendors, customers, merchants, and/ or contributors of content. "
    #                                   "We do not keep your information or sell it all information gathered "
    #                                   "is used for the creation of the wallet to help facilitate your own "
    #                                   "ability to trade, swap, or pay users or organisations for their"
    #                                   " goods and or services.",
    #                             inline=False)
    #
    #         join_info.add_field(name="Disclaimer",
    #                             value="We reserve the right to update, change or replace any part of these "
    #                                   "Terms of Service by posting updates and/or changes to"
    #                                   " this message. It is your responsibility to check this bot"
    #                                   " periodically for changes. Your continued use of or access "
    #                                   "to the bot following the posting of any changes constitutes"
    #                                   " acceptance of those changes. You agree that the use of this bot "
    #                                   "is at your own risk. In no event should Crypto Link "
    #                                   "discord server or any of its members including the bot creator "
    #                                   "be liable for any direct or indirect trading losses caused by this "
    #                                   "bot and its services and features.")
    #         try:
    #             await member.send(embed=join_info)
    #         except commands.NoPrivateMessage:
    #             pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Clean up process once member leaves the guild
        """

        if not member.bot:
            if self.bot.backoffice.account_mng.check_user_existence(user_id=member.id):
                print(Fore.LIGHTYELLOW_EX + f'{member} left {member.guild}... Notifying him on funds')

                warning_embed = Embed(title=f':warning:  __{self.bot.user}__ :warning: ',
                                      description='This is automatic notification from Crypto Link Payment system bot',
                                      colour=Colour.dark_orange())
                warning_embed.add_field(name='Notification',
                                        value=f'You have left the {member.guild} where {self.bot.user} payment system '
                                              f'is present. Hope you did not have any funds in your wallet.'
                                              ' Funds can be accessed from any community where the system is present.',
                                        inline=False)
                await member.send(embed=warning_embed)
            else:
                print(Fore.LIGHTYELLOW_EX + f'{member} left {member.guild}... Not Registered')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """
        Triggering message to system channel when bot joins new guild
        """
        print(Fore.LIGHTMAGENTA_EX + f'{self.bot.user} joined {guild} ')

        new_guild = Embed(title='__NEW GUILD!!!!__',
                          description=f'{self.bot.user} has joined new guild',
                          colour=Colour.green())
        new_guild.add_field(name='Guild name and id:',
                            value=f'```{guild} {guild.id}```',
                            inline=False)
        new_guild.add_field(name='Guild created:',
                            value=f'```{guild.created_at}```',
                            inline=False)
        new_guild.add_field(name='Guild Owner:',
                            value=f'```{guild.owner} {guild.owner_id}```',
                            inline=False)
        new_guild.add_field(name='Guild Region:',
                            value=f'```{guild.region}```',
                            inline=False)
        new_guild.add_field(name='Member Count',
                            value=f'```{guild.member_count}```',
                            inline=False)

        animus = await self.bot.fetch_user(user_id=int(self.animus_id))

        channel_id = self.bot_channels["sys"]
        dest = self.bot.get_channel(id=int(channel_id))
        await dest.send(embed=new_guild, content=f'{animus.mention}')

        # Register default prefix
        self.bot.backoffice.guild_profiles.set_guild_prefix(guild_id=guild.id, prefix="!")

        print(
            Fore.LIGHTYELLOW_EX + '===================================\nGlobal Stats Updated after join...\n========'
                                  '===========================')
        guilds = await self.bot.fetch_guilds(limit=150).flatten()
        reach = len(self.bot.users)
        print(Fore.LIGHTGREEN_EX + f'Integrated into: {len(guilds)} guilds')
        print(Fore.LIGHTGREEN_EX + f'Member reach: {reach} members')
        print(Fore.LIGHTYELLOW_EX + '===================================')

        if not self.bot.guild_profiles.check_guild_registration_stats(guild_id=guild.id):
            new_guild = {
                "guildId": guild.id,
                "guildName": f'{guild}',
                "explorerSettings": {"channelId": int(0)},
                "txFees": {"xlmFeeValue": int(0)},
                "registeredUsers": 0,
                "xlm": {"volume": float(0.0),
                        "txCount": int(0),
                        "privateCount": int(0),
                        "publicCount": int(0),
                        "roleTxCount": int(0),
                        "emojiTxCount": int(0),
                        "multiTxCount": int(0)}
            }
            await self.bot.guild_profiles.register_guild(guild_data=new_guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """
        Triggered when bot is removed from guild and system message is sent to channel on removal
        """
        print(Fore.LIGHTMAGENTA_EX + f'{self.bot.user} left {guild} ')
        removed_guild = Embed(title='__GUILD REMOVED!!!!__',
                              description=f'{self.bot.user} has left guild',
                              colour=Colour.red())
        removed_guild.add_field(name='Guild name and id:',
                                value=f'```{guild} {guild.id}```',
                                inline=False)
        removed_guild.add_field(name='Guild Owner:',
                                value=f'{guild.owner} {guild.owner_id}',
                                inline=False)
        removed_guild.add_field(name='Member Count',
                                value=f'```{guild.member_count}```',
                                inline=False)
        animus = await self.bot.fetch_user(user_id=int(self.animus_id))

        dest = self.bot.get_channel(id=int(self.bot_channels["sys"]))

        await dest.send(embed=removed_guild, content=f'{animus.mention}')

        print(
            Fore.LIGHTYELLOW_EX + '===================================\nGlobal Stats Updated'
                                  ' after remove...\n===================================')
        guilds = await self.bot.fetch_guilds(limit=150).flatten()
        reach = len(self.bot.users)
        print(Fore.LIGHTGREEN_EX + f'Integrated into: {len(guilds)} guilds')
        print(Fore.LIGHTGREEN_EX + f'Member reach: {reach} members')
        print(Fore.LIGHTYELLOW_EX + '===================================')


def setup(bot):
    bot.add_cog(AutoFunctions(bot))
