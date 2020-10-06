# Crypto Link Quick Start manual for Discord Users


## Crypto Link Prefixes

Crypto link listens to following prefixes:
```text
!<command> <subcommands>
or
@CryptoLink <command> <subcommands>
```

## :runner: Quick start guide :runner:

Head to one of the Communities where Crypto-Link is present and execute 
```text
!register
```

Once you receive successful report to DM on registration you can proceed with:
```text
!wallet   --> Instructions on all available commands to operate with your personal wallet
```

### Check Available Currencies 
```text
!help currencies
```
### Fast balance check and personal address details
```text
!acc
```

### :dollar: Making P2P (Peer To Peer) public transaction :dollar:

Function Structure

```text
!send <amount> <ticker> <@discord.User> <message=Optional>

Note: if transactions successful both sender and recipient will receive transaction slip with included message. 
```

example for Stellar Lumen:
```text
!send 100 xlm @Animus#4608 have a coffee # Sends N amount of XLM to targeted user
```

### :moneybag: Making Discord Withdrawals and Deposits :moneybag:

#### :incoming_envelope: Deposits :incoming_envelope:
Same data can be used for tokens built on Stellar XLM

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

## :sos: Access Help menu :sos:
In order to ease access to Discord users we have provided general command where all functions are explained.
By executing command bellow either on the public channel of the community or direct messaging the bot system
will guide you through all available areas

```text
!help
```

All available commands for ***help*** category are available [here](HELPCMDS.md)


[Back to main page](README.md) | [Complete User Command List](USERCOMMANDS.md)
