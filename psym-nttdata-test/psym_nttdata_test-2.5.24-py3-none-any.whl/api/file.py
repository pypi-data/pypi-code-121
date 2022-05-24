#!/usr/bin/env python3


import glob
import os
from datetime import datetime
from typing import Generator, Optional

import filetype
from psym.client import SymphonyClient
from psym.common.data_class import Document, Location

from ..graphql.enum.image_entity import ImageEntity
from ..graphql.input.add_image_input import AddImageInput
from ..graphql.mutation.add_image import AddImageMutation
from ..graphql.mutation.delete_image import DeleteImageMutation


def list_dir(directory_path: str) -> Generator[str, None, None]:
    files = list(glob.glob(os.path.join(directory_path, "**/**"), recursive=True))
    for file_path in set(files):
        if os.path.isfile(file_path):
            yield file_path


def add_file(
    client: SymphonyClient,
    local_file_path: str,
    entity_type: str,
    entity_id: str,
    category: Optional[str] = None,
    document_category_id: Optional[str] = None,
) -> None:
    """This function adds file to an entity of a given type.

    :param local_file_path: Local system path to the file
    :type local_file_path: str
    :param entity_type: One of existing options ["LOCATION", "WORK_ORDER", "SITE_SURVEY", "EQUIPMENT"]
    :type entity_type: str
    :param category: File category name
    :type category: str, optional
    :param document_category_id: Document category id
    :type document_category_id: int, optional

    :raises:
        FailedOperationException: on operation failure

    :return: None

    **Example**

    .. code-block:: python

        document_category = PsymClient.get_document_category_by_names(
            client=client_symp,
            location_type_name="Country",
            doc_category_name="Correo de notificación"
        )
        location = client.get_location({("Country", "LS_IND_Prod_Copy")})
        client.add_file(
            local_file_path="./document.pdf",
            entity_type="LOCATION",
            entity_id=location.id,
            document_category_id=document_category.id
        )
    """
    entity = {
        "LOCATION": ImageEntity.LOCATION,
        "WORK_ORDER": ImageEntity.WORK_ORDER,
        "SITE_SURVEY": ImageEntity.SITE_SURVEY,
        "EQUIPMENT": ImageEntity.EQUIPMENT,
    }.get(entity_type, ImageEntity.LOCATION)
    add_image(
        client, local_file_path, entity, entity_id, category, document_category_id
    )


def add_files(
    client: SymphonyClient,
    local_directory_path: str,
    entity_type: str,
    entity_id: str,
    category: Optional[str] = None,
    document_category_id: Optional[int] = None,
) -> None:
    """This function adds all files located in folder to an entity of a given type.

    :param local_directory_path: Local system path to the directory
    :type local_directory_path: str
    :param entity_type: One of existing options ["LOCATION", "WORK_ORDER", "SITE_SURVEY", "EQUIPMENT"]
    :type entity_type: str
    :param category: File category name
    :type category: str, optional
    :param document_category_id: Document category id
    :type document_category_id: int, optional

    :raises:
        FailedOperationException: on operation failure

    :return: None

    **Example**

    .. code-block:: python

        document_category = PsymClient.get_document_category_by_names(
            client=client_symp,
            location_type_name="Country",
            doc_category_name="Correo de notificación"
        )
        location = client.get_location({("Country", "LS_IND_Prod_Copy")})
        client.add_files(
            local_directory_path="./documents_folder/",
            entity_type="LOCATION",
            entity_id=location.id,
            document_category_id=document_category.id
        )
    """
    for file in list_dir(local_directory_path):
        add_file(client, file, entity_type, entity_id, category, document_category_id)


def add_location_image(
    client: SymphonyClient,
    local_file_path: str,
    location: Location,
    document_category_id: Optional[str] = None,
) -> None:
    """This function adds image to existing location.

    :param local_file_path: Local system path to the file
    :type local_file_path: str
    :param location: Existing location object, could be retrieved from

        * :meth:`~psym.api.location.get_location`
        * :meth:`~psym.api.location.add_location`
    :param document_category_id: Document category id
    :type document_category_id: int, optional

    :type location: :class:`~psym.common.data_class.Location`

    :raises:
        FailedOperationException: on operation failure

    :return: None

    **Example**

    .. code-block:: python
        document_category = PsymClient.get_document_category_by_names(
            location_type_name="Country",
            doc_category_name="Correo de notificación",
        )
        location = client.get_location({("Country", "LS_IND_Prod_Copy")})
        client.add_location_image(
            local_file_path="./document.pdf",
            location=location,
            document_category_id=document_category.id
        )
    """
    add_image(
        client,
        local_file_path,
        ImageEntity.LOCATION,
        location.id,
        documentCategoryId=document_category_id,
    )


def delete_document(client: SymphonyClient, document: Document) -> None:
    """This function deletes existing document.

    :param document: Document object
    :type document: :class:`~psym.common.data_class.Document`

    :raises:
        FailedOperationException: on operation failure

    :return: None

    **Example**

    .. code-block:: python

        client.delete_document(document=document)
    """
    delete_image(client, document.parent_entity, document.parent_id, document.id)


def add_image(
    client: SymphonyClient,
    local_file_path: str,
    entity_type: ImageEntity,
    entity_id: str,
    category: Optional[str] = None,
    documentCategoryId: Optional[str] = None,
) -> None:
    file_type = filetype.guess(local_file_path)
    file_type = file_type.MIME if file_type is not None else ""
    img_key = client.store_file(local_file_path, file_type, False)
    file_size = os.path.getsize(local_file_path)

    AddImageMutation.execute(
        client,
        AddImageInput(
            entityType=entity_type,
            entityId=entity_id,
            imgKey=img_key,
            fileName=os.path.basename(local_file_path),
            fileSize=file_size,
            modified=datetime.utcnow(),
            contentType=file_type,
            category=category,
            documentCategoryId=documentCategoryId,
        ),
    )


def delete_image(
    client: SymphonyClient, entity_type: ImageEntity, entity_id: str, image_id: str
) -> None:
    DeleteImageMutation.execute(
        client, entityType=entity_type, entityId=entity_id, id=image_id
    )
