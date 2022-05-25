
class Process:

    def __init__(self, uuid: str, name: str, tasks: [str], description: str = "", _type: str = ''):
        """
        :param name: name of the task
        :param tasks: list of task uuid's
        :param description: a description of the task
        :param uuid: UUID of the task
        """
        self._type = 'process'
        self.uuid = uuid
        self.name = name
        self.tasks: [str] = tasks
        self.description = description

        if len(tasks) <= 0:
            raise ValueError("A task must have a least 1 subtask or component!")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Process):
            return other.uuid == self.uuid and \
                   other.name == self.name and \
                   other.tasks == self.tasks and \
                   other.description == self.description
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<id={self.uuid},name={self.name},tasks={self.tasks},description={self.description}>"


class ProcessMessage:

    def __init__(self, process_uuid: str, message: str, _type: str = ''):
        self._type = 'process_message'
        self.process_uuid = process_uuid
        self.message = message

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ProcessMessage):
            return other.process_uuid == self.process_uuid and other.message == self.message
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"<process_uuid={self.process_uuid},message={self.message}>"
