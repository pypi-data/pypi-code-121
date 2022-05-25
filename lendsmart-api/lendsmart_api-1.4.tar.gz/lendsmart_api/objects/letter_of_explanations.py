from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class LetterOfExplanation(Base):
    """
    A Letter of explanation objects structure
    """

    letter_of_explanations = {
        "id": Property(identifier=True),
        "type_meta": Property(mutable=True, filterable=True),
        "object_meta": Property(mutable=True, filterable=True),
        "asks": Property(),
        "created_at": Property(),
        "status": Property(),
    }