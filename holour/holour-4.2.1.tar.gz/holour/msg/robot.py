
class RobotState:

    def __init__(self, state: str, moving: bool, active: bool, target_speed: float, actual_speed: float, _type: str = ''):
        self._type = 'robot_state'
        self.state = state
        self.moving = moving
        self.active = active
        self.target_speed = target_speed
        self.actual_speed = actual_speed

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RobotState):
            return other.state == self.state and \
                   other.moving == self.moving and \
                   other.active == self.active and \
                   other.target_speed == self.target_speed and \
                   other.actual_speed == self.actual_speed
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<robot_state<state={self.state},moving={self.moving},active={self.active}," \
               f"target_speed={self.target_speed},actual_speed={self.actual_speed}>"

    @staticmethod
    def translate_state_code(state: int) -> (str, bool, bool):
        # Return: state-string, is_moving, is_active (the last two are something I made up)
        if state == 0:
            return "Stopping", True, False
        elif state == 1:
            return "Stopped", False, False
        elif state == 2:
            return "Playing", True, True
        elif state == 3:
            return "Pausing", True, False
        elif state == 4:
            return "Paused", False, False
        elif state == 5:
            return "Stopped", False, False
        else:
            return "Unknown", False, False


class RobotStateChange:
    START = 'start'
    PAUSE = 'pause'
    STOP = 'stop'

    def __init__(self, state: str, speed: float, _type: str = ''):
        assert state in [RobotStateChange.START, RobotStateChange.PAUSE, RobotStateChange.STOP]
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
