# -*- coding: utf-8 -*-
from datetime import datetime
from typing import AnyStr, List, Optional

from attr import define, field, validators

# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from .fields import (
    CheckboxField,
    CommentsField,
    CreatedByField,
    DateField,
    DateTimeField,
    EmailField,
    FirstCreatedField,
    GridReferenceField,
    HistoryField,
    IPField,
    JSONField,
    LastUpdatedByField,
    LastUpdatedField,
    MultilineField,
    MultiSelectField,
    MultiSelectReferenceField,
    RadioButtonField,
    RichTextField,
    SingleSelectField,
    SingleSelectReferenceField,
    TelephoneField,
    TextField,
    TimeField,
    TimespanField,
    TrackingField,
    UrlField,
    UserGroupField,
    UsersGroupsField,
)


@define()
class Application:
    description: AnyStr = field()
    acronym: AnyStr = field()
    trackingFieldId: AnyStr = field(eq=False, order=False)
    maxTrackingId: int = field()
    name: AnyStr = field()
    fields: List = field(
        validator=validators.instance_of(
            (
                CommentsField,
                HistoryField,
                DateTimeField,
                TimespanField,
                TimeField,
                DateField,
                FirstCreatedField,
                LastUpdatedField,
                SingleSelectField,
                MultiSelectField,
                SingleSelectReferenceField,
                MultiSelectReferenceField,
                GridReferenceField,
                MultilineField,
                TextField,
                TelephoneField,
                EmailField,
                UrlField,
                IPField,
                RichTextField,
                JSONField,
                TrackingField,
                UserGroupField,
                UsersGroupsField,
                CreatedByField,
                LastUpdatedByField,
                RadioButtonField,
                CheckboxField,
            )
        )
    )
    id: AnyStr = field(eq=False, order=False)
    version: int = field(eq=False, order=False)
    createdDate: Optional[datetime] = field(kw_only=True, eq=False, order=False)
    createdByUser: dict = field(default={})
    modifiedByUser: dict = field(default={})
    permissions: dict = field(default={})
    modifiedDate: Optional[datetime] = field(kw_only=True, eq=False, order=False)
    workspaces: List = field(default=None)
    createWorkspace: bool = field(default=None)
    timeTrackingEnabled: bool = field(default=None)
    selectionFields: List = field(default=None)
    uid: AnyStr = field(default=None, eq=False, order=False)
    disabled: bool = field(default=None)
    layout: List = field(eq=False, order=False, default=[])

    def __init__(self, **kwargs):
        from ..base import Base

        Base().scrub(kwargs)
        self.__attrs_init__(**kwargs)

    def __attrs_post_init__(self):
        if self.fields:
            field_list = []
            for sfield in self.fields:
                for item in [
                    CommentsField,
                    HistoryField,
                    DateTimeField,
                    TimespanField,
                    TimeField,
                    DateField,
                    FirstCreatedField,
                    LastUpdatedField,
                    SingleSelectField,
                    MultiSelectField,
                    SingleSelectReferenceField,
                    MultiSelectReferenceField,
                    GridReferenceField,
                    MultilineField,
                    TextField,
                    TelephoneField,
                    EmailField,
                    UrlField,
                    IPField,
                    RichTextField,
                    JSONField,
                    TrackingField,
                    UserGroupField,
                    UsersGroupsField,
                    CreatedByField,
                    LastUpdatedByField,
                    RadioButtonField,
                    CheckboxField,
                ]:
                    try:
                        field_list.append(item(**sfield))
                    except Exception as e:
                        continue
            self.fields = field_list
