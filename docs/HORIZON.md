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

## :office_worker: Horizon Accounts Endpoint :office_worker:
Returns information on available sub-commands
```text
!accounts
```

### :new: Create inactive on-chain account :new:
```text
!accounts create
```

### :mag_right: Query Accounts :mag:
Returns the details on balances and account settings
```text
!accounts get <Valid Stellar Public Address>
```
Note: In order for account to be found it needs to be activate with XLM.

## :money_with_wings: Horizon Payments Endpoint :money_with_wings:
Returns information on available sub-commands
```text
!payments
```

### :map: Query Payments by Address :map:
```text
!payments address <Valid Stellar Public Address>
```

### :ledger: Query Payments by Ledger Sequence :ledger:
```text
!payments ledger <Ledger Number>
```

### :hash: Query Payments by Transaction Hash :hash:
```text
!payments transaction <transaction hash>
```

## :incoming_envelope: Horizon Transactions Endpoint :incoming_envelope:
Returns information on available sub-commands
```text
!transactions
```

### :map: Query Transactions by Address :map:
```text
!transactions account <Valis Stellar Public Address>
```

### :ledger: Query Transactions by Ledger Sequence :ledger:
```text
!transactions ledger <Ledger Sequence>
```

### Query Transactions by Transaction Hash  :hash:
```text
!transactions single <transaction hash>
```

## :gem: Horizon Assets Endpoints :gem:
Returns information on available sub-commands
```text
!assets
```

### :regional_indicator_c: Query Assets by code :regional_indicator_c:

```text
!assets code <alphanumeric string>
```


### :map: Query Assets Issuer :map:

```text
!assets code <alphanumeric string>
```

## :fireworks: Horizon Effect Endpoints :fireworks:
Returns information on available sub-commands
```text
!effects
```

### :map: Query Effects by Account :map:

```text
!effects account <public address>
```

### :ledger: Query Effects by Ledger Sequence :ledger:

```text
!effects ledger <ledger sequence>
```

### :wrench: Query Effects by Operation ID :wrench:

```text
!effects operations <operation id>
```
### :wrench: Query Effects by Transactions Hash :hash:

```text
!effects transaction <transaction hash>
```

## :ledger: Horizon Ledger Endpoints :ledger:
Returns information on available sub-commands
```text
!horizon ledger
```

### :information_source: Query Ledger by Sequence :information_source:

```text
!ledger <ledger sequence>
```

## :clipboard: Horizon Offers Endpoints :clipboard:
Returns information on available sub-commands
```text
!offers
```

### :id: Query Offers by Offer id :id:

```text
!offers single <offer id>
```

###  :map: Query Offers by Account  :map:

```text
!offers account <Account public address>
```

## :wrench: Horizon Operations Endpoints :wrench:
Returns information on available sub-commands
```text
!operations
```

### :tools:Query single operation :tools:

```text
!operations operation <operation id>
```

### :ledger: Query operation by ledger :ledger:

```text
!operations ledger <ledger id>
```

### :map: Query operation by Account :map:

```text
!operations account <Account public address>
```

### :hash: Query operation by transaction hash :hash:

```text
!operations transaction <transaction hash>
```

## :book: Horizon Order Book Endpoints :book:
Returns information on available sub-commands
```text
!book
```

### :currency_exchange: Query Orderbook :currency_exchange:

```text
!book details <selling asset> <buying asset>
```

## :wrench: Horizon Operations Endpoints :wrench:
Returns information on available sub-commands
```text
!operations
```

### :tools:Query single operation :tools:

```text
!operations operation <operation id>
```

### :ledger: Query operation by ledger :ledger:

```text
!operations ledger <ledger id>
```

### :map: Query operation by Account :map:

```text
!operations account <Account public address>
```

### :hash: Query operation by transaction hash :hash:

```text
!operations transaction <transaction hash>
```

## :railway_track: Horizon Paths Endpoints :railway_track:
Returns information on available sub-commands
```text
!paths
```
### :service_dog:  Query strict send path :service_dog: 

```text
!paths send <to address> <amount> <asset> <issuer>
```

### :mag: Query strict receive path :mag:

```text
!paths find <from address> <amount> <asset_codes> <asset isser>
```

## :bar_chart: Horizon Trade Aggregation Endpoints :bar_chart:
Returns information on available sub-commands
```text
!trade
```
### :chart_with_upwards_trend: Query trades where base is XLM :chart_with_upwards_trend:

**__Note__**: Resolutions allowed 1, 5, and 15 minutes

```text
!trade agg <counter asset> <counter issuer> <resolution> 
```

## :bar_chart: Horizon Transactions Endpoints :bar_chart:
Returns information on available sub-commands
```text
!transactions
```

### :hash: Query Transaction by hash :hash:

```text
!transactions single <Transaction Hash>
```

### :map: Query transactions for account :map:

```text
!transactions account <valid stellar public address>
```

###:ledger: Query transactions by ledger sequence :ledger:

```text
!transactions ledger <Ledger Number>
```


