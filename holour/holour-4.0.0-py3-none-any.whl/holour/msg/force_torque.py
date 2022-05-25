from holour.msg import Vector3


class ForceTorque:

    def __init__(self, force: Vector3, torque: Vector3, _type: str = ''):
        self._type = 'force_torque'
        self.force = force
        self.torque = torque

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ForceTorque):
            return other.force == self.force and other.torque == self.torque
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"ForceTorque<force={self.force}, torque={self.torque}>"
