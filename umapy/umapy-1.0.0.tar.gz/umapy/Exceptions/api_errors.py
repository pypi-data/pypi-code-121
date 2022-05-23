from typing import Optional


class APIError(Exception):
    '''
    All API related errors.
    '''
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class ChampError(Exception):
    '''
    Errors related to champname, their tier or rank.
    '''

    def __init__(self, message):
        super().__init__(message)
        self.message = message

class NodeError(Exception):
    '''
    Errors related to Nodes
    '''
    def __init__(self, message):
        super().__init__(message)
        self.message = message    

class RosterError(Exception):
    '''
    Errors related to Roster
    '''
    def __init__(self, message):
        super().__init__(message)
        self.message = message    