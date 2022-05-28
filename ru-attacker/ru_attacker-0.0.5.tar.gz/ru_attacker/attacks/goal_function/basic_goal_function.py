from abc import ABC, abstractmethod

__all__ = ["BasicGoalFunction"]


class BasicGoalFunction(ABC):
    """
    A basic class to verify the success of attack
    """
    @abstractmethod
    def success(self, label, prediction):
        """
        a method that verifies whether an attack is successful or not
        :param label: true label
        :param prediction: predicted label
        :return: True/False
        """
        pass
