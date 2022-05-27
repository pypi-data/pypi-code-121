# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
class Validator(object):
    def validate(self):
        """
        At this time, any field (optional or required) that does not pass validation
        will cause the entire message to not be reported. In the future we could:

        1. if the field is optional but doesn't pass validation, skip the field
        :return:
        """
        assert self.VALIDATIONS, "Child class must implement VALIDATIONS"

        for field_name, validations in self.VALIDATIONS.items():
            # The field_name we're validating must be defined as an attr to the class.
            try:
                field_value = getattr(self, field_name)
            except AttributeError:
                raise ValidationException(
                    self, field_name, "field is not an attr of the class"
                )

            required = validations.get("required")

            # if field is required but it isn't populated.
            if required and not field_value:
                raise ValidationException(
                    self, field_name, "field is required but empty"
                )

            range_val = validations.get("range")

            # python range is exclusive so +1 to make it inclusive of top value
            if range_val is not None and len(field_value) not in range(
                range_val[0], range_val[1] + 1
            ):
                raise ValidationException(
                    self, field_name, "field is outside required range length"
                )


class ValidationException(Exception):
    def __init__(self, klass, field_name, orig_msg):
        message = f"Unable to validate field `{field_name}` for class `{klass.__class__.__name__}`: {orig_msg}"
        super().__init__(message)
