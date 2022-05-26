from abc import ABC, abstractmethod


class Algorithm(ABC):
    """The algorithm wrapper template for the customized agent
    """    
    @abstractmethod
    def take_action(self, observation, info=None):
        """Return an action from the action space.

        Args:
            observation (any): The observation from the environment.
            info (any, optional): The market information. Defaults to None.

        Raises:
            NotImplementedError: You have to implement this method
        """        
        raise NotImplementedError
