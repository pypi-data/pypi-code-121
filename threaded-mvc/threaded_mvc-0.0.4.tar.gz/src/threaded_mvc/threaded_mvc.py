import abc
import threading

__version__ = "0.0.3"


class Model(threading.Thread, abc.ABC):
    """
    Abstract base class for model objects.

    Though Model inherits from threading.Thread, you can not pass in a
    callback object.
    """

    def __init__(self, to_controller_queue, to_model_queue):
        """
        Model constructor

        Args:
            controller_queue (Queue): Queue to pass messages to Controller
            model_queue (Queue): Queue to pass messages to Model
        """
        # Call Thread class's init() function
        threading.Thread.__init__(self)

        # These are our message queues to and from the from controller
        self.to_controller_queue = to_controller_queue
        self.to_model_queue = to_model_queue

    @abc.abstractmethod
    def run(self):
        """
        Model's thread entry point.

        You must override this method in a subclass.
        """
        pass


class View(abc.ABC):
    """
    Abstract base class for view objects.
    """

    @abc.abstractmethod
    def __init__(self):
        """
        View contructor

        This is an abstract method that must be overridden
        """
        pass


class Controller(abc.ABC):
    """
    Abstract base class for controller objects.
    """

    @abc.abstractmethod
    def __init__(self, to_controller_queue, to_model_queue):
        """Controller constructor

        This is an abstract method that must be overridden

        Args:
            to_controller_queue (Queue): Queue to send messages to the
                                        Controller object
            to_model_queue (Queue): Queue to send messages to the
                                        Model object
        """
        # These are our message queues to and from the from controller
        self.to_controller_queue = to_controller_queue
        self.to_model_queue = to_model_queue
