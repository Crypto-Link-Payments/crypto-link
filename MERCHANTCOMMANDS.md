# Merchant system 
## About
Merchnat system allows Discord Guild Owners to monetize their Discord Roles. By providing USD value of the role and its
duration, users will be able to purchase role with available cryptocurrencies supported by Crypto-Link. 

## Monetization cycle
1. Community owner creates role with any name, usd value and duration
2. Community owner informs members of the monetized role available for purchase
3. Uppon purchase
## Quick Set-up Guide
1. Check if you have rights presented below:
```text
1. Owner of the community
2. Need to have wallet registered in the system (!register)
3. Command needs to be executed on public channel
```
2. Register community into the Crypto-Link merchant system. This will create corporate wallet where all earning will be gathered.

```text
!merchant initiate
```

3. Create Monetized Role

```text
!merchant monetize create_role <role name> <dolar_value> <weeks count> <days count> <hours count> <minute count>
```






### How to delete monetized role 
```text
!merchant monetize delete_role <@discord.Role>
```

### How to obtain all available monetized roles from community?
```text
!merchant monetize community_role
```

### Deactivating and reactivating already created role 
```text
!merchant monetize stop_role <discord.Role>
```

```text
!merchant monetize start_role <discord.Role>
```

## Accessing Merchant Wallet of the community
- get the details on all available commands for the wallet 
```text
!merchant wallet
```
### Wallet balances

```text
!merchant wallet balance
```

### Transfer from Merchant wallet to owner account
```text
!merchant wallet transfer <currency = xlm or xmr>
```