# Merchant system 

## About
Merchant system allows Discord Guild Owners to monetize their Discord Roles. By providing USD value of the role and its
duration, users will be able to purchase role with XLM after conversion from USD to XLM based on CoinGecko deta

## Register merchant system
```text
!merchant_initiate
```

## 
## How to create monetized role



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