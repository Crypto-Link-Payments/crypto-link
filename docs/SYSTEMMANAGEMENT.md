# Crypto Link system management commands

## :key: Access list :key:
- [X] Crypto Link Staff 
- [ ] Guild owners
- [ ] Discord Members


## Prefix
```text
!<command> <subcommands>
or
@CryptoLink <command> <subcommands>
```

Entry command to access help menu and all available sub-commands is:

## Entry point for management commands
```text
!mng <sub-command>
```

## List of Sub-commands
### Accessing the system
Returns all available sub commands
```text
!mng system
```
#### Turn the bot completely off
```text
!mng system off
```

#### Pull git updates and reload scripts
```text
!mng system update
```
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


[Back to main page](README.md)
### Setting up system fees and limits
All fees are provided in USD ($) and are converted based on current market rates uppon request.
To check all available sub-commands use command:

```text
!fees
```
#### Check current fee and limit values
```text
!fee current
```

#### Change minimum merchant transfer value
```text
!fee change minimum_merchant_transfer_value <Float value in dollar>
```

#### Merchant monthly license fee
```text
!fee change merchant_license_fee <Float value in dollar>
```

#### Merchant wallet transfer fee
```text
!fee change merchant_wallet_transfer_fee <Float value in dollar>
```

#### On chain XLM withdrawal fee

```text
!fee change xlm_withdrawal_fee <Float value in dollar>
```
[Back to main page](README.md)
