
class AlphaFile():
    def __init__(self,
            name:str,
            permission:str=None,
            owner:str=None,
            group:str=None,
            size:int=None,
            date:str=None
        ):
        self.name = name.split('.')[0].strip()
        self.extension = '' if not '.' in name else name.split('.')[1]
        self.permission = permission
        self.owner = owner
        self.group = group
        self.size = size
        self.date = date

        self.key = None