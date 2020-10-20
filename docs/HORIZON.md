# :sunrise:  Discord Horizon Queries and Actions :sunrise: 

## :key: Access list :key:
- [X] Discord Members

## About
Crypto link's Horizon set of commands enables Discord Members to execute queries straight through client-facing API 
server built on top of Stellar Core, where information returned, can be easily interpreted. 
Mimicking functionality of [Stellar Laboratory](https://laboratory.stellar.org/), commands are straight forward so 
members can dive straight into the experience.



## :sos: Horizon help related commands :sos: 

```text
!help horizon
```

## Horizon Entry Point
Returns all available commands to be used by users willing to make queries to the Stellar Core

```text
!horizon
```

## Horizon Accounts endpoint

### Create on-chain account
```text
!accounts create
```

### Query Accounts
```text
!accounts get <Valid Stellar Public Address>
```
Note: In order for account to be found it needs to be activate with XLM.

