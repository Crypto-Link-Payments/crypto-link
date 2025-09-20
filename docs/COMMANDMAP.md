
# :joystick: Command map for Crypto Link System :joystick: 


/register -> register personal wallet into the Crypto Link system


## Prefix
Slash Commands

## About the system and fees 
```text
!about --> Returns information about the system
```

To check the fees implemented and their values use command:

```text
!fees
```
## User account commands and operations
To be able to access own wallet or operate with the the Crypto Link system you are required to 
register yourself into the system with `/register`

### Wallet queries and management

```text
/wallet help --> List of available commands
/me --> Quick check of the balance 
/wallet balance --> in depth balance overview
/wallet stats --> In depth statistics on the wallet operations
/wallet deposit --> Details on where and how to deposit to Discord wallet
/wallet qr --> Qr code to be scanned for automatic deposit details 
```

#### Making on-chain withdrawals
```text
/wallet withdraw <Stellar valid destination address> <amount:float> <asset_code:str> --> asset code 'xlm' to withdraw "Stellar Lumen"
```

### Making off-chain peer to peer transactions

```text
!send <amount:float> <ticker> <@discord.User> <message optional> --> Creates a public P2P transaction
!private <amount:float> <ticker> <@discord.User> <message optional> --> Initiates a private P2P transaction meaning that the value will not bee seen on private channel
```


### Participating in merchant system on the server to purchase monetized roles
```text
/membership help --> information on all available commands 
/membership
```

## Community Owners 
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