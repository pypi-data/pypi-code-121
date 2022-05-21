import binascii
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.utils import generate_mnemonic, is_mnemonic
from web3.auto import w3

from libsimba.base.wallet_base import WalletBase
from libsimba.exceptions import (
    LibSimbaException,
    SimbaMnemonicException,
    SimbaPrivateKeyException,
    SimbaWalletNotFoundException,
)


class Wallet(WalletBase):
    def unlock_wallet(self, passkey: str):
        """
        Unlock the wallet with the given passkey

        Args:
            passkey: used to unlock the wallet
        """
        pass

    def generate_from_mnemonic(self, mnemonic: str = None):
        """
        Create a new wallet using that wallet mnemonic. Set self.wallet to this new wallet.

        Args:
            mnemonic: A string the wallet will use to create the wallet
        """
        wallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)

        if not mnemonic:
            mnemonic = generate_mnemonic(language="english", strength=128)

        try:
            wallet.from_mnemonic(
                mnemonic=mnemonic,
                language="english",
            )
        except ValueError as exc:
            raise SimbaMnemonicException(message=str(exc))
        # Clean default BIP44 derivation indexes/paths
        wallet.clean_derivation()

        self.wallet = wallet

    def generate_from_private_key(self, private_key):
        """
        Create a new wallet using that wallet mnemonic. Set self.wallet to this new wallet.

        Args:
            mnemonic: A string the wallet will use to create the wallet
        """
        wallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)

        try:
            wallet.from_private_key(private_key=private_key)
        except binascii.Error:
            raise SimbaPrivateKeyException(message="Invalid private key")

        # Clean default BIP44 derivation indexes/paths
        wallet.clean_derivation()

        self.wallet = wallet

    def delete_wallet(self):
        """
        Remove the current wallet
        """
        self.wallet = None

    def wallet_exists(self) -> bool:
        """
        Does a wallet currently exists?

        Returns:
            Returns a boolean indicating if a wallet exist.
        """
        return self.wallet is not None

    def sign_transaction(self, payload) -> dict:
        """
        Sign the transaction payload with the wallet

        Args:
            payload: a transaction object
        Returns:
            Returns the signed transaction
        """
        if not self.wallet_exists():
            raise SimbaWalletNotFoundException(message="No wallet loaded!")

        try:
            transaction_template = {
                "to": bytes.fromhex(payload["to"][2:]),
                "value": 0,
                "gas": payload["gas"],
                "gasPrice": payload["gasPrice"],
                "data": bytes.fromhex(payload["data"][2:]),
                "nonce": payload["nonce"],
            }
        except KeyError as exc:
            raise LibSimbaException(message=f"Missing field in transaction: {exc}")

        private_key = self.wallet.private_key()

        try:
            signed = w3.eth.account.sign_transaction(transaction_template, private_key)
        except TypeError as exc:
            raise LibSimbaException(message=f"Invalid transaction provided: {exc}")

        return {
            "rawTransaction": signed.rawTransaction.hex(),
            "hash": signed.hash.hex(),
            "r": signed.r,
            "s": signed.s,
            "v": signed.v,
        }

    def get_address(self):
        """
        The address associated with this wallet

        Returns:
            Returns the address associated with this wallet
        """
        if not self.wallet_exists():
            raise SimbaWalletNotFoundException("No wallet loaded!")

        return self.wallet.address()
