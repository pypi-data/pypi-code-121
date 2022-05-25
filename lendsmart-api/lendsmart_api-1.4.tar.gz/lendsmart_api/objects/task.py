from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class Task(Base):
    """
    A Task objects structure.
    """

    task = {
        "id": Property(identifier=True),
        "type_meta": Property(mutable=True, filterable=True),
        "object_meta": Property(mutable=True, filterable=True),
        "due_date": Property(),
        "assigned_at": Property(),
        "comment": Property(),
        "task_type": Property(),
        "invite_type": Property(),
        "created_at": Property(),
        "status": Property(),
        "updated_at": Property(),
        "metadata": Property()
    }