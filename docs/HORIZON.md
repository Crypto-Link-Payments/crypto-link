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

## Horizon Accounts Endpoint
Returns information on available sub-commands
```text
!accounts
```

### Create on-chain account
```text
!accounts create
```

### Query Accounts
Returns the details on balances and account settings
```text
!accounts get <Valid Stellar Public Address>
```
Note: In order for account to be found it needs to be activate with XLM.

## Horizon Payments Endpoint
```text
!payments
```

## Horizon Payments Endpoint
Returns information on available sub-commands
```text
!payments
```

### Query Payments by Address
```text
!payments address <Valis Stellar Public Address>
```

### Query Payments by Ledger Number
```text
!payments ledger <Ledger Number>
```

### Query Payments by Transaction Hash
```text
!payments transaction <transaction hash>
```

## Horizon Transactions Endpoint
Returns information on available sub-commands
```text
!transactions
```

### Query Transactions by Address
```text
!transactions account <Valis Stellar Public Address>
```

### Query Transactions by Ledger Number
```text
!transactions ledger <Ledger Number>
```

### Query Transactions by Transaction Hash
```text
!transactions single <transaction hash>
```