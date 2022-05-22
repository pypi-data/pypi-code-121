import sys
import time

from fireblocks_sdk import FireblocksSDK, TransferPeerPath, DestinationTransferPeerPath, ONE_TIME_ADDRESS, VAULT_ACCOUNT, \
    EXTERNAL_WALLET
from chain import Chain


CHAIN_TO_ASSET_ID = {
    Chain.MAINNET: 'ETH',
    Chain.ROPSTEN: 'ETH_TEST',
    Chain.KOVAN: 'ETH_TEST2',
    Chain.BSC: 'BNB_BSC',
    Chain.BSC_TEST: 'BNB_TEST',
    Chain.POLYGON: 'MATIC_POLYGON'
}


class Web3Bridge:
    def __init__(self, fb_api_client: FireblocksSDK, vault_account_id: str, external_wallet_address: str, chain: Chain):
        self.fb_api_client = fb_api_client
        self.source_vault_id = vault_account_id
        self.external_wallet_address = external_wallet_address
        self.chain = chain

    def send_transaction(self, tx_data, note=''):
        return self.fb_api_client.create_transaction(
            tx_type="CONTRACT_CALL",
            asset_id=CHAIN_TO_ASSET_ID[self.chain],
            source=TransferPeerPath(VAULT_ACCOUNT, self.source_vault_id),
            amount="0",
            destination=DestinationTransferPeerPath(ONE_TIME_ADDRESS, one_time_address={"address": self.external_wallet_address}),
            # destination=TransferPeerPath(EXTERNAL_WALLET, "address_id_here") --> for whitelisted address
            note=note,
            extra_parameters={
                "contractCallData": tx_data["data"]
            }
        )

    def check_tx_is_completed(self, tx_id):
        is_not_completed = True
        while is_not_completed:
            tx_info = self.fb_api_client.get_transaction_by_id(tx_id)
            if tx_info["status"] == "COMPLETED":
                print("Done successfully")
                is_not_completed = False
            elif tx_info["status"] == "FAILED" or tx_info["status"] == "CANCELED" or tx_info["status"] == "BLOCKED":
                print(f"FAILED with status, {tx_info['status']}")
                sys.exit(1)
            else:
                time.sleep(3)
                print("waiting for tx to be completed")