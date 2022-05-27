"""
This module contains object types that are part of OVITO's data pipeline system.

**Pipelines:**

  * :py:class:`Pipeline`
  * :py:class:`Modifier` (base class)

**Data sources:**

  * :py:class:`StaticSource`
  * :py:class:`FileSource`
  * :py:class:`PythonScriptSource`

"""

__all__ = ['Pipeline', 'Modifier', 'StaticSource', 'FileSource', 'PythonScriptSource', 'ModifierInterface']