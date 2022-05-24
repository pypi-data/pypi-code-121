"""
    Module d'interprétation de la configuration
"""
from __future__ import annotations

import os
import time

from pydantic import BaseModel
import xarray as xr

from mfire.settings import Settings, get_logger
from mfire.utils import MD5, current_process
from mfire.utils.xr_utils import ArrayLoader, LoaderError


# Logging
LOGGER = get_logger(name="composite.base.mod", bind="composite.base")


class BaseComposite(BaseModel):
    """Cette classe Abstraite permet de mettre en place le design pattern "Composite"
    i.e. une structure arborescente d'objets à produire.

    Exemple : j'ai un aléa, qui contient plusieurs niveaux de risques; chaque niveau
    contient des évenements élémentaires; chaque événement est défini par des champs
    et des masques. Pour produire chacun des éléments cités ici on a besoin de produire
    les éléments fils.

    Cette classe rassemble les attributs et méthodes communes aux Field, Geo, Element,
    Level, Component, etc.
    """

    _data: xr.DataArray = None
    _cached_filenames: dict = dict()

    class Config:
        """ Cette classe Config permet de contrôler de comportement de pydantic
        """

        underscore_attrs_are_private = True
        arbitrary_types_allowed = True

    @property
    def _cached_attrs(self) -> dict:
        return {"data": ArrayLoader}

    @property
    def cached_basename(self) -> str:
        """Property created to define the basename of the cached file

        Returns:
            str: self cached file's basename
        """
        return f"{self.__class__.__name__}/{self.hash}"

    def cached_filename(self, attr: str = "data") -> str:
        """Property created to define the filename of the cached file
        and creating the directory if it doesn't exists

        Returns:
            str: self cached file's full name
        """
        if self._cached_filenames.get(attr, None) is None:
            self._cached_filenames[attr] = os.path.join(
                Settings().cache_dirname, f"{self.cached_basename}_{attr}"
            )
        return self._cached_filenames[attr]

    def is_cached(self) -> bool:
        """Method to know whether a composite object is already cached or not

        Returns:
            bool: Whether the object is cached.
        """
        return all(
            os.path.isfile(self.cached_filename(attr)) for attr in self._cached_attrs
        )

    def load_cache(self) -> bool:
        """Load a given file if a filename is given
        or load a cached file if it exists.

        Args:
            filename (str, optional): File to open.
                Defaults to None.

        Raises:
            ValueError: Raised if no filename is given and no file is cached.
        """
        if not self.is_cached():
            raise ValueError(f"{self!r} not cached, you must compute it before.")

        for attr, loader_class in self._cached_attrs.items():
            filename = self.cached_filename(attr)
            try:
                loader = loader_class(filename=filename)
                self.__setattr__(f"_{attr}", loader.load())
            except (LoaderError, FileNotFoundError) as excpt:
                LOGGER.warning(f"Exception caught during cache loading : {repr(excpt)}")
                return False
        return True

    def dump_cache(self):
        """Method for dumping the self._data into a netcdf file.
        If no filename is provided, it is dumped to cache.

        Args:
            filename (str, optional): File to dump. Defaults to None.
        """
        for attr, loader_class in self._cached_attrs.items():
            filename = self.cached_filename(attr)
            if not os.path.isfile(filename):
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                tmp_hash = MD5(f"{current_process().name}-{time.time()}").hash
                tmp_filename = filename + f"{tmp_hash}.tmp"
                try:
                    loader = loader_class(filename=tmp_filename)
                    dump_status = loader.dump(data=self.__getattribute__(f"_{attr}"))
                    err_msg = ""
                except LoaderError as excpt:
                    dump_status = False
                    err_msg = excpt
                if dump_status:
                    os.rename(tmp_filename, filename)
                else:
                    LOGGER.warning(
                        f"Failed to dump attribute '_{attr}' to tmp cached file "
                        f"{tmp_filename} using {loader_class}. {err_msg}"
                    )

    def _compute(self, **kwargs) -> xr.DataArray:
        """Private method to actually produced the composite no matter what.

        Returns:
            xr.DataArray: computed data
        """
        return xr.DataArray(**kwargs)

    def compute(self, keep_data: bool = False, **kwargs) -> xr.DataArray:
        """Generic compute method created to provide computed composite's data.
        If the self._data already exist or if composite's data has already been
        cached, we use what has already been computed.
        Else we use the private _compute method to compute composite's data.

        Args:
            keep_data (bool, optional): Whether to keep the computed data in memory.
                ! Warning ! : don't keep to much thing on memory or it's gonna explode.
                Defaults to False.

        Returns:
            xr.DataArray: Computed data
        """
        if self._data is None:
            if not (self.is_cached() and self.load_cache()):
                self._data = self._compute(**kwargs)
                self.dump_cache()

        if keep_data:
            # si on souhaite conserver le self._data on le renvoie en l'état
            return self._data

        # sinon on l'efface et on renvoie le résultat
        tmp_da = self._data
        self._data = None
        return tmp_da

    def reset(self):
        """Reset the self._data and self._cached_filename
        To use when attributes are change on the fly.
        """
        self._data = None
        for attr in self._cached_filenames:
            self._cached_filenames[attr] = None

    def clean(self):
        """Clean the cache and reset the object.
        To use when attributes are change on the fly.
        """
        if self.is_cached():
            for filename in self._cached_filenames.values():
                os.remove(filename)
        self.reset()

    @property
    def hash(self) -> str:
        """Hash of the object

        Returns:
            str: hash
        """
        return MD5(obj=self.dict(), length=-1).hash

    def new(self) -> BaseComposite:
        """Create a brand new - not computed yet - copy of self

        Returns:
            BaseComposite: Not computed copy of self
        """
        return self.__class__(**self.dict())
