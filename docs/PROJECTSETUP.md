#How to setup project and development environment

## Discord integration instructions
In order to be able to use the bot it needs to be integrated into Discord Community. You can either create your
own guild on Discord and use it as testing environment or than join Crypto Link Community and contact staff. They will
dedicate a special channel for your bot instance so you can at the same time showcase your contribution to the staff.
Staff and request can be also requested through email cryptolinkpayments@gmail.com

### Developer account
Got to [Discord Developer](https://discord.com/developers) page and register for developer account.

### Create Bot Instance
Once Successfully registered you need to create new application to get ***ID*** and create bot by going to 
***Bot*** --> ***Add Bot***. Once everything successfully created, store ***Bot token*** and ***ID*** as you will need 
them as well when setting up .json files on next sections. Create bot invite link from 
[Permission calculator site](https://discordapi.com/permissions.html). In order for bot to function optimally following
permissions are required:

> - [X] Manage Roles
> - [X] Manage Emojis
> - [X] Read Message
> - [X] Send Message
> - [X] Manage Message
> - [X] Embed Links
> - [X] Attach Files
> - [X] Read message history
> - [X] Use external Emojis
> - [X] Add reactions

Once everything selected at the bottom select client link and invite link will be automatically generated for you. 
If you are having difficulties you can follow instructions as well [here](https://www.getdroidtips.com/discord-bot-token/#:~:text=Start%20by%20going%20to%20the%20Discord%20Developer%20Portal,a%20name%20to%20the%20bot%20and%20click%20Create)
 or [here](https://discordpy.readthedocs.io/en/latest/discord.html)


## Install project dependencies

### Install mongoDB instructions
```text
https://docs.mongodb.com/manual/installation/
```

### Install PIP project requirements
```text
pip3 install -r requirements.tx
```

## Setup required files
In main directory of the project create following json files and populate key with required values

### Cl system channels
***filename***: 
```text
autoMessagingChannels.json
```
***file content***: 
```json
{
  "stellar": 0,  
  "merchant": 0,
  "sys": 0,
  "twitter": 0
}
```
- ***stellar*** : discord channel id as INT where on chain activities will be relayed
- ***merchant*** : discord channel id as INT where merchant wallet transfers will be relayed
- ***sys***: discord channel id as INT where other system messages will be relayed
- ***twitter***: discord channel id where twitter messages will be relayed

### Discord Bot config file
***filename***: 
```text
botSetup.json
```
***file content***: 
```json
{
  "token": "bot token",
  "command": " " ,
  "botId": 0,
  "ownerId": 0,
  "creator": 0,
  "trustedMembers": [],
 "horizonServer": "https://horizon-testnet.stellar.org",
  "database": {
    "connection": "mongodb://127.0.0.1:27017"},
  "twitter": {
    "apiKey": "xxxx",
    "apiSecret": "xxxx",
    "accessToken": "xxxx",
    "accessSecret":"xxxx"
  }

}
```

- ***token***: discord bot token obtained from [Discord Developer page](https://discord.com/developers/applications)
- ***command***: any character or combination of letter to be used as prefix for bot to listen to
- ***botId***: bot id (client id) number from Discord developer page
- ***ownerId***: User id of Discord User who owns the bot
- ***creator***: User id of Discord User who created the bot
- ***trustedMembers***: all additional user IDs who should have access to system commands
- ***horizonServer***: Tetstnet vs pubnet
- ***database***: connection to mongodb database. leave it like this if you run bot locally
- ***twitter***: api key details from twitter developer account

### Stellar hot wallet setup
Two different files are required. You can create Stellar testnet account through [Stellar Laboratory](https://laboratory.stellar.org/#account-creator?network=test)

steps:
```text
1. generate new key pair through ***Generate keypair***
2. fund a testnet account with friendbot to activate account
3. Provide details to files bellow
```

#### Public key details (wallet address)
***filename***: 
```text
hotWallets.json
```
```json
{
  "xlm": "public key here"
}
```
#### Private key details
***filename***: 
```text
walletSecrets.json
```
```json
{
  "stellar":"private key here"
}
```

### Stellar paging_token (height of "blockchain")
***filename***: 
```text
stellarPag.json
```
```json
{
  "pag":"4232625845706753"
}
```

### Last Processed Tweet file
***filename***: 
```text
lastTweet.json
```
```text
{"tweetId": 1313421059119616002}
```

## Running the bot 
Cd to project folder and run 

Ubuntu
```text
./python3 main.py
```

On first run script should automatically check database and create necessary tables and documents. After that
bot should show successful login as example bellow, as well as become online on Discord. 

```text
Logged in as
Crypto Link
706806251321032726
------
================================

```

[Back to Contributing](CONTRIBUTING.md)  |  [Back to main page](README.md)
