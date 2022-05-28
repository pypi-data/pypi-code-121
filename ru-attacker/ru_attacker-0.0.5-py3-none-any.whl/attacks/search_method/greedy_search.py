from .basic_search_method import BasicSearchMethod

__all__ = ["GreedySearch"]


class GreedySearch(BasicSearchMethod):
    def search(self, premise, hypothesis, label, transformations, goal_function, type_perturbation, model,
               constraints=None):
        prediction = None
        for transformation in transformations:
            if type_perturbation == "hypothesis":
                ch = self.check(hypothesis, transformation, constraints)
                if ch:
                    prediction = model.predict(model.prepare_data(premise, transformation))
                    if goal_function.success(label, prediction):
                        return "succeeded", transformation, prediction
            else:
                if self.check(premise, transformation, constraints):
                    prediction = model.predict(model.prepare_data(transformation, hypothesis))
                    if goal_function.success(label, prediction):
                        return "succeeded", transformation, prediction
        if not prediction:
            return "skipped", None, None
        return "failed", transformation, prediction

    @staticmethod
    def check(original, transformation, constraints):
        if constraints:
            for constraint in constraints:
                if not constraint.check(original, transformation):
                    return False
        return True
