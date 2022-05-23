from __future__ import annotations

import uuid
from django.apps import apps
from django.db import models

from django_omise.omise import omise
from django_omise.utils.core_utils import (
    update_or_create_from_omise_object,
)

from django.utils.translation import gettext_lazy as _

from typing import Optional, Dict
from .managers import DeletableManager

from typing import List


class OmiseMetadata(models.Model):

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Custom metadata for this object."),
    )

    def set_metadata(self, metadata: Optional[Dict] = None) -> "OmiseBaseModel":
        """
        Set the object's medata both on Omise and the Django object.

        :params metadata: A dictionary for medatada

        :returns: Currenct object.
        """

        if metadata is None:
            metadata = {}

        omise_object = self.omise_class.retrieve(self.id)
        omise_object.update(metadata=metadata)

        self.metadata = metadata
        self.save()

        return self

    class Meta:
        abstract = True


class OmiseBaseModel(models.Model):

    id = models.CharField(max_length=255, primary_key=True)
    livemode = models.BooleanField()
    data = models.JSONField(default=dict, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    NON_DEFAULT_FIELDS = [
        "id",
        "livemode",
        "date_created",
        "date_updated",
        "data",
        "uid",
    ]

    def __str__(self):
        return f"Omise{self.__class__.__name__}: {self.id}"

    class Meta:
        abstract = True
        ordering = [
            "-date_created",
        ]

    def get_omise_object(self) -> omise.Base:
        """Fetch the object from Omise's server."""
        return self.omise_class.retrieve(self.id)

    def reload_from_omise(self) -> OmiseBaseModel:
        """Reload the data from Omise's server and return the saved object"""
        omise_object = self.omise_class.retrieve(self.id)
        return self.__class__.update_or_create_from_omise_object(
            omise_object=omise_object
        )

    @classmethod
    def update_or_create_from_omise_object(
        cls,
        omise_object: omise.Base,
        ignore_fields: Optional[List[str]] = None,
        uid: Optional[uuid.UUID] = None,
    ) -> OmiseBaseModel:
        """
        Update existing charge or create a new charge from Omise Charge object.

        :param omise_object: An instance of Omise object
        :param ignore_fields optional: List of field names to ignore
        :param uuid optional: A unique id for new object.

        :returns: An instance of current class
        """
        if ignore_fields is None:
            ignore_fields = []

        fields = cls._meta.get_fields()

        defaults = {}

        for field in fields:
            if field.name == "metadata":
                defaults["metadata"] = getattr(
                    omise_object,
                    field.name,
                ).__dict__.get("_attributes")
                continue

            if field.name in cls.NON_DEFAULT_FIELDS:
                continue

            if field.name in ignore_fields:
                continue

            if callable(getattr(omise_object, field.name, None)):
                continue

            if (
                getattr(getattr(omise_object, field.name, None), "object", None)
                == "list"
            ):
                values = getattr(omise_object, field.name)
                for value in values:
                    update_or_create_from_omise_object(omise_object=value)
                continue

            if type(field) in [models.ForeignKey, models.OneToOneField]:
                value = getattr(omise_object, field.name, None)

                if value is None or type(value) is str:
                    defaults[f"{field.name}_id"] = value
                else:

                    new_object = update_or_create_from_omise_object(omise_object=value)

                    defaults[field.name] = new_object

                continue

            if (
                type(field) in [models.TextField, models.CharField]
                and getattr(omise_object, field.name, None) is None
            ):
                defaults[field.name] = ""
                continue

            if (
                getattr(omise_object, field.name, None) is None
                and field.null == False
                and field.default
            ):
                defaults[field.name] = field.default()
                continue

            defaults[field.name] = getattr(omise_object, field.name, None)

        new_object, created = cls.objects.update_or_create(
            pk=omise_object.id,
            livemode=omise_object.livemode,
            defaults=defaults,
        )

        if uid:
            new_object.uid = uid
            new_object.save()

        return new_object


class OmiseDeletableModel(models.Model):
    deleted = models.BooleanField(
        default=False,
        help_text=_("Whether this object is marked as deleted on Omise's server"),
    )

    objects = DeletableManager()

    class Meta:
        abstract = True
