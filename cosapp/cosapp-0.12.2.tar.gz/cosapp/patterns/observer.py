import abc
import inspect
import weakref


class Observer(abc.ABC):
    """Generic interface for observers"""
    def __init__(self, subject=None):
        self._subject = None
        if subject is not None:
            self.observe(subject)

    @abc.abstractmethod
    def _update(self, *args, **kwargs) -> None:
        """Action to perform when notified by observed subject"""
        pass

    def observe(self, subject) -> None:
        """Sign in as observer of subject"""
        self.quit()
        subject.add(self)
        self._subject = weakref.ref(subject)

    def quit(self) -> None:
        """Quit observing whoever observer is currently observing"""
        if self._subject is not None:
            self._subject().remove(self)
        self._subject = None

    def observes(self, subject=None) -> bool:
        """Bool: does observer observe `subject`?
        If `subject` is None, returns True if observer observes anyone, False otherwise."""
        observing = (self._subject is not None)  # does observer observe anyone?
        if subject is None:
            return observing
        return observing and (self._subject() is subject)

    def __del__(self) -> None:
        try:
            object.__getattribute__(self, "_subject")
        except AttributeError:
            pass  # Quit should be skipped if `_subject` is already deleted
        else:
            self.quit()


class Subject:
    """
    Prototype of subject for Observer objects.
    The philosophy is that observers are responsible for signing in or out.
    Therefore, the subject should not unilaterally add or remove observers, except when it is cleared.
    """
    __obs_type = Observer

    def __new__(cls, obs_type=Observer):
        """
        Constructor of class `Subject`, accepting observers of type `Observer`.
        Derived classes can be constructed with a more specialized
        definition of allowed observer types, by specifying `obs_type`.
        """
        cls.__obs_type = obs_type if inspect.isclass(obs_type) else type(obs_type)
        return super().__new__(cls)

    def __init__(self):
        self._observers = weakref.WeakSet()
    
    @classmethod
    def observer_type(cls) -> type:
        """Returns the type of observers allowed to observe Subject"""
        return cls.__obs_type
    
    def notify(self, *args, **kwargs) -> None:
        """Notify observers that they must update"""
        for observer in self._observers:
            observer._update(*args, **kwargs)
    
    def add(self, observer):
        """
        Add an observer to the list of observers.
        Invoked by outside observers when they sign in; should not be called by self directly.
        """
        otype = self.observer_type()
        if not isinstance(observer, otype):
            cls_name = self.__class__.__name__
            raise TypeError(f"{cls_name} can only be observed by objects of type {otype.__name__}")
        self._observers.add(observer)

    def remove(self, observer) -> None:
        self._observers.remove(observer)

    def clear(self) -> None:
        """Force all observers to quit"""
        for observer in self._observers.copy():
            observer.quit()

    @property
    def n_observers(self) -> int:
        """int: number of observers of current subject"""
        return len(self._observers)

    def __del__(self) -> None:
        self.clear()
