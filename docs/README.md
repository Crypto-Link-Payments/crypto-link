![banner](../img/twitterUpdate.png)

![License](https://img.shields.io/github/license/launch-pad-investments/crypto-link?style=plastic)
![stellar](https://img.shields.io/badge/Powered%20by-Stellar&%20Lumen-brightgreen?style=plastic) 
![discord](https://img.shields.io/badge/Platform-Discord-blue?style=plastic&?style=plastic)
![Issues](https://img.shields.io/github/issues/launch-pad-investments/crypto-link?style=plastic)
![Forks](https://img.shields.io/github/forks/launch-pad-investments/crypto-link?style=plastic)
![Stars](https://img.shields.io/github/stars/launch-pad-investments/crypto-link?style=plastic)
![Language](https://img.shields.io/badge/Python-v3.8-yellowgreen?style=plastic)
![Discord](https://img.shields.io/discord/756132394289070102?label=Discord&logo=discord&style=plastic)
![Last Commit](https://img.shields.io/github/last-commit/launch-pad-investments/crypto-link?logo=github&style=plastic)
![Last Commit](https://img.shields.io/github/contributors/launch-pad-investments/crypto-link?logo=Github&style=plastic)
![Commit activity](https://img.shields.io/github/commit-activity/m/launch-pad-investments/crypto-link?logo=github&style=plastic)
![Code Size](https://img.shields.io/github/languages/code-size/launch-pad-investments/crypto-link?logo=github&style=plastic)
![Repo Size](https://img.shields.io/github/repo-size/launch-pad-investments/crypto-link?logo=github&style=plastic)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/9fd3218417ba4c0db99701ce8aecfd13)](https://www.codacy.com/gh/launch-pad-investments/crypto-link/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=launch-pad-investments/crypto-link&amp;utm_campaign=Badge_Grade)
[![CodeFactor](https://www.codefactor.io/repository/github/launch-pad-investments/crypto-link/badge)](https://www.codefactor.io/repository/github/launch-pad-investments/crypto-link)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](code_of_conduct.md)

Crypto Link, Discord bot which allows for instant peer to peer (P2P) transactions, payments and Discord community 
monetization with the help of integrated Merchant System built on top of Stellar Lumen cryptocurrency.
Discord users can access their wallet through any community which has integrated Crypto Link in their daily operations.

## Code of Conduct
The project is governed by the Launch Pad Investments. By participating, 
you are expected to uphold this code. You can access Code of Conduct details [here](CODE_OF_CONDUCT.md).
Please report unacceptable behavior to the project team at cryptolinkpayments@gmail.com.

## ![banner](../img/emojiLumen.png) What is Stellar and Lumen (XLM) ![banner](../img/emojiLumen.png)

Stellar is an open source, decentralized protocol for digital currency to fiat money transfers which allows 
cross-border transactions between any pair of currencies. The Stellar protocol is supported by a 501(c)3 nonprofit, 
the Stellar Development Foundation.

__More on Stellar, Foundation and its native cryptocurrency__:<br />
[Stellar](https://www.stellar.org/) <br />
[Stellar Foundation](https://www.stellar.org/foundation) <br />
[Stellar Lumnes](https://www.stellar.org/lumens) <br />

## :construction: Crypto Link Use case:construction:
Crypto Link user experience is designed with peer-to-peer and merchant-consumer perspective in mind.

### Peer to Peer perspective
Crypto Link allows users to execute instant peer to peer transactions with the help of XLM. Once transaction is
successfully processed, user experience is further expanded, with transactions reports and conversion rates provided
by [CoinGecko](https://www.coingecko.com/en). 

### Merchant-Consumer perspective
With integration of the Merchant System, Discord guild owners can now monetize their Discord Communities and their roles.
There has been significant rise in communities which offer their members Payed services for limited amount of time. 
To Our knowledge none of the payment solutions on Discord currently provides this opportunity. With Crypto Link Merchant
system owner can deploy timed monetized roles and offer them to their community members. User than uses XLM and personal
wallet to purchase the role, and obtain access to special areas. Merchant System than automatically monitors for role
expiration. With integration guild owners can save a lot of time and resources devoted to purchase handling and monitoring
for expirations. Crypto Link will take care on its own. 

Additional basic information on how Crypto Link is designed can be obtained [here](DESIGN.md).

## :hammer: Integration of Crypto Link to Discord :hammer: 
Monetizing guild community is instant and straight-forward. No programming skills required, just basic knowledge on how
Discord operate from user and owner perspective. 

### :warning: Required permissions for Crypto Link to operate optimally :warning:

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
listens for commands, and everything will be set and ready to go.

## :joystick: Commands to operate with Crypto Link :joystick:

Crypto link listens to following prefixes:
```text
!<command> <subcommands>
or
@CryptoLink <command> <subcommands>
```
### :sos: Access Help menu :sos:
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
#### Fast balance check and address
```text
!acc
```

#### :dollar: Making P2P (Peer To Peer) public transaction :dollar:

Function Structure

```text
!send <amount> <currency symbol> <@discord.User> <message=Optional>

Note: if transactions successful both sender and recipient will receive transaction slip with included message. 
```

example for Stellar Lumen:
```text
!send 100 xlm @Animus#4608 have a coffee # Sends N amount of XLM to targeted user
```

#### :moneybag: Making Discord Withdrawals and Deposits :moneybag:

##### :incoming_envelope: Deposits :incoming_envelope:
```text
!wallet deposit  # Returns instructions on how to deposit currency to Discord
```

##### :outbox_tray: Withdraw XLM from Discord:outbox_tray:
```text
!withdraw xlm <amount> <destination address>  
```

Example:
```text
!withdraw xlm 100 GBAGTMSNZLAJJWTBAJM2EVN5BQO7YTQLYCMQWRZT2JLKKXP3OMQ36IK7
```

#### :credit_card: Purchasing membership  :credit_card:

If user wants to purchase available monetized role on community, he/she can do so with command:
```text
!membership subscribe <@discord.Role>
```

#### :page_with_curl: All available commands for user :page_with_curl:

Complete command list can be access [here](USERCOMMANDS.md)

### :crown: As Discord Guild Owner :crown:

#### :currency_exchange: Merchant System registration :currency_exchange:

In order to register corporate wallet and merchant system for community execute command:
```text
!merchant_initiate
```
once successfully registered you can check all available commands under:

#### :page_with_curl: Access merchant manual :page_with_curl:

Merchant manual can be access through
```text
!merchant manual
```

#### :moneybag: Check community balance :moneybag:
```text
!merchant balance
```

More on merchant system, its use cases, and set up procedure can be found [here](MERCHANTCOMMANDS.md).

Instructions to operate with corporate account can be found [here](CORPORATEACCOUNTMANAGEMENT.md)

## :money_with_wings: Fees for using the crypto link system :money_with_wings:
We have integrated as well operational fees to gather funding for further development. Fees are currently applied
 for following crypto link activities:

- [X] Merchant license fee 
- [X] Merchant wallet withdrawal
- [X] XLM withdrawal fee

Additional limits:
- [X] Minimum merchant transfer amount
- [X] Minimum stellar withdrawal amount 

For explanation on all the fees and limits read [here](FEESANDLIMITS.md) 
 
 To check current fees and their conversion please use command:

```text
!fees
```


## Bot management commands
Crypto Link has as well integrated command for management which are locked for Crypto Link Staff.
Commands are broken down into three specific areas:

- Bot basic administration commands
- Hot wallet queries
- Management of fees and limits for Crypto Link

More on commands and their showcase can be viewed [here](CRYPTOLINKSTAFF.md)

## Additional and Specific Material
- [Available Cryptocurrencies and fees on Crypto Link System](COINLIMITS.md)
- [Bot Set up functions only Crypto Link Staff](CLOFFCHAIN.md)
- [Help Commands](HELPCMDS.md)
- [Dealing with user accounts and making P2P payments](USERCOMMANDS.md)
- [Merchant System Only for Community owners](MERCHANTCOMMANDS.md)
- [Command map and help categories](COMMANDMAP.md)]


##Roadmap

[Development road-map](ROADMAP.md)

## Get in touch

### Crypto Link invite 
Coming soon (when its officially release)...

### Join us on Discord
[Discord Invite Link](https://discord.gg/ddvGTsb)

### Send us email
cryptolinkpayments@gmail.com

## Contributing 
If you would like to contribute to the project we have prepared certain guidelines which can be accessed [here](CONTRIBUTINGGUIDLINES.md)

## License
Crypto Link is an open-source project managed by Launch Pad Investments.
We are operating under the [GNU GENERAL PUBLIC LICENSE](https://github.com/launch-pad-investments/crypto-link/blob/master/LICENSE).

## :pig2:  Support jar :pig2: 
### Cryptocurrencies
```text
BTC: 36vWbdegL57pHK3sVghrpwfp3V1tMqvHfc
ETH: 0x03AE3AD4b8d19091363Beb6f97AA10f8ae9c3284
XLM: GD6SRXH4BXMW7ANSW3PKXZNORKHRXQIGV7TYNK6DHSDB5ISC3M7FOQUU
NEO: AbXWN3yD7JpajRiPmXdaTF4KRCHjkVjUSV
ONT: AKSDsUfbyJcQgpycwi73MCvapseLwt2P1c
```

