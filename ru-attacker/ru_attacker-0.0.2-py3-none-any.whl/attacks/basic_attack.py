from abc import ABC, abstractmethod

__all__ = ["BasicAttack"]


class BasicAttack(ABC):
    @abstractmethod
    def attack(self, model, dataset):
        pass

    @staticmethod
    def print_results(results):
        di = {1: "entailment", 0: "not_entailment"}
        if results["attacked label"][-1] != None:
            print(f"""
                  [Succeeded / Failed / Skipped / Total] {results["attack"].count("succeeded")} / {results["attack"].count("failed")} / {results["attack"].count("skipped")} / {len(results["attack"])}:
                  {di[results["original label"][-1]]} --> {di[results["attacked label"][-1]]}
                  original premise: {results["original premise"][-1]}
                  original hypothesis: {results["original hypothesis"][-1]}
                  
                  transformed: {results["transformed"][-1]}
                  
                  """)
        else:
            print(f"""
                  [Succeeded / Failed / Skipped / Total] {results["attack"].count("succeeded")} / {results["attack"].count("failed")} / {results["attack"].count("skipped")} / {len(results["attack"])}:
                  {di[results["original label"][-1]]} --> Skipped

                  """)
