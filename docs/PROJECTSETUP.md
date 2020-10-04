#How to setup-project locally

## Install project dependencies

### Install mongoDB
```text
https://docs.mongodb.com/manual/installation/
```

### Install requirements
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
  "sys": 0
}
```
- ***stellar*** : discord channel id as INT where on chain activities will be relayed
- ***merchant*** : discord channel id as INT where merchant wallet transfers will be relayed
- ***sys***: discord channel id as INT where other system messages will be relayed

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
  "database": {
    "connection": "mongodb://127.0.0.1:27017"}
}
```

- ***token***: discord bot token obtained from [Discord Developer page](https://discord.com/developers/applications)
- ***command***: any character or combination of letter to be used as prefix for bot to listen to
- ***botId***: bot id number from Discord developer page
- ***ownerId***: User id of Discord User who owns the bot
- ***creator***: User id of Discord User who created the bot
- ***trustedMembers***: all additional user IDs who should have access to system commands
- ***database***: connection to mongodb database. leave it like this if you run bot locally

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

