from copy import copy

from djangoldp.activities import errors
from djangoldp.activities.objects import ALLOWED_TYPES, Object, Actor


class Activity(Object):
    attributes = Object.attributes + ["actor", "object"]
    type = "Activity"
    # dictionary defining required attributes -> tuple of acceptable types
    required_attributes = {
        "actor": (Actor, str),
        "object": dict
    }

    def get_audience(self):
        audience = []
        for attr in ["to", "bto", "cc", "bcc", "audience"]:
            value = getattr(self, attr, None)
            if not value:
                continue

            if isinstance(value, str):
                value = [value]
            audience += value
        return set(audience)

    def strip_audience(self):
        new = copy(self)
        if getattr(new, "bto", None):
            delattr(new, "bto")
        if getattr(new, "bcc", None):
            delattr(new, "bcc")
        return new

    def _validate_type_id_defined(self, value):
        '''recursively ensures that all nested dict items define @id and @type attributes'''
        for item in value.items():
            if isinstance(item[1], dict):
                item_value = item[1]
                if '@type' not in item_value or '@id' not in item_value:
                    raise errors.ActivityStreamValidationError("all sub-objects passed in activity object must define @id and @type tags")
                self._validate_type_id_defined(item_value)


    def validate(self):
        for attr in self.required_attributes.keys():
            if not isinstance(getattr(self, attr, None), self.required_attributes[attr]):
                raise errors.ActivityStreamValidationError("required attribute " + attr + " of type "
                                                           + str(self.required_attributes[attr]))

        # validate that every dictionary stored in object has @id and @type
        self._validate_type_id_defined(self.__getattribute__("object"))

class Add(Activity):
    type = "Add"
    attributes = Activity.attributes + ["target"]
    required_attributes = {**Activity.required_attributes, "target": dict}


class Remove(Activity):
    type = "Remove"
    attributes = Activity.attributes + ["target", "origin"]

    def validate(self):
        super().validate()

        if not getattr(self, "target", None) and not getattr(self, "origin", None):
            raise errors.ActivityStreamValidationError("Invalid activity, no target or origin given")

        if getattr(self, "target", None) is not None:
            if not isinstance(self.target, dict):
                raise errors.ActivityStreamValidationError("Invalid target type, must be a dict")
        if getattr(self, "origin", None) is not None:
            if not isinstance(self.origin, dict):
                raise errors.ActivityStreamValidationError("Invalid origin type, must be a dict")


class Create(Activity):
    type = "Create"


class Update(Activity):
    type = "Update"


class Delete(Activity):
    type = "Delete"
    attributes = Activity.attributes + ["origin"]


class Follow(Activity):
    type = "Follow"

    def validate(self):
        super().validate()

        if isinstance(self.actor, Actor) and (self.actor.inbox is None and self.actor.id is None):
            raise errors.ActivityStreamValidationError("Must pass inbox or id with the actor to follow")


ALLOWED_TYPES.update({
    "Activity": Activity,
    "Add": Add,
    "Remove": Remove,
    "Create": Create,
    "Update": Update,
    "Delete": Delete,
    "Follow": Follow
})
