![banner](../img/image0.png)
![stellar](https://img.shields.io/badge/Powered%20by-Stellar&%20Lumen-brightgreen?style=plastic) 
![discord](https://img.shields.io/badge/Platform-Discord-blue?style=plastic&?style=plastic)
![Issues](https://img.shields.io/github/issues/launch-pad-investments/crypto-link?style=plastic)
![Forks](https://img.shields.io/github/forks/launch-pad-investments/crypto-link?style=plastic)
![Stars](https://img.shields.io/github/stars/launch-pad-investments/crypto-link?style=plastic)
![License](https://img.shields.io/github/license/launch-pad-investments/crypto-link?style=plastic)
![Language](https://img.shields.io/badge/Python-v3.8-yellowgreen?style=plastic)

Crypto Link, Discord bot which allows for instant peer to peer (P2P) transactions, payments and Discord community 
monetization with the help of integrated Merchant System built on top of Stellar Lumen cryptocurrency.
Discord users can access their wallet through any community which has integrated Crypto Link in their daily operations.

### ![banner](../img/emojiLumen.png) What is Stellar and Lumen (XLM) ![banner](../img/emojiLumen.png)

Stellar is an open source, decentralized protocol for digital currency to fiat money transfers which allows 
cross-border transactions between any pair of currencies. The Stellar protocol is supported by a 501(c)3 nonprofit, 
the Stellar Development Foundation.

__More on Stellar, Foundation and its native cryptocurrency__:<br />
[Stellar](https://www.stellar.org/) <br />
[Stellar Foundation](https://www.stellar.org/foundation) <br />
[Stellar Lumnes](https://www.stellar.org/lumens) <br />

## :construction: Constructs of Crypto Link :construction:
Crypto Link user experience is designed with peer-to-peer and merchant-consumer perspective in mind

### Peer to Peer perspective
Crypto Link allows users to execute instant peer to peer transactions with the help of XLM. Once transaction is
successfully processed, user experience is further expanded, with transactions reports





Additional basic information on how Crypto Link is designed can be obtained [here](DESIGN.md).

## :hammer: Integration of Crypto Link to Discord :hammer: 
Monetizing guild community is instant and straight-forward. No programming skills required, just basic knowledge on how
Discord operate from user and owner perspective. If you are familiar with Discord than simply click [here](https://discord.com/oauth2/authorize?client_id=706806251321032726&scope=bot&permissions=1342700624&response_type=code)
to get invitation. Once Crypto Link joins community required role with permissions will be automatically created. 

### Required permissions for Crypto Link to operate optimally

* ***Manage Roles*** --> Required for Merchant System to operate optimally
* ***Manage Emojis*** --> Eventually custom emojis will be integrated
* ***Read, Send Messages*** --> Informing users on transactions and activities (not marketing!)
* ***Manage Messages*** --> Tx public reports are deleted after a while to keep channels clean
* ***Attach Files*** --> PDF reports on account statement and other infographics to be integrated
* ***Read Message History*** --> Required to read own  messages from the past for deletion 
* ***Add Reaction*** --> For use with special transactions 
* ***Mentions*** --> Transactions done by the role 
* ***Use of external emojis*** --> Custom emojis wil be integrated and cross community emojis

### After Crypto Link Joins 
Assign newly created role Crypto Link to the channels of your community where you would like that it operates and 
listens for commands. 


## :joystick: Commands to operate with Crypto Link :joystick:
Command to which Crypto Link listens to can be broken down into multiple areas. 

Crypto link listens to following prefixes:
```text
!<command> <subcommands>
or
@CryptoLink <command> <subcommands>
```
### :sos: Helper menu :sos:
In order to ease access to Discord users we have provided general command where all functions are explained.
By executing command bellow either on the public channel of the community or direct messaging the bot system
will guide you through all available areas

```text
!help
```

All available commands for ***help*** category are available [here](HELPCMDS.md)


## :runner: Quick start guide :runner:

### :boy: As Discord User :boy:

Head to one of the Communities where Crypto-Link is present and execute 
```text
!register
```
Once you receive successful report to DM on registration you can proceed with:
```text
!wallet      --> Instructions on all available commands to operate with your personal wallet
```

#### :dollar: Making P2P (Peer To Peer) transaction :dollar:

Function Structure

```text
!send <currency symbol> <amount> <@discord.User>

Note: if transactions successful both sender and recipient will receive payment slip. 
```

example for Stellar Lumen:
```text
!send xlm <amount> <@discord.User>  # Sends N amount of XLM to targeted user
```

#### :moneybag: Making Discord Withdrawals and Deposits :moneybag:

##### :incoming_envelope: Deposits :incoming_envelope:
```text
!wallet deposit  # Returns instructions on how to deposit currency to Discord
```

##### :outbox_tray: Withdrawals:outbox_tray:
```text
!withdraw  # Returns Instructions on how to withdraw from Discord to your personal wallet
```

### :crown: As Discord Guild Owner :crown:

#### :currency_exchange: Merchant system and corporate wallet :currency_exchange:
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
