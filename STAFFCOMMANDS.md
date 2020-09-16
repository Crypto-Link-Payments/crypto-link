# Corporate Account Money Management 

Bot Prefix : ! or Bot tag

## Check Corporate Balance
``` check_corp_balance```

## Transfer from Corporate Balance to person
```transfer```

### Sweep Stellar Lumen Balance 
``` transfer sweep_xlm``` 

### Sweep Monero Balance
``` transfer sweep_xmr```


# Set-ups (fees)

## View currently set fees for the system 
```fee current```

## Changing Various Fees for services
```fee change```

### Change minimum merchant transfer amount
- Function is designed to set a minimum withdrawal limit for Communities from their corporate wallets to personal wallet of the owner

```fee change minimum_merchant_transfer_value <float value in $ 0.00 format>```

### Change merchant wallet transfer fee
- Function changes the fee community owner needs to pay when trasnfering from 
community merchant wallet to his personal wallet

``` fee change merchant_wallet_transfer_fee  <float value in $ - 0.00 format>```

### Change merchant 31 day license fee value
- This functions allows to set a one time fee for communities in order to remove previous fees in duration of 31 days
``` fee change merchant_license_fee <float value in $ - 0.00 format>```


### Change withdrawall fee for Stellar Network
- This function allows to set minimum withdrawal fee in $ when discord user 
requests on chain withdrawal from Discord wallet to any stellar address

```fee change xlm_withdrawal_fee <float value in $ - 0.00 format>```

### Change withdrawall fee for Monero Network
- This function allows to set minimum withdrawal fee in $ when discord user 
requests on chain withdrawal from Discord wallet to any monero address

```fee change xmr_withdrawal_fee <float value in $ - 0.00 format>```

# Hot Wallet available actions

## Stellar Lumen (XLM)

## Get Stellar Lumen hot wallet balance and details 
```hot_wallet stellar_balance```

## Monero (XMR)

## Get Monero hot wallet balance and details 
```hot_wallet monero_balance```