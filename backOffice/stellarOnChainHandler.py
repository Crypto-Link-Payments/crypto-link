"""
Handling Stellar chain
"""

import os
import sys
from stellar_sdk import Account, Server, Keypair, TransactionEnvelope, Payment, Network, TransactionBuilder, exceptions
from stellar_sdk.sep import stellar_uri
from stellar_sdk import TextMemo, Asset
from stellar_sdk.exceptions import NotFoundError
# from pprint import pprint
from colorama import Fore, init
from utils.tools import Helpers

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

init(autoreset=True)


class StellarWallet:
    """
    Stellar Hot Wallet Handler on chain
    for live net use self.server = Server(horizon_url="https://horizon.stellar.org")  # Live network

    """

    def __init__(self, network_type):
        helpers = Helpers()

        # Decide network type
        if not network_type:
            secret_details = helpers.read_json_file(file_name="walletSecretsTest.json")  # Load Stellar wallet secrets
            public_details = helpers.read_json_file(file_name="hotWalletsTest.json")  # Load hot wallet details
            self.network_phrase = Network.TESTNET_NETWORK_PASSPHRASE
            self.network_type = 'testnet'
            self.server = Server(horizon_url="https://horizon-testnet.stellar.org/")
            self.public_key = public_details["xlm"]
            self.dev_key = public_details["xlmDev"]
            self.private_key = secret_details['stellar']

        else:
            secret_details = helpers.read_json_file(file_name="walletSecrets.json")  # Load Stellar wallet secrets
            public_details = helpers.read_json_file(file_name="hotWallets.json")  # Load hot wallet details
            self.network_phrase = Network.PUBLIC_NETWORK_PASSPHRASE
            self.network_type = 'pub-net'
            self.server = Server(horizon_url="https://horizon.publicnode.org/")
            self.public_key = public_details["xlm"]
            self.dev_key = public_details["xlmDev"]
            self.private_key = secret_details['stellar']

        self.root_keypair = Keypair.from_secret(self.private_key)
        self.root_account = Account(account_id=self.root_keypair.public_key, sequence=1)

        print(Fore.YELLOW + f' Connected to {self.network_type}')

    def create_stellar_account(self):
        """
        Creates inactive stellar account which needs to be activated by depositing lumens
        """
        try:
            key_pair = Keypair.random()
            public_key = key_pair.public_key
            private_key = key_pair.secret
            return {f'address': f'{public_key}',
                    f'secret': f'{private_key}',
                    "network": f'{self.network_type}'}
        except NotFoundError:
            return {}

    def generate_uri(self, address: str, memo: str):

        """
        Returns Transaction as envelope
        """

        return stellar_uri.PayStellarUri(destination=address,
                                         memo=TextMemo(text=memo),
                                         asset=Asset.native(),
                                         network_passphrase=self.network_phrase,
                                         message='Deposit to Discord',
                                         ).to_uri()

    @staticmethod
    def __filter_error(result_code):
        if 'op_no_trust' in result_code:
            return 'no trust'
        elif 'op_no_source_account' in result_code:
            return 'No source account provided'
        else:
            return result_code

    def check_if_account_activate(self, address):
        "Try to load account on the network"
        try:
            self.server.load_account(account_id=address)
            return True
        except NotFoundError:
            return False

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

    def decode_transaction_envelope(self, envelope_xdr):
        """
        Decode envelope and get details
        Credits to overcat :
        https://stellar.stackexchange.com/questions/3022/how-can-i-get-the-value-of-the-stellar-transaction/3025#3025
        :param envelope_xdr: Xdr envelope from stellar network
        :return: Decoded transaction details
        """
        te = TransactionEnvelope.from_xdr(envelope_xdr, self.network_phrase)
        operations = te.transaction.operations

        # TODO make multiple payments inside one transaction
        for op in operations:
            if isinstance(op, Payment):
                asset = op.asset.to_dict()
                if asset.get('type') == 'native':
                    asset['code'] = 'XLM'  # Appending XLM code to asset incase if native
                asset["amount"] = op.to_xdr_amount(op.amount)
                # TODO count all deposits
                return asset

    def get_incoming_transactions(self, pag):
        """
        Gets all incoming transactions and removes certain values
        :return: List of incoming transfers
        """
        try:
            builder = self.server.transactions().for_account(
                account_id=self.public_key).include_failed(False).order(
                desc=False).cursor(pag).limit(200)
            data = builder.call()

            # getting URI
            # print(Fore.YELLOW + f"endpoint: {os.path.join(builder.horizon_url, builder.endpoint)}")
            # print(f"params: {builder.params}")

            to_process = list()
            for tx in data['_embedded']['records']:
                # Get transaction envelope
                if tx['source_account'] != self.public_key and tx[
                    'successful'] is True:  # Get only incoming transactions
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
                    to_process.append(tx)
            return to_process
        except Exception as e:
            return e

    def filter_transactions(self, stellar_data):
        to_process = list()
        for tx in stellar_data['_embedded']['records']:
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
                to_process.append(tx)
        return to_process

    def token_withdrawal(self, address, token, amount: str, asset_issuer: str = None, memo=None):
        """
        Amount as full
        """
        source_account = self.server.load_account(self.public_key)
        base_fee = self.server.fetch_base_fee()
        if memo:
            tx = TransactionBuilder(
                source_account=source_account,
                network_passphrase=self.network_phrase,
                base_fee=base_fee).add_text_memo(memo_text=memo).append_payment_op(asset_issuer=asset_issuer,
                                                                                   destination=address,
                                                                                   asset_code=token.upper(),
                                                                                   amount=amount) \
                .set_timeout(30) \
                .build()
        else:
            tx = TransactionBuilder(
                source_account=source_account,
                network_passphrase=self.network_phrase,
                base_fee=base_fee).append_payment_op(asset_issuer=asset_issuer,
                                                     destination=address,
                                                     asset_code=token.upper(),
                                                     amount=amount) \
                .set_timeout(30) \
                .build()

        tx.sign(self.private_key)
        try:
            resp = self.server.submit_transaction(tx)
            details = self.decode_transaction_envelope(envelope_xdr=resp['envelope_xdr'])
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

    def establish_trust(self, token, asset_issuer: str, private_key=None):
        """
        Amount as full
        """
        # Load user secret and get account
        if not private_key:
            private_key = self.private_key

        user_key_pair = Keypair.from_secret(private_key)
        public_key = user_key_pair.public_key

        try:
            source_account = self.server.load_account(public_key)
            tx = TransactionBuilder(
                source_account=source_account,
                network_passphrase=self.network_phrase,
                base_fee=self.server.fetch_base_fee()).append_change_trust_op(asset_code=f'{token.upper()}',
                                                                              asset_issuer=asset_issuer).set_timeout(
                30).build()
            tx.sign(private_key)

            data = self.server.submit_transaction(tx)
            return True, data
        except exceptions.NotFoundError as e:
            print(Fore.RED + f'Error {e}')
            return False, e
        except Exception as e:
            print(Fore.RED + f'Error {e}')
            return False, e

    def get_account_assets(self):
        return self.server.accounts().account_id(account_id=self.public_key).call()

    def get_asset_details(self, asset_code, asset_issuer):
        return self.server.assets().for_code(asset_code=asset_code.upper()).for_issuer(
            asset_issuer=asset_issuer.upper()).call()
