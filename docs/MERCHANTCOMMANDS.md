# Merchant system 

## :key: Access list :key:
- [ ] Crypto Link Staff 
- [X] Guild owners
- [ ] Discord Members

## About
Merchant system allows Discord Guild Owners to monetize their Discord Roles. By providing USD value of the role and its
duration, users will be able to purchase role with XLM after conversion from USD to XLM based on CoinGecko deta

## Register merchant system
```text
!merchant_initiate
```
## How to create and activate monetized role 
Once you successfully register into the merchant system you can start to monetize your community.

### Step 1 -> Create role and assign parameters

When creating monetized role following details are required to be provided to the system 

- Role Name -> No longer than 10 Characters in length and no special characters allowed
- Dollar value -> Dollar value of the role which will be used for conversion to XLM when purchase is initiated
- Duration parameters required to be set in order like shown in command bellow and only integer allowed. Infinite role 
is at this point not allowed. At least one of the chronological parameters needs to be greater than 1. 

    - ***Weeks*** - Integer number 
    - ***Days*** - Integer number
    - ***Hours*** - Integer number
    - ***Minutes*** - Integer number
    
```text
!merchant create_role <role name> <value in $> <weeks> <days> <hours> <minutes>
```
Examples:
```text
!merchant create_role Weekly 100 1 0 0 0  # monetized role with name Weekly in value 100$ for 1 week.
```
If everything goes well you should receive notification from the system on successfull creation. 

### Step 2 Activate role for purchase
```text
!merchant start_role <@discord.Role>
```

Referencing to step 1 example would be:
```text
!merchant start_role @weekly
```

***__Congratulations you have just monetized your community. Now inform your members and earn some XLM.__***

## Other available commands 

### Merchant manual
```text
!merchant manual
```

### Role management

#### Removing role from the system
```text
!merchant monetize delete_role <@discord.Role>
```
#### Deactivate merchant role from available to purchase:
```text
!merchant stop_role <@discord.Role>
```
### Activate/reactivate merchant role 
```text
!merchant start_role <@discord.Role>
```

### Community Wallet Commands
#### Checking details of merchant wallet
```text
!merchant balance
```


### Withdraw XLM from wallet to personal wallet

```text
!merchant transfer_xlm
```

[Back to main page](README.md)