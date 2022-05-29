"""Quick access to the core functionality."""

from .iinjectable_catalog import IInjectableCatalog
from .ilifetime_scope import ILifetimeScope, TInjectable
from .injectable_catalog import InjectableCatalog
from .injectable_discovery import find_injectables
from .lifetime_scope import LifetimeScope
