
# :joystick: Command map for Crypto Link System :joystick: 

## Commands Count
System has currently 65 various commands of various categories dedicate to:
- Discord User accounts and P2P transactions
- Discord Guild Owner and merchant
- Crypto Link System Management for bot owner

## Prefix
Bot listens to prefix 
```text
!

or 

@CryptoLink tag
```

## About the system and fees 
```text
!about --> Returns information about the system
```

To check the fees implemented and their values use command:

```text
!fees
```

## Help Commands
```text
!help --> Main command entry
!help get_started --> Discord User Entry Point with explanation on how to get started
!help currencies --> Information on available cryptocurrencies
!help transactions --> Instruction on how to make peer to peer transaction
!help account --> Information on available commands to operate with personal account
!help owner --> Available commands and sub commands for owners of the community
!help owner merchant --> get information about merchant system
```

## User account commands and operations

### Wallet queries and management

```text
!register --> Registers user into Crypto Link System
!acc --> Returns general report about personal account
!balance --> Fast personal account balance check 
!wallet --> Information on available sub commands for personal wallet
!wallet stats --> Statistical details for off-chain and on-chain activities 
!wallet deposit --> Instructions on how to deposit available cryptocurrencies
!wallet withdraw --> Instructions on how to withdraw available cryptocurrencies
!wallet balance --> Additional expansion of the wallets balance
!wallet trust --> Used to create a trust line between personal account and token issuer for token withdrawal
```

### Making off-chain peer to peer transactions

```text
!send <amount:float> <ticker> <@discord.User> <message optional> --> Creates a public P2P transaction
!private <amount:float> <ticker> <@discord.User> <message optional> --> Initiates a private P2P transaction
```

### Making on-chain withdrawals
```text
!withdraw --> Representation of available withdrawal sub-commands
!withdraw token <ticker> <amount:float> <destination address: Valid Stellar Lumen Address> --> Stellar chain token withdrawals
!withdraw xlm <amount:float> <destination address: Valid Stellar Lumen Address>  --> Withdrawal of Stellar Lumen (XLM)
```

### Participating in merchant system
```text
!membership --> Returns description on all available sub-commands
!membership current --> Returns on-going purchased memberships for the community user has obtained
!membership roles --> Get all available roles/memberships listed for purchase on community
!membership subscribe --> Subscribe to role which is available on community to be purchased 
```

## Community Owners 

### Up-Link activation deactivation
```text
!owner services explorer apply <#discord.TextChannel> 
!owner services explorer remove 
```
### Merchant system setup

#### Merchant setup and general commands

```text
!merchant_initiate --> Registers community for the merchant service
!merchant --> Representation of available sub-commands
!merchant manual --> HOW-TO monetize community
!merchant  create_role <role name> <dollar_value> <weeks:int> <days:int> <hours:int> <minutes:int>
!merchant  delete_role <@discord.Role> --> Deletes role from merchant system 
!merchant  community_roles --> Queries all monetized roles and provides details
!merchant  stop_role <@discord.Role> --> Prevents the monetized role to be purchased 
!merchant  start_role <@discord.Role> --> Re-starts the monetized role
```

#### Merchant wallet withdrawals
```text
!merchant balance --> Get the balance of the community wallet 
!merchant transfer_xlm --> Withdraws the XLM from corporate account to owners personal wallet
```
#### Merchant Licensing details

```text
!license --> Representation of available sub-commands
!license about --> Information about the license 
!license price --> Information about current license price 
!license status --> Check the license status of the community for merchant system
!license buy --> Representation of available sub commands
!license buy with_xlm --> Use Stellar Lumen to purchase license
```

## System management commands
Locked for bot owner/creators

### Overview of all commands
```text
!gods
```

### Crypto Link Hot Wallet commands
```text
!hot --> Information on available sub-commands
!hot balance --> Check hot wallet balance details
```

### Crypto Link off chain information

```text
!cl --> Information on available sub-commands
!cl balance --> Crypto Link own wallet balance information 
!cl stats --> Statistical details about the system
!cl sweep <ticker> --> Transferring balance from Crypto Link wallet to developer 
```

### Crypto Link SYS commands
```text
!system --> Information on available sub-comands
!system off --> Turning the System completely OFF
!system update --> Pull neew updates from github and reload COGS
```

### Crypto Link COG management
```text
!cogs --> Information on available sub-commands
!cogs list --> Returns names of all implemented COGS
!cogs unload <cog name> --> Turns off COG and its relevant commands
!cogs load <cog name> --> Turns on COG and its relevant commands
!cogs reload --> Reloads all the cogs in the system 
```

### Crypto Link Fee Management
```text
!fee --> Returns details on all available categories
!fee change --> Sub-commands expanations
!fee change coin_fee <value in $ in format 0.00> <coin ticker> --> Sets withdrawal fee for integrated coin
!fee change merchant_license_fee <value in $ in format 0.00> --> Sets the merchant license fee
!fee change min_merchant_transfer <value in $ in format 0.00> --> Sets minimum merchant transfer
!fee change merchant_wallet_transfer_fee <value in $ in format 0.00> --> Set fee for transfers from merchant earnings
```

[Back to main page](README.md)