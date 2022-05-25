
class RobotState:
    START = 'start'
    PAUSE = 'pause'
    STOP = 'stop'

    def __init__(self, state: str, target_speed: float, actual_speed: float, _type: str = ''):
        self._type = 'robot_state'
        self.state = state
        self.target_speed = target_speed
        self.actual_speed = actual_speed

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RobotState):
            return other.state == self.state and \
                   other.target_speed == self.target_speed and \
                   other.actual_speed == self.actual_speed
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<robot_state<state={self.state},target_speed={self.target_speed},actual_speed={self.actual_speed}>"


class RobotStateChange:

    def __init__(self, state: str, speed: float, _type: str = ''):
        assert state in [RobotState.START, RobotState.PAUSE, RobotState.STOP]
        self._type = 'robot_state_change'
        self.state = state
        self.speed = speed

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RobotStateChange):
            return other.state == self.state and \
                   other.speed == self.speed
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<robot_state_change<state={self.state},speed={self.speed}>"
