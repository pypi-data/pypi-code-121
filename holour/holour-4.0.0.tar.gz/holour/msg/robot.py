

class ProgramState:

    START = 'start'
    PAUSE = 'pause'
    STOP = 'stop'

    def __init__(self, program_state: str, _type: str = ''):
        assert program_state in (self.START, self.PAUSE, self.STOP)
        self._type = 'program_state'
        self.program_state = program_state

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ProgramState):
            return other.program_state == self.program_state
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<program_state={self.program_state}>"
