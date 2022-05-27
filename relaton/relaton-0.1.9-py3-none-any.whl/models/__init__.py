"""
Some of Relaton’s bibliographic item specifications implemented
as typed dictionaries, dataclasses and Pydantic models.

They are mixed for a few reasons:

- Since we don’t want to always validate every item we instantiate,
  we can’t use Pydantic’s models for simpler types,
  so we use plain dataclasses.
- Where we encounter reserved words, we use ``TypedDict()``
  instantiations. They have a big drawback (no defaults on optionals),
  so their use is as limited as possible.
- Dataclass instantiation may cause a ``TypeError`` when given
  unexpected data, which is especially bad at root model level.
  That, and generally Pydantic’s support for dataclasses
  is poor—so we use regular Pydantic models at higher levels.

.. important:: Dumping a model as a dictionary using Pydantic
               may not dump members that are dataclass instances.
               To obtain a full dictionary,
               use :func:`common.pydantic.unpack_dataclasses` utility.
"""

from .bibdata import *
from .copyrights import *
from .people import *
from .orgs import *
from .contacts import *
from .links import *
from .dates import *
from .strings import *


__all__ = (
  'BibliographicItem',
  'DocID',
  'Series',
  'BiblioNote',
  'Contributor',
  'Relation',
  'Person',
  'PersonName',
  'PersonAffiliation',
  'Organization',
  'Contact',
  'Date',
  'Link',
  'Title',
  'GenericStringValue',
  'FormattedContent',
)

