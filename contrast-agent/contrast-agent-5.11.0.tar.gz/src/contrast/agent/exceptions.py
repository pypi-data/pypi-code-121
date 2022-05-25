# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import hashlib
import traceback
import inspect
from contrast.agent.validator import Validator
from contrast.utils import get_installed_distributions
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class _Exception(Validator):
    VALIDATIONS = dict(
        type=dict(required=True, range=(1, 256)),
        module=dict(required=False, range=(1, 256)),
        value=dict(required=False, range=(0, 256)),
        stackframes=dict(required=True, range=(0, 128)),
    )

    def __init__(self, error: Exception):
        self.type = error.__class__.__name__
        # module would be location where this error is defined, not where raised.
        self.module = self._determine_module(error)
        self.value = str(error)
        self.stackframes = self._build_stackframes(error)

        self.validate()

    def _determine_module(self, error):
        """
        Find the str representing the path for where an error / exception is defined.
        """
        module = ""

        try:
            module = inspect.getfile(error.__class__)
        except TypeError as ex:
            if "is a built-in class" in str(ex):
                module = "builtin"

        return redact(module)

    def _build_stackframes(self, error):
        frames = []
        stacks = traceback.extract_tb(error.__traceback__)

        for stack in stacks:
            frames.append(
                _StackFrame(
                    # type is more appropriate for other languages so for now just
                    # make it the function name
                    stack_type=stack.name,
                    module=stack.filename,
                    function=stack.name,
                )
            )
        return frames

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.to_json()}"

    def to_json(self):
        return dict(
            type=self.type,
            module=self.module,
            value=self.value,
            stackFrames=[ex.to_json() for ex in self.stackframes],
        )


class _StackFrame(Validator):
    VALIDATIONS = dict(
        type=dict(required=True, range=(1, 256)),
        module=dict(required=False, range=(1, 256)),
        function=dict(required=True, range=(1, 256)),
        in_contrast=dict(required=False, default=False),
    )

    def __init__(self, stack_type, module, function):
        # type is meant to represent the more primitive types of functional langs,
        # for python we will make this the class type
        self.type = stack_type
        self.in_contrast = "/contrast" in module
        # Don't redact if we're in contrast code
        self.module = module if self.in_contrast else redact(module)
        self.function = function

        self.validate()

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.to_json()}"

    def to_json(self):
        return dict(
            type=self.type,
            module=self.module,
            function=self.function,
            inContrast=self.in_contrast,
        )


def redact(text):
    """
    Determine if to redact `text` by converting it to sha256 if
    `text` does not contain an accepted name.

    When in doubt, redact. We want to prevent reporting private customer data.

    :param text:
    :return: `text` or sha256 version of text
    """

    if not text:
        return ""

    text_lower = text.lower()

    accepted_third_party = ["contrast", "builtin"] + get_installed_distributions()

    for accepted in accepted_third_party:
        name = (
            accepted.lower()
            if isinstance(accepted, str)
            else accepted.project_name.lower()
        )

        # length check is a fail safe to not do a too-short str comparison.
        if len(name) > 2 and name in text_lower:
            return text

    return hashlib.sha256(text.encode()).hexdigest()[:7]
