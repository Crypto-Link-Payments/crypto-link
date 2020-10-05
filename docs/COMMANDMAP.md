
# Command map for Crypto Link System 
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
!wallet balance --> Additional expansion of the wallets balance
!wallet trust --> Used to create a trust line between personal account and token issuer for token withdrawal
```

### Making off-chain peer to peer transactions

```text
!send <amount:float> <ticker> <@discord.User> <message optional> --> Creating public transaction
!private <amount:float> <ticker> <@discord.User> <message optional> --> Creating private transaction
```

### Making on-chain withdrawals
```text
!withdraw --> Representation of available withdrawal sub-commands
!withdraw token <ticker> <amount:float> <destination address: Valid Stellar Lumen Address> --> Stellar chain token withdrawals
!withdraw xlm <amount:float> <destination address: Valid Stellar Lumen Address>  --> Withdrawal of Stellar Lumen (XLM)
```

### Participating in merchant system
```text
!membership --> Returs description on all available sub-commands
!membership current --> Returns on-going purchased memberships for the community user has obtained
!membership roles --> Get all available roles/memberships listed for purchase on community
!membership subscribe --> Subscribe to role which is available on community to be purchased 
```

## Community Owners and merchant system setup

### Merchant setup and general commands

```text
!merchant_initiate --> Registers community for the merchant service
!merchant --> Representation of available sub-commands
!merchant manual --> HOW-TO monetize community
!merchant  create_role <role name> <dolar_value> <weeks:int> <days:int> <hours:int> <minutes:int>
!merchant  delete_role <@discord.Role> --> Deletes role from merchant system 
!merchant  community_roles --> Queries all monetized roles and provides details
!merchant  stop_role <@discord.Role> --> Prevents the monetized role to be purchased 
!merchant  start_role <@discord.Role> --> Re-starts the monetized role
```

### Merchant wallet withdrawals
```text
!merchant balance --> Get the balance of the community wallet 
!merchant transfer_xlm --> Withdraws the XLM from corporate account to owners personal wallet
```
### Merchant Licensing details

```text
!license --> Representation of available sub-commands
!license about --> Information about the license 
!license price --> Information about current license price 
!license status --> Check the license status of the community for merchant system
!license buy --> Representation of available sub commands
!license buy with_xlm --> Use Stellar Lumen to purchase license
```

# System management commands

```text

# Stats of the system 
!stats --> Returns indepth live statistical data on the system

# System management commands
!god --> Available sub commands in god system
!god system --> Available sub commands 
!god system off --> Turning off Crypto Link
!god system update --> Updating the Crypto Link through Github
!god system load_cog <cog.name> --> Loads the cog back and its respective commands
!god system unload_cog <cog.name> --> Unloads cog and its respective commands
!god system list_cogs --> Provides information on all cog names
!god system reload --> Reloads all cogs 

# Corporate account balances
!check_corp_balance --> Returns the balance of the off-chain corporate LPI account 
!transfer --> Representation of all available sub-commands
!transfer sweep_xlm --> Transfers from corporate account to one of god users
!transfer sweep_xmr --> Transfers from corporate account to one of god users

# Hot wallet commands
!hot_wallet --> Representation of all available commands
!hot_wallet stellar_balance --> Return the hot wallet state on Stellar Chain

# Managing fees
!fee --> representation of all available sub-commands
!fee current --> Information on current set fee values for each category
!fee change --> representation of all available sub-commands
!fee change minimum_merchant_transfer_value <dollar amount:float> -> Set minimum withdrawal amount from merchant to owner wallet
!fee change merchant_license_fee <dollar amount:float> -> Set Monthly merchant license fee
!fee change merchant_wallet_transfer_fee <dollar amount:float> --> Set withdrawal fee from merchant wallet to owner wallet if no license
!fee change xlm_withdrawal_fee <dollar amount:float> --> Set on chain withdrawal fee from user wallet 
```
