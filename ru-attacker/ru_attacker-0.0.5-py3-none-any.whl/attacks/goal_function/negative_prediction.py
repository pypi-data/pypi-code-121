from .basic_goal_function import BasicGoalFunction

__all__ = ["NegativePrediction"]


class NegativePrediction(BasicGoalFunction):
    def success(self, label, prediction):
        if prediction == 1:
            return True
        else:
            return False
