from stellar_sdk import Server

from stellar_sdk import TransactionEnvelope, Network, TextMemo, Payment, Asset, Memo

address = "GDII325UI6TEJIUANLQ6BBIAVO4VGVICLGZ33GWGABKOYQIXI2YY2MYF"
server = Server("https://horizon-testnet.stellar.org")


def process_memo(m):
    "Gets text memo otherwise if something else returs none"
    if isinstance(m, TextMemo):
        memo = m.memo.memo_text
    else:
        memo = None
    return memo


def get_payments(operations: list):
    """
    Processes transaction envelope and returns list of payment operations
    :return: List of payments as dict
    """
    tx_payments = list()
    for op in operations:
        if isinstance(op, Payment):
            amount = op.amount
            asset = op.asset

            # build Asset
            # Process asset of payment
            if isinstance(asset, Asset):
                if asset.is_native():
                    a = 'XLM'
                    issuer = "Stellar Org"
                else:
                    a = asset.code
                    issuer = asset.issuer

            payment = {
                "amount": amount,
                "asset": a,
                "assetIssuer": issuer,
            }
            tx_payments.append(payment)
        else:
            pass

    return tx_payments


new_transactions = server.transactions().for_account(account_id=address).include_failed(False).order(
    desc=False).limit(2).call()

transactions = new_transactions["_embedded"]['records']

from pprint import pprint
pprint(transactions)
if transactions:
    for tx in transactions:
        if address != tx["source_account"]:

            te = TransactionEnvelope.from_xdr(tx["envelope_xdr"], Network.TESTNET_NETWORK_PASSPHRASE)

            # Process operations and return only payments as list of dict
            all_tx_payments = get_payments(te.transaction.operations)

            if all_tx_payments:
                processed_memo = process_memo(te.memo)

                proc_tx = {
                    "memo":processed_memo,
                    "createdAt": tx["created_at"],
                    "paging_token": tx["paging_token"],
                    "hash": tx['hash'],
                    "payments": all_tx_payments
                }

                pprint(proc_tx)

