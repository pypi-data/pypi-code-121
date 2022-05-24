from ekp_sdk.db.mg_client import MgClient
from pymongo import DESCENDING, UpdateOne
import time


class ContractTransactionsRepo:
    def __init__(
            self,
            mg_client: MgClient
    ):
        self.mg_client = mg_client

        self.collection = self.mg_client.db['contract_transactions']
        self.collection.create_index("hash", unique=True)
        self.collection.create_index([("blockNumber", DESCENDING)])
        self.collection.create_index([("timeStamp", DESCENDING)])
        self.collection.create_index([("methodId", DESCENDING)])
        self.collection.create_index("source_contract_address")

    def get_latest(self, contract_address):
        return list(
            self.collection.find(
                {"source_contract_address": contract_address}
            )
                .sort("blockNumber", -1).limit(1)
        )

    def find_since_block_number(self, block_number, limit, method_id=None):
        start = time.perf_counter()
        query = {"blockNumber": {"$gte": block_number}}
        
        if method_id is not None:
            query["methodId"] = method_id
            
        results = list(
            self.collection
                .find(query)
                .sort("blockNumber")
                .limit(limit)
        )

        print(
            f"⏱  [ContractTransactionsRepo.find_since_block_number({block_number})] {time.perf_counter() - start:0.3f}s")

        return results

    def save(self, trans):
        start = time.perf_counter()

        self.collection.bulk_write(
            list(map(lambda tran: UpdateOne(
                {"hash": tran["hash"]}, {"$set": tran}, True), trans))
        )

        print(f"⏱  [ContractTransactionsRepo.save({len(trans)})] {time.perf_counter() - start:0.3f}s")

    def save_logs(self, logs):
        start = time.perf_counter()

        def format_write(log):
            log_index = log["logIndex"]
            return UpdateOne(
                {"hash": log["transactionHash"]},
                {"$set": {f"logs.{log_index}": log}},
                True
            )

        self.collection.bulk_write(
            list(map(lambda log: format_write(log), logs))
        )

        print(f"⏱  [ContractTransactionsRepo.saveLogs({len(logs)})] {time.perf_counter() - start:0.3f}s")