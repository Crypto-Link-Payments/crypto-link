# Crypto Link Discord related commands

## :key: Access list :key:
- [X] Crypto Link Staff 
- [ ] Guild owners
- [ ] Discord Members

## Commands
### Entry point for CL account
Entry point to operate with Crypto Link OFf chain wallet. For sub commands check next sections
```text
!cl <sub-commands>
```

### Sub commands 
#### Check Crypto Balance
```text
!cl balance
```

### Withdraw funds from Crypto Link to personal
```text
!cl sweep
```

__***Note***: this will withdraw all off chain balance from crypto link to the team member who executed command__

### Check Current off chain Statistics
```text
!cl stats
```

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


[Back to main page](README.md)