"""
Handling Stellar chain
"""

import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from stellar_sdk import Account, Server, Keypair, TransactionEnvelope, Payment, Network, TransactionBuilder, exceptions, \
    ChangeTrust

from utils.tools import Helpers


class StellarWallet:
    """
    Stellar Hot Wallet Handler on chain
    for live net use self.server = Server(horizon_url="https://horizon.stellar.org")  # Live network

    """

    def __init__(self, public_key, private_key):
        helpers = Helpers()
        self.integrated_coins = helpers.read_json_file(file_name='integratedCoins.json')
        self.public_key = public_key
        self.private_key = private_key
        self.root_keypair = Keypair.from_secret(self.private_key)
        self.root_account = Account(account_id=self.root_keypair.public_key, sequence=1)
        self.server = Server(horizon_url="https://horizon-testnet.stellar.org")  # Testnet

    def __base_fee(self):
        """
        Get the base fee from the network
        """
        fee = self.server.fetch_base_fee()
        return fee

    @staticmethod
    def __filter_error(result_code):
        if 'op_no_trust' in result_code:
            return 'no trust'
        elif 'op_no_source_account' in result_code:
            return 'No source account provided'
        else:
            return result_code

    @staticmethod
    def __decode_processed_withdrawal_envelope(envelope_xdr):
        """
        Decode envelope and get details
        Credits to overcat :
        https://stellar.stackexchange.com/questions/3022/how-can-i-get-the-value-of-the-stellar-transaction/3025#3025
        :param envelope_xdr: Xdr envelope from stellar network
        :return: Decoded transaction details
        """
        te = TransactionEnvelope.from_xdr(envelope_xdr, Network.TESTNET_NETWORK_PASSPHRASE)
        operations = te.transaction.operations

        for op in operations:
            if isinstance(op, Payment):
                asset = op.asset.to_dict()
                if asset.get('type') == 'native':
                    asset['code'] = 'XLM'  # Appending XLM code to asset incase if native
                asset["amount"] = op.to_xdr_amount(op.amount)
                return asset

    def make_transaction(self, address, token, amount: str, memo_text: str = None):
        """
        Amount as full
        """

        if token != 'xlm':
            asset_issuer = self.integrated_coins[token.lower()]["assetIssuer"]
        else:
            asset_issuer = None

        source_account = self.server.load_account(self.public_key)
        tx = TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=self.server.fetch_base_fee()).add_text_memo(memo_text=memo_text).append_payment_op(
            asset_issuer=asset_issuer,
            destination=address, asset_code=token.upper(), amount=amount).set_timeout(30).build()
        tx.sign(self.root_keypair)
        try:
            resp = self.server.submit_transaction(tx)
            details = self.__decode_processed_withdrawal_envelope(envelope_xdr=resp['envelope_xdr'])
            end_details = {
                "asset": details['code'],
                "explorer": resp['_links']['transaction']['href'],
                "hash": resp['hash'],
                "ledger": resp['ledger'],
                "destination": address,
                "amount": details['amount']
            }
            return end_details
        except exceptions.BadRequestError as e:
            # get operation from result_codes to be processed
            error = self.__filter_error(result_code=e.extras["result_codes"]['operations'])
            return {

                "error": f'{error} with {token.upper()} issuer'
            }


if __name__ == '__main__':
    from pprint import pprint

    wallet = StellarWallet(private_key="SCLIUWDUS2O5JFDZZI6LCCO4MKHSZMYV543F2K74UJFOPI42PQP45QNB",
                           public_key="GAGJZJPP27DJ6M5T2UVZAMP3CLIZKXDCOXU7UNYWZBAX4XXR5J5DLDZO")

    result = wallet.make_transaction(address="GBAGTMSNZLAJJWTBAJM2EVN5BQO7YTQLYCMQWRZT2JLKKXP3OMQ36IK7", amount='100',
                                     memo_text="$#}_89a05d7b7ce54cada74e", token='xlm')

    # # For personal computer
    # result = wallet.make_transaction(address="GBAGTMSNZLAJJWTBAJM2EVN5BQO7YTQLYCMQWRZT2JLKKXP3OMQ36IK7", amount='1',
    #                                  memo_text="3f1549f69d6f45ec918f", token='xlm')

    pprint(result)
