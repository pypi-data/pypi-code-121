from ast import literal_eval

from ekp_sdk.db.contract_logs_repo import ContractLogsRepo
from ekp_sdk.db.contract_transactions_repo import ContractTransactionsRepo
from ekp_sdk.services import EtherscanService


class TransactionSyncService:
    def __init__(
            self,
            contract_transactions_repo: ContractTransactionsRepo,
            contract_logs_repo: ContractLogsRepo,
            etherscan_service: EtherscanService,
    ):
        self.contract_transactions_repo = contract_transactions_repo
        self.contract_logs_repo = contract_logs_repo
        self.etherscan_service = etherscan_service
        self.page_size = 1000

    async def sync_transactions(self, contract_address, start_block_number=0):

        latest_block_number = await self.etherscan_service.get_latest_block_number()

        latest_transaction = self.contract_transactions_repo.get_latest(
            contract_address
        )

        if latest_transaction is not None and len(latest_transaction):
            start_block_number = latest_transaction[0]["blockNumber"]

        original_start_block = start_block_number

        while True:
            trans = await self.etherscan_service.get_transactions(contract_address, start_block_number, self.page_size)

            if len(trans) == 0:
                break

            models = []

            for tran in trans:
                block_number = int(tran["blockNumber"])

                if block_number > start_block_number:
                    start_block_number = block_number

                tran["blockNumber"] = block_number
                tran["source_contract_address"] = contract_address
                tran["confirmations"] = int(tran["confirmations"])
                tran["cumulativeGasUsed"] = int(tran["cumulativeGasUsed"])
                tran["gas"] = int(tran["gas"])
                tran["gasUsed"] = int(tran["gasUsed"])
                tran["gasPrice"] = int(tran["gasPrice"])
                tran["isError"] = tran["isError"] == "1"
                tran["timeStamp"] = int(tran["timeStamp"])
                tran["transactionIndex"] = int(tran["transactionIndex"])
                if len(tran["input"]) >= 10:
                    tran["methodId"] = tran["input"][0:10]

                models.append(tran)

            self.contract_transactions_repo.save(models)

            pc_complete = round(
                (block_number - original_start_block) * 100 /
                (latest_block_number - original_start_block),
                1
            )

            print(
                f"🐛 [Transaction Sync] - [{contract_address}] - {block_number} / {latest_block_number} ({pc_complete} %)"
            )

            if (len(trans) < self.page_size):
                break

    async def sync_logs(self, log_address, start_block_number=0):
        latest_block_number = await self.etherscan_service.get_latest_block_number()

        latest_log = self.contract_logs_repo.get_latest(
            log_address
        )

        if latest_log is not None and len(latest_log):
            start_block_number = latest_log[0]["blockNumber"]

        original_start_block = start_block_number

        while True:
            logs = await self.etherscan_service.get_logs(log_address, start_block_number)

            if len(logs) == 0:
                break

            models = []

            for log in logs:
                block_number = literal_eval(log["blockNumber"])

                if block_number > start_block_number:
                    start_block_number = block_number

                log["blockNumber"] = block_number
                log["gasUsed"] = literal_eval(log["gasUsed"])
                log["gasPrice"] = literal_eval(log["gasPrice"])
                log["timeStamp"] = literal_eval(log["timeStamp"])

                if (log["logIndex"] == "0x"):
                    log["logIndex"] = 0
                else:
                    log["logIndex"] = literal_eval(log["logIndex"])

                if (log["transactionIndex"] == "0x"):
                    log["transactionIndex"] = 0
                else:
                    log["transactionIndex"] = literal_eval(
                        log["transactionIndex"])

                models.append(log)

            self.contract_logs_repo.save(models)
            self.contract_transactions_repo.save_logs(models)

            pc_complete = round(
                (block_number - original_start_block) * 100 /
                (latest_block_number - original_start_block),
                1
            )

            print(
                f"🐛 [Log Sync] - {log_address} - {block_number} / {latest_block_number} ({pc_complete} %)"
            )

            if (len(logs) < 1000):
                break
