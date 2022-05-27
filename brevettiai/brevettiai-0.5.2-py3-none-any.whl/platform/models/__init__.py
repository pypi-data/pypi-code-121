"""
Implementations of interfaces of platform features

* Annotation: as annotated using the platform annotation feature
* Job: as defined by the platform job functionality
"""
from .platform_backend import PlatformBackend, backend
from .camelmodel import CamelModel
from .iomodel import IoBaseModel
from .tag import Tag
from .dataset import Dataset
from .job import Job, JobSettings
