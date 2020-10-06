# Crypto Link Discord related commands

## :key: Access list :key:
- [X] Crypto Link Staff 
- [ ] Guild owners
- [ ] Discord Members

## Crypto Link On chain wallet
To access all related commands dealing with Crypto Link on-chain wallet entry point is:

```text
!hot <sub-commands>
```

### Check Hot wallet balance

```text
!hot balance
```
Returns compelte information on the state of bots hot wallet. Including token balances. 

## Crypto Link Off chain wallet 
To access all related commands dealing with Crypto Link off-chain wallet entry point is 

```text
!cl <sub-commands>
```

### Check Bot's balance 
Returns current balance of off-chain wallet for all tokens

```text
!cl balance
```

### Withdraw funds from Crypto Link to personal
```text
!cl sweep
```

__***Note***: this will withdraw all off-chain balance from Crypto Link to the team member who executed command. Rights
to withdraw are linked to botSetup.json file under key ***ownerId*** & ***creatorId***__

### Check Current off chain Statistics
Check Crypto Link On-chain and Off-chain stats. Data like Discord guild and member reach, filtered stats
for on chain deposits and withdrawals as well as off chain transactions counts, etc. is returned.

```text
!cl stats
```

## Crypto Link system management commands

### Accessing the system
Returns all available sub commands
```text
!mng system
```
#### Turning bot OFF

```text
!mng system off
```

Command executes __sys.exit(0)__ and Crypto Link will stop operating completelly.

#### Pull git updates and reload scripts
```text
!system update
```
Command will fetch latest commit from github and reload bot COGS. Important to remember is that bot 
will load only updates into cogs not to Crypto Link backend. In order to load new backend changes, a
complete restart of the bot is required.

### Accessing Discord part of the system
Returns all available sub commands
```text
!mng scripts
```
#### Listing all available cogs
```text
!mng scripts list_cogs
```
#### Unloading specific cog
```text
!mng scripts unload <cog name>
```

#### Loading specific cog
```text
!mng scripts load <cog name> 
```

#### Reload all cogs
```text
!mng scripts reload <cog name> 
```

## Crypto Link COGS management (commands)
More on COGS can be found [here](https://snoozey.io/discord-py-cogs/). Cogs include all commands which 
are available to end user to be utilized in order to operate with the bot. 
On the other than this allow bot owners to turn OFF and ON set of commands in each COG (py script) and still
keep the bot online. 

### Entry point for cog management
To access all related commands dealing with Crypto Link on-chain wallet entry point is:

```text
!manage scripts <sub-command>
```

### Getting the list of all integrated cogs
this will return names of the cogs which can be used in other commands bellow
```text
!manage scripts list_cogs
```

### Turn single set of commands off
```text
!manage scripts unload <cog name>
```

### Turn single set of commands on
```text
!manage scripts load <cog name>
```

### Reload all commands on Crypto Link System
```text
!manage scripts reload
```

## Fees and Limits set-up


### Check current fee and limit values

```text
!fees
```
Returns details on all current limits and fees integrated in Crypto Link System


### Entry point for fee management
```text
!fee change
```
Returns all commands available to manage fees and limits

### Change token on-chain withdrawal fees
```text
!fee change coin_fee <value> <ticker>
```
Changes the fee when user initiates discord on-chain withdrawal.

#### Change minimum merchant transfer value
```text
!fee change minimum_merchant_transfer_value <Float value in dollar>
```
If guild owners have integrated merchant into their activities, they will get funds relayed to their
corporate wallet. We have integrated minimum merchant transfer value when guild owners are withdrawing
to their personal wallets. 

#### Merchant wallet transfer fee
```text
!fee change merchant_wallet_transfer_fee <Float value in dollar>
```
As per on-chain Crypto Link System has integrated as well merchant wallet transfer fee. This fee is 
deducted from the amount withdrawn by the guild owner to his personal wallet. 

#### Merchant monthly license fee
```text
!fee change merchant_license_fee <Float value in dollar>
```
If guild owner purchases monthly license he will be stripped of all additional fees when transfering 
from merchant wallet to his/her own wallet.


[Back to main page](README.md) [Back to previous page](CONTRIBUTING.md)