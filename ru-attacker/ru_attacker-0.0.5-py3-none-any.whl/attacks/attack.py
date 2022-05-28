class Attack:
    """
    A wrapper for attacks
    """
    def __init__(self, transformation, goal_function, type_perturbation, constraints=None, search_method=None):
        """
        It contains of four main components and a type of perturbation which is required for the RTE task
        :param transformation: an obligatory component, type of transformation
        :param goal_function: an obligatory component, type of goal function
        :param type_perturbation: an obligatory component, to what part the perturbation is applied
        :param constraints: a facultative component, constraints to filter samples
        :param search_method: a facultative component, a method to find attack
        """
        self.transformation = transformation
        self.goal_function = goal_function
        self.constraints = constraints
        self.search_method = search_method
        self.type_perturbation = type_perturbation

    def attack(self, model, dataset):
        """
        a method to attack models
        :param model: model to attack
        :param dataset: dataset on which the attack is performed
        :return: results of attack
        """
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

                if self.type_perturbation == "hypothesis":
                    transformations = self.transformation.transform(hypothesis)
                elif self.type_perturbation == "premise":
                    transformations = self.transformation.transform(premise)
                else:
                    raise TypeError("Transformations only to hypothesis and premise are supported")

                if self.search_method:
                    result, transformation, prediction = self.search_method.search(
                        premise, hypothesis, label, transformations,
                        self.goal_function, self.type_perturbation, model, self.constraints
                    )
                    if result == "skipped":
                        correct_attack += 1
                        results["transformed"].append(None)
                        results["attacked label"].append(None)
                        results["attack"].append("skipped")
                        self.print_results(results)
                        continue
                    results["attacked label"].append(prediction)
                    results["transformed"].append(transformation)
                    if label == prediction:
                        correct_attack += 1
                    if result == "succeeded":
                        results["attack"].append("succeeded")
                    else:
                        results["attack"].append("failed")
                    self.print_results(results)
                    continue

                transformation = transformations[0]

                if self.type_perturbation == "hypothesis":
                    valid, results = self.check(hypothesis, transformation, results)
                else:
                    valid, results = self.check(premise, transformation, results)
                if not valid:
                    correct_attack += 1
                    self.print_results(results)
                    continue

                if self.type_perturbation == "hypothesis":
                    prediction = model.predict(model.prepare_data(premise, transformation))
                elif self.type_perturbation == "premise":
                    prediction = model.predict(model.prepare_data(transformation, hypothesis))
                if label == prediction:
                    correct_attack += 1

                results["attacked label"].append(prediction)
                results["transformed"].append(transformation)

                if self.goal_function.success(label, prediction):
                    results["attack"].append("succeeded")
                else:
                    results["attack"].append("failed")
                self.print_results(results)

        print(
            f"Accuracy before attack {round(correct / total, 2)} --> Accuracy after attack {round(correct_attack / total, 2)}"
        )
        print(f"Success rate {round(results['attack'].count('succeeded') / len(results['attack']), 2)}")
        return results

    def check(self, original, transformation, results):
        if self.constraints:
            for constraint in self.constraints:
                if not constraint.check(original, transformation):
                    results["transformed"].append(None)
                    results["attacked label"].append(None)
                    results["attack"].append("skipped")
                    return False, results
        return True, results

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
