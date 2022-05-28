"""Script-specific exceptions."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.


class ScriptError(Exception):
    """Generic script error."""


class NodeError(ScriptError):
    """Something wrong with finding/processing a node."""
