class Observer:
    """Implement this class to implement Kamzik3 Observer."""

    def subject_update(self, key, value, subject):
        """
        Receive an subject update.

        :param mixed key: subject name
        :param mixed value: subject value
        :param Subject subject: Subject
        """
        raise NotImplementedError("Not implemented")

    def attach_to_subject(self, subject):
        """
        Connect Observer to Subject.

        :param Subject subject: Subject
        """
        subject.attach_observer(self)

    def detach_subject(self, subject):
        """
        Connect Observer to Subject.

        :param Subject subject: Subject
        """
        subject.detach_observer(self)
