import ast, uuid, os

from ._base import AlphaClass

class AlphaTransaction(AlphaClass):
    task = None
    name = "TRANSACTION"

    def __init__(self,message=None,message_type=None):
        self.message  = None
        self.error    = False
        self.lifetime = 60*60

        self.message_type   = message_type.upper() if message_type is not None else self.name
        self.process        = os.getpid()
        self.uuid           = str(uuid.uuid4())

        if type(message) == dict:
            self.message        = message
        else:
            self.map(message)

    def map(self, obj):
        if obj is None:
            self.error = True
            return self
            
        self.uuid:str    = obj.uuid
        self.process:int = obj.process

        try:
            self.message = ast.literal_eval(obj.message)
        except Exception as ex:
            self.message = str(ex)
        self.message_type:str = obj.message_type
        self.lifetime:int = obj.lifetime
        self.creation_date:datetime.datetime = obj.creation_date
        return self

    @staticmethod
    def get_type(class_):
        name = class_ if type(class_) == str else class_.__class__.__name__
        return "".join([(c if c.upper() != c or i == 0 else "_" + c) for i, c in enumerate(name)])
