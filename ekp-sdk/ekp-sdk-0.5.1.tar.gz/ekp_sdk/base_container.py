from ekp_sdk.db.contract_logs_repo import ContractLogsRepo
from ekp_sdk.db.contract_transactions_repo import ContractTransactionsRepo
from ekp_sdk.db.mg_client import MgClient
from ekp_sdk.db.pg_client import PgClient
from ekp_sdk.services.cache_service import CacheService
from ekp_sdk.services.client_service import ClientService
from ekp_sdk.services.coingecko_service import CoingeckoService
from ekp_sdk.services.etherscan_service import EtherscanService
from ekp_sdk.services.redis_client import RedisClient
from ekp_sdk.services.rest_client import RestClient
from ekp_sdk.services.transaction_sync_service import TransactionSyncService
from ekp_sdk.services.web3_service import Web3Service


class BaseContainer:
    def __init__(self, config):

        EK_PLUGIN_ID = config("EK_PLUGIN_ID", default=None)
        ETHERSCAN_API_KEY = config("ETHERSCAN_API_KEY", default=None)
        ETHERSCAN_BASE_URL = config("ETHERSCAN_BASE_URL", default=None)
        MONGO_DB_NAME = config('MONGO_DB_NAME', default=None)
        MONGO_URI = config('MONGO_URI', default=None)
        PORT = config("PORT", default=3001, cast=int)
        POSTGRES_URI = config("POSTGRES_URI", default=None)
        REDIS_URI = config("REDIS_URI", default=None)
        WEB3_PROVIDER_URL = config("WEB3_PROVIDER_URL", default=None)

        self.rest_client = RestClient()

        if REDIS_URI is not None:
            self.redis_client = RedisClient(
                uri=REDIS_URI
            )
        else:
            print("⚠️ skipped RedisClient init, missing REDIS_URI")

        if POSTGRES_URI is not None:
            self.pg_client = PgClient(
                uri=POSTGRES_URI,
            )
        else:
            print("⚠️ skipped PgClient init, missing POSTGRES_URI")

        if MONGO_URI is not None:
            self.mg_client = MgClient(
                uri=MONGO_URI,
                db_name=MONGO_DB_NAME
            )
        else:
            print("⚠️ skipped MgClient init, missing MONGO_URI")

        if ETHERSCAN_API_KEY is not None and ETHERSCAN_BASE_URL is not None:
            self.etherscan_service = EtherscanService(
                api_key=ETHERSCAN_API_KEY,
                base_url=ETHERSCAN_BASE_URL,
                rest_client=self.rest_client
            )
            self.contract_transactions_repo = ContractTransactionsRepo(
                mg_client=self.mg_client,
            )

            self.contract_logs_repo = ContractLogsRepo(
                mg_client=self.mg_client,
            )
            self.transaction_sync_service = TransactionSyncService(
                contract_transactions_repo=self.contract_transactions_repo,
                contract_logs_repo=self.contract_logs_repo,
                etherscan_service=self.etherscan_service,
            )
        else:
            print(
                "⚠️ skipped EtherscanService init, missing ETHERSCAN_API_KEY and ETHERSCAN_BASE_URL")

        if REDIS_URI is not None:
            self.cache_service = CacheService(
                redis_client=self.redis_client,
            )
        else:
            print("⚠️ skipped CacheService init, missing REDIS_URI")

        if WEB3_PROVIDER_URL is not None:
            self.web3_service = Web3Service(
                provider_url=WEB3_PROVIDER_URL,
            )
        else:
            print("⚠️ skipped Web3Service init, missing WEB3_PROVIDER_URL")

        if EK_PLUGIN_ID is not None:
            self.client_service = ClientService(
                port=PORT,
                plugin_id=EK_PLUGIN_ID
            )
        else:
            print("⚠️ skipped ClientService init, missing EK_PLUGIN_ID")

        self.coingecko_service = CoingeckoService(
            rest_client=self.rest_client
        )
