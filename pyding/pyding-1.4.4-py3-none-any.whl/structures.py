#structures.py
import asyncio
from .exceptions import UncancellableEvent, UnfulfilledRequirement


# Wrapper for event handlers
class EventHandler:
    def __init__(self, function, event: str, priority: int, event_space, additional_kwargs: dict = {}, execution_requirements: dict = {}, requirement_exceptions: bool = False, is_async: bool = False):
        self.function = function
        self.event = event
        self.priority = priority
        self.additional_kwargs = additional_kwargs
        self.event_space = event_space
        self.execution_requirements = execution_requirements
        self.requirement_exceptions = requirement_exceptions
        self.is_async = is_async

    def register(self, additional_kwargs: dict={}):
        self.event_space.register_handler(self)        
        self.additional_kwargs = self.additional_kwargs | additional_kwargs

    def unregister(self):
        self.event_space.unregister_handler(self)        

    @property
    def registered(self):
        return self.event_space.handler_registered(self)

    def call(self, call, args, kwargs):        
        kwargs = kwargs | self.additional_kwargs
        for argument in self.execution_requirements:
            if argument not in kwargs or self.execution_requirements[argument] != kwargs[argument]:
                if self.requirement_exceptions:
                    raise UnfulfilledRequirement(f"Argument {argument} was unmet.")
                return
        if self.is_async:
            return asyncio.run(self.function(event=call, *args, **kwargs))
        return self.function(event=call, *args, **kwargs)




# Add support for event calls inside objects
class EventSupport:
    def __init__(self):
        self.register_events()

    def register_events(self):
        for method in self.__dir__():
            method = self.__getattribute__(method)
            if isinstance(method, EventHandler):
                if method.registered:
                    method.unregister()
                method.register({"self": self})



# Define the EventCall class
class EventCall:
    def __init__(self, event_name, cancellable=False):
        self.__name = event_name
        self.__cancelled = False
        self.cancellable = cancellable        
        self.response = None
        self.responses = []
    
    # Cancelling is only one-way. 
    def cancel(self):
        if self.cancellable:
            self.__cancelled = True
            return
        raise UncancellableEvent(f'{self.event_name} is not an cancellable event.')
    
    # Using it as a property since we don't want it to be writable 
    @property
    def cancelled(self):
        return self.__cancelled

    @property
    def name(self):
        return self.__name
    
    def __repr__(self):
        return f'<EventCall _name={self.name!r} _cancelled={self.cancelled!r} _response={self.response!r}>'