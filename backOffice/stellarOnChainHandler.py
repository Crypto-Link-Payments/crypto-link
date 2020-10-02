"""
Handling Stellar chain
"""

import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from stellar_sdk import Account, Server, Keypair, TransactionEnvelope, Payment, Network, TransactionBuilder, exceptions

from utils.tools import Helpers

helpers = Helpers()
secret_details = helpers.read_json_file(file_name="walletSecrets.json")  # Load Stellar wallet secrets
public_details = helpers.read_json_file(file_name="hotWallets.json")  # Load hot wallet details
integrated_coins = helpers.read_json_file(file_name='integratedCoins.json')


class StellarWallet:
    """
    Stellar Hot Wallet Handler on chain
    for live net use self.server = Server(horizon_url="https://horizon.stellar.org")  # Live network

    """

    def __init__(self):
        self.public_key = public_details["xlm"]
        self.private_key = secret_details['stellar']
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

    def get_stellar_hot_wallet_details(self):
        """
        Return the stellar hot wallet balance
        :return:
        """
        data = self.server.accounts().account_id(account_id=self.public_key).call()
        if 'status' not in data:
            data.pop('_links')
            data.pop('data')
            data.pop('flags')
            data.pop('last_modified_ledger')
            data.pop('sequence')
            data.pop('subentry_count')
            data.pop('thresholds')
            data.pop('signers')
            data.pop('id')
            data.pop('paging_token')
            return data
        else:
            return {}

    @staticmethod
    def decode_transaction_envelope(envelope_xdr):
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

    def get_incoming_transactions(self, pag=None):
        """
        Gets all incoming transactions and removes certain values
        :return: List of incoming transfers
        """
        data = self.server.transactions().for_account(account_id=self.public_key).include_failed(False).order(
            desc=False).cursor(cursor=pag).limit(200).call()
        to_process = list()
        for tx in data['_embedded']['records']:
            # Get transaction envelope
            if tx['source_account'] != self.public_key and tx['successful'] is True:  # Get only incoming transactions
                tx.pop('_links')
                tx.pop('fee_charged')
                tx.pop('id')
                tx.pop('fee_account')
                tx.pop('fee_meta_xdr')
                tx.pop('ledger')
                tx.pop('max_fee')
                tx.pop('operation_count')
                tx.pop('result_meta_xdr')
                tx.pop('result_xdr')
                tx.pop('signatures')
                tx['asset_type'] = self.decode_transaction_envelope(envelope_xdr=tx['envelope_xdr'])
                tx.pop('envelope_xdr')
                tx.pop('valid_after')
                to_process.append(tx)
        return to_process

    @staticmethod
    def check_if_memo(memo):
        """
        Check if memo has been provided
        :param memo:
        :return:
        """
        if memo != 'none':
            return True
        else:
            return False

    def withdraw(self, address: str, xlm_amount: str):
        source_account = self.server.load_account(self.public_key)
        tx = TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=self.server.fetch_base_fee()).append_payment_op(
            destination=address, asset_code="XLM", amount=xlm_amount).set_timeout(30).build()
        tx.sign(self.root_keypair)
        response = self.server.submit_transaction(tx)
        try:
            if "status" not in response:
                details = self.__decode_processed_withdrawal_envelope(envelope_xdr=response['envelope_xdr'])
                end_details = {
                    "asset": details['code'],
                    "explorer": response['_links']['transaction']['href'],
                    "hash": response['hash'],
                    "ledger": response['ledger'],
                    "destination": address,
                    "amount": details['amount']
                }
                return end_details
        except exceptions.BadRequestError as e:
            # get operation from result_codes to be processed
            error = self.__filter_error(result_code=e.extras["result_codes"]['operations'])
            return {
                "error": f'{error}'
            }

    def token_withdrawal(self, address, token, amount: str):
        """
        Amount as full
        """
        source_account = self.server.load_account(self.public_key)
        tx = TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=self.server.fetch_base_fee()).append_payment_op(
            asset_issuer=integrated_coins[token.lower()]["assetIssuer"],
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
