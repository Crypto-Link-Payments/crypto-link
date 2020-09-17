![banner](../img/image0.png)

Crypto Link, Discord bot which allows for instant peer to peer (P2P) transactions, payments and Discord community 
monetization with the help of integrated Merchant System built on top of Stellar Lumen cryptocurrency.
Discord users can access their wallet through any community which has integrated Crypto Link in their daily operations.

Additional basic information on how Crypto Link is designed can be obtained [here](DESIGN.md).


### ![banner](../img/emojiLumen.png) What is Stellar and Lumen (XLM) ![banner](../img/emojiLumen.png)

Stellar is an open source, decentralized protocol for digital currency to fiat money transfers which allows 
cross-border transactions between any pair of currencies. The Stellar protocol is supported by a 501(c)3 nonprofit, 
the Stellar Development Foundation.

__More on Stellar, Foundation and its native cryptocurrency__:<br />
[Stellar](https://www.stellar.org/) <br />
[Stellar Foundation](https://www.stellar.org/foundation) <br />
[Stellar Lumnes](https://www.stellar.org/lumens) <br />



## Onboard Crypto Link to Discord 
If you are Discord community owner or you have administrator rights, you can import Crypto Link simply by clicking bellow 
to invite link. Once bot will join your community, Crypto Link role will be automatically created with all required
permissions for Crypto Link to operate. 

### Required permissions for bot to integrate

### As Discord User

Head to one of the Communities where Crypto-Link is present and execute 
```text
!register
```
Once you receive successful report to DM on registration you can proceed with:
```text
!wallet      --> Instructions on all available commands to operate with your personal wallet
```

#### Making P2P (Peer To Peer) transaction

Function Structure

```text
!send <currency symbol> <amount> <@discord.User>

Note: if transactions successful both sender and recipient will receive payment slip. 
```

example for Stellar Lumen:
```text
!send xlm <amount> <@discord.User>  # Sends N amount of XLM to targeted user
```

#### Making Discord Withdrawals and Deposits

##### Deposits
```text
!wallet deposit  # Returns instructions on how to deposit currency to Discord
```

##### Withdrawals
```text
!withdraw  # Returns Instructions on how to withdraw from Discord to your personal wallet
```

### As Discord Guild Owner 

#### Invite the bot
Bot requires following Discord Permissions to operate optimally
```text
# Read Message
# Send Message
# Send TTS Message
# Manage Message  --> Bot deletes transaction reports after a while so channels are not spammed
# Embed Links
# Attach Files
# Read Message History
# Use External Emojis 
# Add Reactions
```

:arrow_down: Invitation Link :arrow_down: 

[Bot Invite Link](https://discord.com/oauth2/authorize?client_id=706806251321032726&scope=bot&permissions=392256)

```text
Note:  All required permission are already calculated in invite link so Crypto Link
role will be automatically created. In order to get started on a channel just
assign role to specific channel where you want Crypto Link to be present.
```

#### Merchant system and corporate wallet
Merchant system allows Guild Owners to monetize and create time oriented roles (Time-Bombed).
Crypto Link, automatically scans for purchases, appends required role to user which made a purchase,
transfers money to Guild's account, as well as monitor for expiration. Ones Expired time checkpoint
is met, it will automatically remove the role from the user. 

More on merchant system, its use cases, and set up procedure can be found [here](MERCHANTCOMMANDS.md).

Instructions to operate with corporate account can be found [here](CORPORATEACCOUNTMANAGEMENT.md)


## Additional and Specific Material
- [Available Cryptocurrencies and fees on Crypto Link System](COINLIMITS.md)
- [Bot Set up functions Only LPI Staff](STAFFCOMMANDS.md)
- [Help Commands](HELPCMDS.md)
- [Dealing with user accounts and making P2P payments](COMMANDS.md)
- [Merchant System Only for Community owners](MERCHANTCOMMANDS.md)
- [Command map and help categories](COMMANDMAP.md)]
