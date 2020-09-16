
# General (Each Discord User)
```text
!about --> Returns information about the system
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

## User account commands

```text
!balance --> Fast personal account balance check 
!register --> Registers user into Crypto Link System
!wallet --> Information on available sub commands for personal wallet
!wallet deposit --> Instructions on how to deposit available cryptocurrencies
!wallet xlm --> Get details on Stellar Lumen personal wallet 
```

## Transaction and withdrawals

```text
# wtihdrawals
!withdraw --> Representation of available withdrawal sub-commands
!withdraw stellar <amount:float> <destination address: Valid Stellar Lumen Address>
!withdraw monero <amount:float> <destination address: Valid Monero Address>

#P2P Transactions

!send --> Representation of available sub-commands 
!send xlm <amount:float> <@recipient:discord.User>
```

# System management commands (Available for Kavic and Animus)

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

# Merchant System Community Owners (Owners only)

```text

# Merchant set-up and usage 

!merchant_initiate --> Registers community for the merchant service
!merchant --> Representation of available sub-commands
!merchant manual --> HOW-TO monetize community
!merchant  --> Representation of available sub-commands 
!merchant  create_role <role name> <dolar_value> <weeks:int> <days:int> <hours:int> <minutes:int>
!merchant  delete_role <@discord.Role> --> Deletes role from merchant system 
!merchant  community_roles --> Queries all monetized roles and provides details
!merchant  stop_role <@discord.Role> --> Prevents the monetized role to be purchased 
!merchant  start_role <@discord.Role> -- Re-starts the montezied role

# Commands to operate with community wallet (Owner rights required)

!merchant balance --> Get the balance of the community wallet 
!merchant transfer_xlm --> Withdraws the XLM from corporate account to owners personal wallet

# Licensing options 

!license --> Representation of available sub-commands
!license about --> Information about the license 
!license price --> Information about current license price 
!license status --> Check the license status of the community for merchant system
!license buy --> Representation of available sub commands
!license buy with_xlm --> Use Stellar Lumen to purchase license

```

# Merchant System Consumer commands (everybody with registered wallet)

```text
!membership --> Representation of available sub-commands
!membership current --> Obtain information on active purchased roles
!membership roles --> Return availabale monetized roles on community
!membership subscribe <@discord.Role> <currency ticker xlm>
```