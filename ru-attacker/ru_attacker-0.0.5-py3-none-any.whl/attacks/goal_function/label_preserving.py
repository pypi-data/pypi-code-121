from .basic_goal_function import BasicGoalFunction

__all__ = ["LabelPreserving"]


class LabelPreserving(BasicGoalFunction):
    def success(self, label, prediction):
        if label == prediction:
            return False
        else:
            return True
