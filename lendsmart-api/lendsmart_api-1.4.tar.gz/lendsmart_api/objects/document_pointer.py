from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class DocumentPointer(Base):
    """
    A DocumentPointer is something a LendSmart customer uploads.
    """
    api_endpoint = '/document_pointers'

    properties = {
        "id": Property(identifier=True),
        "type_meta": Property(mutable=True, filterable=True),
        "object_meta": Property(mutable=True, filterable=True),
        "remote_bucket": Property(),
        "remote_filename": Property(),
        "remote_folder": Property(),
        "created_by": Property(),
        "updated_at": Property(),
        "metadata": Property()
    }
