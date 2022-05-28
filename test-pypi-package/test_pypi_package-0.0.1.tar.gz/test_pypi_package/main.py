from typing import Optional

class HelloWorld:
    """
    HelloWorld class greets users.
    """
    
    def __init__(self, name: Optional[str] = None):
        self.name = name

    def say_hello(self):
        greeting_message = "Hello "
        greeting_message += self.name if self.name is not None else "user"

        print(greeting_message)

        return greeting_message