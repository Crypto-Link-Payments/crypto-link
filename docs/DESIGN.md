# Backbone of Crypto Link
## ***Deposit processing***
Part of Crypto link monitors for deposits to hot wallet every 10 minutes. It loops through range of blocks and searches 
for incoming transactions. Once new incoming transactions identified it uses transaction memo to cross-reference with 
database of user wallets. Once Discord user identified it assigns him deposited amount of XLM and makes it available for
 user to use on Discord for P2P transactions or to be used to make purchases on Merchant System.

## ***Withdrawal processing***
Withdrawals are execute straight upon initiated request from the user through Crypto Link if user has sufficient amount 
in his wallet, which he requested to be withdrawed. Once withdrawal is successfully processed user receives notification
 with transaction details so he/she can query them in explorer. 

## ***Off-chain activities***
All Discord related activities where XLM is used happens off-chain. In order for transactions to be instant and to allow
other types of special transactions, which we are planning to integrate (random tx, tx for users with certain role, 
rain tx, etc.), off-chain wallet system has been created. Once user deposits XLM everything else happens inside 
database till user decides to withdraw from Discord.

## ***Merchant System***
Merchant system allows Discord community owners to monetize Discord roles timely oriented. Owner sets the role, 
provide role time length, value of the role in $ (converted to XLM based on market price). Once done, role becomes
 monetized and available for Discord users to be purchased. Once user purchases it, system will automatically monitor 
 for role expiration, and handle everything on behalf of the owner. 