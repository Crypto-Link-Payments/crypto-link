# Command access for users

## :key: Access list :key:
- [ ] Crypto Link Staff 
- [ ] Guild owners
- [X] Discord Members


## Prefix
```text
!<command> <subcommands>
or
@CryptoLink <command> <subcommands>
```

## Available commands for Discord members

### Account related commands
#### Register yourself to Crypto Link System
```text
!register
```

#### Quick balance check 
```text
!acc
```

#### Wallet statistics

```text
!wallet stats
```

#### Check balance of wallet (detailed)
```text
!wallet balance
```

#### Withdraw funds
```text
!withdraw xlm <amount> <destination address>
```

#### Deposit details for your account
```text
!wallet deposit
```
***Note***: Be sure to provide exact Stellar Deposit address and your unique MEMO otherwise funds might get lost

### Transaction related commands

#### Public peer to peer transactions
```text
!send <amount> <ticker> <@discord.User> <message>
```
***Note***: Transaction can be executed 1x/1min/user

#### Private Peer to Peer transaction
```text
!private <amount> <ticker> <@discord.User> <message>
```
***Note***: Transaction can be executed 1x/1min/user


### Merchant Related commands (consumer perspective)
```text
!merchant
```
#### Check available roles on community for purchase
```text
!membership roles
```

#### Check currently obtained roles and their expiration time
```text
!membership current
```
#### Purchase role/membership 
```text
!membership subscribe <@discord.Role>
```

[Back to main page](README.md)