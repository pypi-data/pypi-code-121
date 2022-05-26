from abc import ABC, abstractmethod
import language_tool_python
import numpy as np
import tensorflow_hub as hub
import tensorflow_text

__all__ = ["BasicAttack"]

embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")
tool = language_tool_python.LanguageTool('ru-RU')


class BasicAttack(ABC):
    """
    A basic class for attacks
    """
    @abstractmethod
    def attack(self, model, dataset):
        """
        A method to attack models
        :param model: a model to attack
        :param dataset: a dataset on which the attack is performed
        :return: results, "status of attack", correct_attack
        """
        pass

    @staticmethod
    def print_results(results):
        """
        A method to print results
        :param results: results dictionary
        :return: None
        """
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

    @staticmethod
    def predict_after_transform_hypothesis(model, premise, transformed, results):
        """
        A method to make prediction after a transformation
        :param model: attacked model
        :param premise: premise
        :param transformed: transformed hypothesis
        :param results: results dictionary
        :return: prediction, results
        """
        prediction = model.predict(model.prepare_data(premise, transformed))
        results["attacked label"].append(prediction)
        results["transformed"].append(transformed)
        return prediction, results

    @staticmethod
    def predict_after_transform_premise(model, hypothesis, transformed, results):
        """
        A method to make prediction after a transformation
        :param model: attacked model
        :param hypothesis: hypothesis
        :param transformed: transformed premise
        :param results: results dictionary
        :return: prediction, results
        """
        prediction = model.predict(model.prepare_data(transformed, hypothesis))
        results["attacked label"].append(prediction)
        results["transformed"].append(transformed)
        return prediction, results

    @staticmethod
    def attack_decorator(func):
        """
        A decorator for attack function
        :param func: attack function
        :return: results
        """
        def wrapper(self, model, dataset):
            results = {
                "original label": [],
                "attacked label": [],
                "original premise": [],
                "original hypothesis": [],
                "transformed": [],
                "attack": [],
            }
            total = 0
            correct = 0
            correct_attack = 0
            for i, row in dataset.iterrows():
                total += 1
                premise = row["premise"]
                hypothesis = row["hypothesis"]
                label = row["label"]
                prediction = model.predict(model.prepare_data(premise, hypothesis))
                if label == prediction:
                    correct += 1
                    results["original premise"].append(premise)
                    results["original hypothesis"].append(hypothesis)
                    results["original label"].append(label)
                    results, attack, correct_attack = func(self, results, model, premise, hypothesis, label, correct_attack)
                    if attack == "succeeded":
                        results["attack"].append("succeeded")
                    elif attack == "skipped":
                        correct_attack += 1
                        results["transformed"].append(None)
                        results["attacked label"].append(None)
                        results["attack"].append("skipped")
                    elif attack == "failed":
                        results["attack"].append("failed")
                    self.print_results(results)
            print(
                f"Accuracy before attack {round(correct / total, 2)} --> Accuracy after attack {round(correct_attack / total, 2)}"
            )
            print(f"Success rate {round(results['attack'].count('succeeded') / len(results['attack']), 2)}")
            return results
        return wrapper

    @staticmethod
    def check_grammar(text):
        """
        A grammar constraint
        :param text: text to check
        :return: True or False
        """
        matches = tool.check(text)
        grammar_mistakes = [1 for m in matches if m.category == "GRAMMAR"]
        if grammar_mistakes:
            return False
        else:
            return True

    @staticmethod
    def check_semantics(original, transformed):
        """
        A semantics constraint
        :param original: original text
        :param transformed: transformed text
        :return: True or False
        """
        score = np.inner(embed(original), embed(transformed))
        if score >= 0.8:
            return True
        else:
            return False
