#  :joystick: Full command list for Discord User :joystick: 

## :key: Access list :key:
- [ ] Crypto Link Staff 
- [ ] Guild owners
- [X] Discord Members


## Available commands for Discord members

### Account and wallet related commands

#### Register yourself to Crypto Link System
If you have not received any transaction yet or you are new to Crypto Link system use command 
bellow to register yourself. 

```text
!register
```

#### Quick Account check
Basic details such as deposit address, memo, Stellar Lumen balance and its conversions to fiat and other
currencies are returned.
```text
!acc
```

#### Wallet help
Returns information on all available sub-commands for the wallet command category
```text
!wallet
```

#### Wallet statistics
Statistical data such as total deposits, withdrawals, executed transactions, etc.  per each token 
are displayed.

```text
!wallet stats
```

#### Check balance of wallet (detailed)
Wallet balance returned for all integrated coins with conversion to fiat.

```text
!wallet balance
```

### Withdrawals, Deposits, Trust Creation

#### Create trustline for token withdrawal 
Since Crypto Link has integrated tokens built on Stellar, to be able to withdraw them you are required to 
create a Trustline between your personal wallet and the Asset Issuer. Once successfully established you will be able 
to withdraw token.

Note: You can do that either by utilizing any app which allows to create trust or than utilize
Crypto Link dedicated command. 

```text
!wallet trust <ticker>
```
#### Withdraw from Discord to personal wallet

##### Withdrawal Instructions

```text
!wallet withdraw
```

##### Withdraw XLM from Discord

```text
!withdraw xlm <amount> <destination address>
```

##### Withdraw Crypto Link integrated/supported token on stellar chain 

```text
!withdraw <ticker> <amount> <destination address>
```

#### Deposit details for your account
```text
!wallet deposit
```
***Note***: Be sure to provide exact Stellar Deposit address and your unique MEMO otherwise funds might get lost


### :incoming_envelope:  Peer to Peer Transaction related commands :incoming_envelope: 

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

## Merchant Related commands (consumer perspective)
Merchant system from consumer perspective has entry point command bellow, which returns all available sub-commands
```text
!membership
```
#### Available Roles
Returns all available roles on the guild which are monetized

```text
!membership roles
```

#### Purchased and on-going roles
Returns the status on roles you have purchased and have not expired yet.
```text
!membership current
```
#### Purchase role/membership 
Roles are currently allowed to be purchased only with Stellar Lumen native currency XLM.

```text
!membership subscribe <@discord.Role>
```

[Back to main page](README.md)