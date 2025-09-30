from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
import io

from nextcord import Colour, Role, Embed
import nextcord
from datetime import datetime, timezone 
from nextcord.ext import commands
from pycoingecko import CoinGeckoAPI
from nextcord import Embed, Colour, slash_command, Interaction, Role

from typing import Optional, Tuple
from utils.customCogChecks import guild_has_merchant
from cogs.utils.systemMessaages import CustomMessages
import nextcord
from nextcord import (
    AllowedMentions,
    ButtonStyle,
    Colour,
    Embed,
    Interaction,
    Role,
    ui,
)

from urllib.parse import urlencode
from nextcord.ui import View, button, Button
from utils.customCogChecks import has_wallet_inter_check, is_public_channel

try:
    import pyqrcode  # pip install qrcode[pil]
    HAS_QR = True
except Exception:
    HAS_QR = False

custom_messages = CustomMessages()
gecko = CoinGeckoAPI()
PAY_TRAMPOLINE_BASE: Optional[str] = None 
PAY_LINK_BASE: Optional[str] = None  
CONST_STELLAR_EMOJI = '<:stelaremoji:684676687425961994>'
CONST_MERCHANT_ROLE_ERROR = "__Merchant System Role Error__"
CONST_MERCHANT_PURCHASE_ERROR = ":warning: __Merchant System Purchase Error__:warning: "
ORDER_TTL_MINUTES = 60  

def _safe(s: str) -> str:
    """Avoid accidental mentions; keep backticks intact."""
    return s.replace("@", "@\u200b").replace("#", "#\u200b")

def _fmt_xlm(x: float) -> str:
    """Always 7 decimals for XLM (Stellar base precision)."""
    return f"{x:.7f}"

def _stellar_pay_uri(dest: str, amount_xlm: float, memo_text: str) -> str:
    """SEP-7 deep link (used in QR only; Discord buttons can't use web+stellar)."""
    return (
        f"web+stellar:pay?destination={dest}"
        f"&amount={_fmt_xlm(amount_xlm)}"
        f"&memo={memo_text}"
        f"&memo_type=MEMO_TEXT"
    )

def _build_https_trampoline(base_url: Optional[str], dest: str, amount_xlm: float, memo_text: str) -> Optional[str]:
    """If you have an HTTPS landing page, build a safe link for a Discord button."""
    if not base_url:
        return None
    qs = urlencode({
        "destination": dest,
        "amount": _fmt_xlm(amount_xlm),
        "memo": memo_text,
        "memo_type": "MEMO_TEXT",
    })
    return f"{base_url}?{qs}"


class OrderCopyView(View):
    def __init__(
        self,
        *,
        address: str,
        memo_text: str,
        amount_xlm: float,
        trampoline_https_url: Optional[str] = None,
        invoker_id: Optional[int] = None,
        timeout: Optional[float] = 600,
    ):
        super().__init__(timeout=timeout)
        self.address = address
        self.memo_text = memo_text
        self.amount_xlm = amount_xlm
        self.invoker_id = invoker_id

        if trampoline_https_url and trampoline_https_url.startswith(("http://", "https://", "discord://")):
            self.add_item(
                Button(
                    label="Open Payment Page",
                    style=ButtonStyle.link,
                    url=trampoline_https_url,
                    row=0,
                )
            )

    async def interaction_check(self, interaction: Interaction) -> bool:
        return True if self.invoker_id is None else (interaction.user.id == self.invoker_id)

    @button(label="Copy Address", style=ButtonStyle.primary, emoji="📋", row=1)
    async def copy_address(self, _, interaction: Interaction):
        await interaction.response.send_message(
            content=f"**Public Address**\n`{_safe(self.address)}`\n\n_long-press to copy_",
            ephemeral=True,
            allowed_mentions=AllowedMentions.none(),
        )

    @button(label="Copy MEMO", style=ButtonStyle.primary, emoji="🧭", row=1)
    async def copy_memo(self, _, interaction: Interaction):
        await interaction.response.send_message(
            content=f"**MEMO**\n`{_safe(self.memo_text)}`\n\n_long-press to copy_",
            ephemeral=True,
            allowed_mentions=AllowedMentions.none(),
        )

    @button(label="Copy Amount", style=ButtonStyle.secondary, emoji="💵", row=1)
    async def copy_amount(self, _, interaction: Interaction):
        await interaction.response.send_message(
            content=f"**Amount (XLM)**\n`{_fmt_xlm(self.amount_xlm)}`\n\n_long-press to copy_",
            ephemeral=True,
            allowed_mentions=AllowedMentions.none(),
        )

    @button(label="Copy Both", style=ButtonStyle.secondary, emoji="📋", row=2)
    async def copy_both(self, _, interaction: Interaction):
        await interaction.response.send_message(
            content=(
                f"**Address + MEMO**\n"
                f"Address:\n`{_safe(self.address)}`\n\n"
                f"MEMO:\n`{_safe(self.memo_text)}`\n\n"
                "_long-press to copy_"
            ),
            ephemeral=True,
            allowed_mentions=AllowedMentions.none(),
        )

def _make_payment_embed(
    interaction: Interaction,
    role: Role,
    order: dict,
    amount_xlm: float,
    amount_usd: float,
    dest_address: str,
    *,
    trampoline_base_https: Optional[str] = None,
) -> Tuple[Embed, Optional[nextcord.File], OrderCopyView]:
    ts_ms = int(order["purchaseRequest"])  
    ts = ts_ms // 1000
    created_dt = datetime.fromtimestamp(ts, tz=timezone.utc)

    status_map = {0: "Awaiting your payment", 1: "Processed"}
    status = status_map.get(order.get("status", 0), "Unknown")

    expires_at = created_dt + timedelta(minutes=ORDER_TTL_MINUTES)
    expires_unix = int(expires_at.timestamp())

    e = Embed(
        title="🧾 Order Created",
        description="Here are your order details. Please complete the payment on the Stellar (XLM) network.",
        colour=Colour.blurple(),
    )
    e.add_field(name="🎪 Role", value=f"**{role.name}** (id:{order['roleId']})", inline=False)
    e.add_field(name="💵 Amount", value=f"{_fmt_xlm(amount_xlm)} XLM  (${amount_usd:.2f})", inline=False)
    e.add_field(name="📦 Status", value=status, inline=True)
    e.add_field(name="🕒 Created", value=f"{created_dt.strftime('%Y-%m-%d %H:%M:%S')} UTC • <t:{ts}:R>", inline=True)

    memo_val = order.get("roleReference") or ""
    if memo_val:
        e.add_field(name="🧾 Payment Memo", value=f"`{memo_val}`", inline=False)

    e.add_field(
        name="💳 Payment Instructions",
        value=(
            f"• **Network:** Stellar (XLM)\n"
            f"• **Destination Address:** `{dest_address}`\n"
            f"• **Amount:** {_fmt_xlm(amount_xlm)} XLM  (${amount_usd:.2f})\n"
            f"• **Memo (required):** `{memo_val}`\n"
            f"• **Order valid until:** <t:{expires_unix}:R> (then it may be recalculated)\n\n"
            "⚠️ **Important**\n"
            "• Use the **Stellar (XLM) network**, not another chain.\n"
            "• Include the **memo exactly** as shown, or your payment may not be linked.\n"
            "• Send the **exact amount** to avoid delays."
        ),
        inline=False,
    )
    e.set_footer(text=f"Community: {interaction.guild.name} • User: {interaction.user}")

    # QR using the SEP-7 deep link (wallets can parse it when scanning)
    qr_file: Optional[nextcord.File] = None
    if HAS_QR:
        try:
            sep7_uri = _stellar_pay_uri(dest_address, amount_xlm, memo_val)
            qr = pyqrcode.create(sep7_uri, error='M')
            buf = io.BytesIO()
            qr.png(buf, scale=5)  
            buf.seek(0)
            qr_file = nextcord.File(buf, filename="stellar_payment_qr.png")
            e.set_image(url="attachment://stellar_payment_qr.png")
        except Exception as ex:
            print(f"QR generation failed: {ex}")
            qr_file = None


    https_url = _build_https_trampoline(trampoline_base_https, dest_address, amount_xlm, memo_val)

    view = OrderCopyView(
        address=dest_address,
        memo_text=memo_val,
        amount_xlm=amount_xlm,
        trampoline_https_url=https_url,
        invoker_id=interaction.user.id,  
    )

    return e, qr_file, view

class PayView(ui.View):
    def __init__(self, url: Optional[str], timeout: Optional[float] = 1800):
        super().__init__(timeout=timeout)
        if url and url.startswith(("http://", "https://", "discord://")):
            self.add_item(ui.Button(label="Open Payment Page", style=ButtonStyle.link, url=url))


class ConsumerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backoffice = bot.backoffice
        self.command_string = bot.get_command_str()


    def human_td(self, td: timedelta) -> str:
        """Nicely format a positive timedelta (no microseconds)."""
        total = int(td.total_seconds())
        if total <= 0:
            return "Expired"
        days, rem = divmod(total, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        parts = []
        if days: parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours: parts.append(f"{hours} h")
        if minutes: parts.append(f"{minutes} min")
        if not parts: parts.append(f"{seconds} s")
        return ", ".join(parts)

    @slash_command(name="membership", description="Membership system entry point", dm_permission=False)
    async def membership(self, interaction: Interaction):
        pass  

    @membership.subcommand(name="help", description="Shows available membership commands")
    @has_wallet_inter_check()
    @guild_has_merchant()
    @is_public_channel()
    async def membership_help(self, interaction: Interaction):
        title = ':joystick: __Membership available commands__ :joystick:'
        description = 'Representation of all available commands under ***membership*** category'

        list_of_commands = [
            {"name": f':circus_tent: Available Roles on {interaction.guild.name} :circus_tent:',
             "value": '`/membership roles`'},
            {"name": f':person_juggling: Subscribe for role on community :person_juggling:',
             "value": '`/membership subscribe`'},
            {"name": f':man_mage: List active roles on community:man_mage:',
             "value": '`/membership current`'},
            {"name": f':receipt: List active roles on community :receipt:',
             "value": '`/membership order`'}
        ]

        await custom_messages.embed_builder(
            interaction=interaction,
            title=title,
            description=description,
            data=list_of_commands,
            c=Colour.magenta()
        )

    @membership.subcommand(name="current", description="Review your active memberships")
    @is_public_channel()
    async def current_cmd(self, interaction: Interaction):
        """
        Returns information on current membership details user currently has active
        """
        author = interaction.user.id
        community = interaction.guild.id

        try:
            roles = self.backoffice.merchant_manager.check_user_roles(user_id=author, discord_id=community)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error fetching role data: {e}", ephemeral=True)
            return

        await interaction.response.send_message("📬 I’ll DM you your role details.", ephemeral=True)

        if roles:
            for role in roles:
                value_in_stellar = round(int(role['atomicValue']) / 10000000, 7)
                starting_time = datetime.fromtimestamp(role['start'], tz=timezone.utc)
                ending_time = datetime.fromtimestamp(role['end'], tz=timezone.utc)
                now = datetime.now(timezone.utc)
                remaining = ending_time - now
                remaining_str = self.human_td(remaining)
                dollar_worth = round(int(role['pennies']) / 100, 4)

                role_embed = Embed(
                    title=":person_juggling: Active Role Information :person_juggling:",
                    colour=Colour.magenta()
                )
                role_embed.add_field(name=":circus_tent: Active Role", value=f"***{role['roleName']}*** (id:{int(role['roleId'])})", inline=False)
                role_embed.add_field(name=":calendar: Role Obtained", value=f"{starting_time.strftime('%Y-%m-%d %H:%M:%S')} UTC", inline=False)
                role_embed.add_field(name=":money_with_wings: Role Value", value=f"{value_in_stellar} {CONST_STELLAR_EMOJI} (${dollar_worth})", inline=False)
                role_embed.add_field(name=":stopwatch: Role Expires", value=f"{ending_time.strftime('%Y-%m-%d %H:%M:%S')} UTC", inline=False)
                role_embed.add_field(name=":timer: Time Remaining", value=remaining_str if remaining.total_seconds() > 0 else "Expired, you will loose membership if not re-purchased", inline=False)

                try:
                    await interaction.user.send(embed=role_embed)
                except nextcord.Forbidden:
                    await interaction.followup.send("⚠️ I couldn’t DM you (privacy settings). Here it is:", ephemeral=True)
                    await interaction.followup.send(embed=role_embed, ephemeral=True)

            await interaction.response.send_message("📬 Role details sent to your DM!", ephemeral=True)
        else:
            message = f"You have no active roles on {interaction.guild}, or all of them have expired."
            await custom_messages.system_message(interaction=interaction, color_code=1, message=message, destination=0,
                                                 sys_msg_title=CONST_MERCHANT_ROLE_ERROR)

    @membership.subcommand(name="roles", description="List all available monetized roles on this community")
    @is_public_channel()
    async def roles(self, interaction: Interaction):
        """
        Gets all available monetized roles on the community
        """
        roles = self.backoffice.merchant_manager.get_all_roles_community(community_id=interaction.guild.id)
        title = f':circus_tent: __Available Roles on Community {interaction.guild.name}__ :circus_tent:'
        dollar_xlm = gecko.get_price(ids='stellar', vs_currencies='usd')

        if roles:
            for role in roles:
                value = float(role["pennyValues"] / 100)
                value_in_stellar = value / dollar_xlm['stellar']['usd']
                values = [
                    {"name": ':person_juggling: Role', "value": f'```{role["roleName"]} ID({role["roleId"]})```'},
                    {"name": ':vertical_traffic_light: Status', "value": f'```{role["status"]}```'},
                    {"name": ':dollar: Fiat value', "value": f"```{value:.2f} $```"},
                    {"name": ':currency_exchange: Conversion to crypto', "value": f"```{value_in_stellar:.7f} XLM```"},
                    {"name": ':timer: Role Length',
                    "value": f"```{role['weeks']} week/s \n{role['days']} day/s \n{role['hours']} hour/s \n{role['minutes']} minute/s```"}
                ]
                await custom_messages.embed_builder(
                    interaction=interaction,
                    title=title,
                    description="Role details",
                    destination=1,
                    data=values,
                    c=Colour.magenta()
                )
            # Acknowledge response if not yet sent
            if not interaction.response.is_done():
                await interaction.response.send_message("✅ Role list sent above!", ephemeral=True)
        else:
            message = f"Server {interaction.guild.name} does not have any available roles for purchase at this moment."
            await custom_messages.system_message(
                interaction=interaction,
                color_code=1,
                message=message,
                destination=1,
                sys_msg_title=CONST_MERCHANT_ROLE_ERROR
            )


    @membership.subcommand(name="subscribe", description="Subscribe to a monetized role in the community")
    @is_public_channel()
    @commands.bot_has_permissions(manage_roles=True)
    async def subscribe(self, interaction: Interaction, role: Role, ticker: str = "xlm"):
        """
        Subscribe to service
        """
        user = interaction.user
        guild = interaction.guild
        guild_id = interaction.guild_id

        # User XLM incase the ticker of the currency is not provided
        if not ticker:
            ticker = "xlm"
        else:
            ticker = 'xlm'

        role_details = self.backoffice.merchant_manager.find_role_details(role_id=role.id)  # Get the roles from the system

        # Check if community has activated merchant
        if role_details and role_details['status'] == 'active':
            # Check if user has already applied for the role
            if role.id not in [r.id for r in user.roles]:  # Check if user has not purchased role yet

                # Calculations and conversions
                convert_to_dollar = role_details["pennyValues"] / 100  # Convert to $
                coin_usd_price = gecko.get_price(ids='stellar', vs_currencies='usd')['stellar']['usd']

                # Check if api returned price
                if coin_usd_price:
                    role_value_crypto = float(convert_to_dollar / coin_usd_price)
                    role_value_rounded = round(role_value_crypto, 7)
                    role_value_atomic = int(role_value_rounded * (10 ** 7))

                    # Get users balance
                    balance = self.backoffice.account_mng.get_balance_based_on_ticker(
                        user_id=int(user.id),
                        ticker=ticker)

                    # Check if user has sufficient balance
                    if balance >= role_value_atomic and self.backoffice.merchant_manager.modify_funds_in_community_merchant_wallet(
                            community_id=int(guild_id),
                            amount=int(role_value_atomic),
                            direction=0,
                            wallet_tick=ticker):

                        # Update community wallet
                        if self.backoffice.account_mng.update_user_wallet_balance(discord_id=user.id,
                                                                                  ticker=ticker,
                                                                                  direction=1,
                                                                                  amount=role_value_atomic):

                            # Assign the role to the user
                            await user.add_roles(role, reason='Merchant purchased role given')
                            start = datetime.now(timezone.utc)
                            # get the timedelta from the role description
                            td = timedelta(weeks=role_details['weeks'],
                                           days=role_details['days'],
                                           hours=role_details['hours'],
                                           minutes=role_details['minutes'])

                            # calculate future date
                            end = start + td
                            gap = end - start
                            unix_today = int(start.timestamp())     # Proper UTC-based timestamp
                            unix_future = int(end.timestamp())

                            # make data for store in database
                            purchase_data = {
                                "userId": int(user.id),
                                "userName": str(user),
                                "roleId": int(role.id),
                                "roleName": f'{role.name}',
                                "start": unix_today,
                                "end": unix_future,
                                "currency": ticker,
                                "atomicValue": role_value_atomic,
                                "pennies": int(role_details["pennyValues"]),
                                "communityName": f'{guild}',
                                "communityId": int(guild.id)}

                            # Add active user to database of applied merchant
                            if self.backoffice.merchant_manager.add_user_to_payed_roles(purchase_data=purchase_data):
                                purchase_role_data = {
                                    "roleStart": f"{start} UTC",
                                    "roleEnd": end,
                                    "roleLeft": gap,
                                    "dollarValue": convert_to_dollar,
                                    "roleRounded": role_value_rounded,
                                    "usdRate": coin_usd_price,
                                    "roleDetails": f"weeks: {role_details['weeks']}\n"
                                                   f"days: {role_details['days']}\n"
                                                   f"hours: {role_details['hours']}\n"
                                                   f"minutes: {role_details['minutes']}"
                                }

                                # Send user payment slip info on purchased role
                                emb = custom_messages.user_role_purchase_msg(interaction=interaction, role=role,
                                                                             role_details=purchase_role_data)

                                # Send report to guild oowner that he recieved funds
                                await custom_messages.guild_owner_role_purchase_msg(interaction=interaction, role=role,
                                                                                    role_details=purchase_role_data)

                                user_stats_update = {
                                    f'{ticker}.spentOnRoles': float(role_value_rounded),
                                    f'{ticker}.roleTxCount': int(1)
                                }

                                # Update user purchase stats
                                await self.backoffice.stats_manager.as_update_role_purchase_stats(
                                    user_id=user.id,
                                    merchant_data=user_stats_update)

                                global_merchant_stats = {
                                    'totalSpentInUsd': convert_to_dollar,
                                    'totalSpentInXlm': role_value_rounded
                                }

                                global_ticker_stats = {
                                    "merchantPurchases": 1,
                                    "merchantMoved": role_value_rounded,
                                    "totalTx": 1,
                                    "totalMoved": role_value_rounded
                                }

                                # Update merchant stats of CL
                                await self.backoffice.stats_manager.update_cl_merchant_stats(ticker='xlm',
                                                                                             merchant_stats=global_merchant_stats,
                                                                                             ticker_stats=global_ticker_stats)

                                guild_stats = {
                                    f"{ticker}.roleTxCount": 1,
                                    f"{ticker}.volume": role_value_rounded,
                                    f'{ticker}.txCount': 1

                                }
                                # Update guild stats
                                await self.backoffice.stats_manager.update_guild_stats(guild_id=guild_id,
                                                                                       guild_stats_data=guild_stats)

                                data = {
                                    "overallGained": role_value_rounded,
                                    "rolesObtained": 1
                                }
                                await self.backoffice.guild_profiles.update_stellar_community_wallet_stats(
                                    guild_id=guild_id, data=data)

                                # Send notifcications
                                load_channels = [
                                    self.bot.get_channel(int(chn))
                                    for chn in self.backoffice.guild_profiles.get_all_explorer_applied_channels()
                                ]
                                explorer_msg = (
                                    f":man_juggling: purchased in value {role_value_rounded} {CONST_STELLAR_EMOJI} "
                                    f"(${convert_to_dollar}) on {interaction.guild.name}"
                                )
                                await custom_messages.explorer_messages(applied_channels=load_channels, message=explorer_msg)
                                # inside user_role_purchase_msg
                                await interaction.response.send_message(
                                    content=f"{interaction.guild.owner.mention}, {interaction.user.mention}",
                                    embed=emb
                                )


                        else:
                            await custom_messages.system_message(
                                interaction=interaction,
                                message='Error while trying to deduct funds from user',
                                sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                                color_code=1,
                                destination=1)
                    else:
                        msg = (f'Insufficient balance. You have {balance / 10**7} xlm and need '
                            f'{role_value_crypto} xlm for @{role}')
                        await custom_messages.system_message(
                            interaction=interaction,
                            message=msg,
                            sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                            color_code=1,
                            destination=0)
                else:
                    message = (
                        "Role cannot be purchased at this moment as conversion rates could not be obtained "
                        "from CoinGecko. Please try again later. We apologize for the inconvenience."
                    )
                    await custom_messages.system_message(
                        interaction=interaction,
                        message=message,
                        sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                        color_code=1,
                        destination=0
                    )
            else:
                msg = f'You already own the role ***{role}***. Wait for it to expire before re-purchasing.'
                await custom_messages.system_message(
                    interaction=interaction,
                    message=msg,
                    sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                    color_code=1,
                    destination=0)
        else:
            msg = f'Role {role} is not active or not monetized on {guild}. Contact {guild.owner}.'
            await custom_messages.system_message(
                interaction=interaction,
                message=msg,
                sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                color_code=1,
                destination=1)


    @membership.subcommand(name="order", description="Create order and pay directly")
    @is_public_channel()
    async def order(self, interaction: Interaction, role: Role, ticker: str = "xlm"):

        await interaction.response.send_message("\u200b", ephemeral=True)

        user = interaction.user
        guild = interaction.guild
        guild_id = interaction.guild_id
        ticker = (ticker or "xlm").lower()


        role_details = self.backoffice.merchant_manager.find_role_details(role_id=role.id)
        if not (role_details and role_details.get("status") == "active"):
            await custom_messages.system_message(
                interaction=interaction,
                message=f"Role {role} is not active or not monetized on {guild}. Contact {guild.owner}.",
                sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                color_code=1,
                destination=1,
            )
            return


        if role.id in [r.id for r in user.roles]:
            await custom_messages.system_message(
                interaction=interaction,
                message=f'You already own the role ***{role}***. Wait for it to expire before re-purchasing.',
                sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                color_code=1,
                destination=0,
            )
            return


        convert_to_dollar = float(role_details["pennyValues"]) / 100.0  # USD price
        gecko_data = gecko.get_price(ids="stellar", vs_currencies="usd") or {}
        coin_usd_price = (gecko_data.get("stellar") or {}).get("usd")
        if not coin_usd_price:
            await custom_messages.system_message(
                interaction=interaction,
                message="Couldn’t fetch conversion rates. Try again later.",
                sys_msg_title=CONST_MERCHANT_PURCHASE_ERROR,
                color_code=1,
                destination=0,
            )
            return
        amount_usd = convert_to_dollar
        amount_xlm = amount_usd / float(coin_usd_price)

        order = self.backoffice.merchant_manager.create_merchant_order(
            community_id=guild_id, role_id=role.id, user_id=user.id
        )
        if not order:
            await interaction.followup.send("❌ Failed to create order.", ephemeral=True)
            return


        dest_address = self.backoffice.stellar_wallet.public_key  
        embed, qr_file, view = _make_payment_embed(
            interaction, role, order, amount_xlm, amount_usd, dest_address,
            trampoline_base_https=PAY_TRAMPOLINE_BASE  
        )


        try:
            await interaction.user.send(
                embed=embed,
                file=qr_file,
                view=view,
                allowed_mentions=AllowedMentions.none(),
            )
            await interaction.followup.send("📬 I’ve sent your order details to your DMs.", ephemeral=True)
        except nextcord.Forbidden:
            await interaction.followup.send(
                "⚠️ I couldn’t DM you. Here are your order details:",
                embed=embed,
                file=qr_file,
                view=view,
                ephemeral=True,
                allowed_mentions=AllowedMentions.none(),
            )

def setup(bot):
    bot.add_cog(ConsumerCommands(bot))
