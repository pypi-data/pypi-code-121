"""
    Some good utils for serializer
"""
from rest_framework.fields import HiddenField, CurrentUserDefault


class ContextFieldSerializer:
    """
        Get current voice
    """
    requires_context = True

    def __init__(self, field):
        self.field = field

    def __call__(self, serializer_field):
        return serializer_field.context[self.field]

    def __repr__(self):
        return f'{self.__class__.__name__}()'


def get_hidden_field(field):
    """
        Use this function in serializer field and send data in context
    """
    return HiddenField(default=ContextFieldSerializer(field))


def get_current_user_default():
    """
        Use this function in serializer field for access to current user
    """
    return HiddenField(default=CurrentUserDefault())
