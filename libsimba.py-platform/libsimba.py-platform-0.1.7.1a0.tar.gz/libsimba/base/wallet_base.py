class WalletBase:
    """Base class for libsymba.py wallet implementations"""

    def __init__(self):
        self.wallet = None

    def unlock_wallet(self, passkey):
        """
        Unlock the wallet with the given passkey

        Args:
            passkey: used to unlock the wallet
        """
        raise NotImplementedError("Wallet.unlock_wallet Not Implemented")

    def generate_wallet_from_mnemonic(self, mnemonic: str = None):
        """
        Create a new wallet using that wallet mnemonic. Set self.wallet to this new wallet.

        Args:
            mnemonic: A string the wallet will use to create the wallet
        """
        raise NotImplementedError(
            "Wallet.generate_wallet_from_mnemonic Not Implemented"
        )

    def generate_wallet_from_private_key(self, private_key: str = None):
        """
        Create a new wallet using that wallet mnemonic. Set self.wallet to this new wallet.

        Args:
            mnemonic: A string the wallet will use to create the wallet
        """
        raise NotImplementedError(
            "Wallet.generate_wallet_from_private_key Not Implemented"
        )

    def delete_wallet(self):
        """
        Remove the current wallet
        """
        raise NotImplementedError("Wallet.delete_wallet Not Implemented")

    def wallet_exists(self) -> bool:
        """
        Does a wallet currently exists?

        Returns:
            Returns a boolean indicating if a wallet exist.
        """
        raise NotImplementedError("Wallet.wallet_exists Not Implemented")

    def sign(self, payload) -> dict:
        """
        Sign the payload with the wallet

        Args:
            payload: an object
        Returns:
            Returns the signed transaction
        """
        raise NotImplementedError("Wallet.sign Not Implemented")

    def get_address(self):
        """
        The address associated with this wallet

        Returns:
            Returns the address associated with this wallet
        """
        raise NotImplementedError("Wallet.get_address Not Implemented")
