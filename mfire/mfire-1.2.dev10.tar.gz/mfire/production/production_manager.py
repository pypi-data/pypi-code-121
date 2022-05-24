"""
processing of different productions
"""

from __future__ import annotations

import os
import tarfile
from typing import List, Tuple

from pydantic import BaseModel

from mfire.settings import get_logger, Settings
from mfire.utils import JsonFile, Parallel
from mfire.composite import AbstractComponentComposite, ProductionComposite
from mfire.text.text_manager import TextManager
from mfire.output import OutputAdapter, BaseOutputProduction

LOGGER = get_logger(name="production.mod", bind="production")


class ProductionManager(BaseModel):
    """
    This class manages the implementation of promethee products by
    loading the metronome configuration file.
    """

    productions: List[ProductionComposite]

    @property
    def components(self) -> List[AbstractComponentComposite]:
        components = []
        for production in self.productions:
            components.extend(production.components)
        return components

    @classmethod
    def load(cls, filename: str) -> ProductionManager:
        config = JsonFile(filename).load()
        if isinstance(config, list):
            return cls(productions=config)
        if isinstance(config, dict):
            return cls(productions=list(config.values()))
        LOGGER.error(
            "Failed to retrieve productions from configuration file. "
            "JsonFile does not contain objects of type list or dict."
        )
        return cls(productions=[])

    @staticmethod
    def compute_single(
        component: AbstractComponentComposite,
    ) -> Tuple[str, BaseOutputProduction]:
        """computes a single component, produces the text associated with it, and export
        it to the corresponding output model.

        Args:
            component (AbstractComponentComposite): Component to compute.

        Returns:
            BaseOutputProduction: Final result of the computation.
        """
        # creating the ids for the logging
        log_ids = {
            "production_id": component.production_id,
            "production_name": component.production_name,
            "component_id": component.id,
            "component_name": component.name,
            "component_type": component.type,
        }
        if component.type == "risk":
            log_ids.update(hazard_name=component.hazard_name)
        # step A : compute the component
        LOGGER.debug("Step A starting", **log_ids)
        try:
            risks_ds = component.compute()
            if not bool(risks_ds) and component.type == "risk":
                LOGGER.warning(
                    "Computed risk empty: avoiding text generation "
                    "and risk output formatting",
                    **log_ids,
                )
                return component.production_id, None
        except FileNotFoundError as excpt:
            LOGGER.error(
                "Missing data to produce component.", missing=excpt.filename, **log_ids
            )
            return component.production_id, None
        LOGGER.debug("Step A done", **log_ids)

        # step B : producing the texts associated with
        LOGGER.debug("Step B starting", **log_ids)
        text_manager = TextManager(component=component)
        texts = dict()
        for geo_id in component.geos:
            try:
                LOGGER.debug("Step B : geo starting", geo_id=geo_id, **log_ids)
                text = text_manager.compute(geo_id)
                LOGGER.debug("Step B : geo done", geo_id=geo_id, **log_ids)
            except Exception:
                LOGGER.error(
                    "Failed to generate text on geo",
                    geo_id=geo_id,
                    **log_ids,
                    exc_info=True,
                )
                text = (
                    "Erreur dans output lors de la generation de ce "
                    "commentaire. Voir les logs pour plus de details."
                )
            texts[geo_id] = text
        LOGGER.debug("Step B done", **log_ids)
        # step C: exporting to the output model
        LOGGER.debug("Step C starting", **log_ids)
        adapter = OutputAdapter(component=component, texts=texts)
        result = adapter.compute()
        LOGGER.debug("Step C done", **log_ids)
        return component.production_id, result

    @staticmethod
    def concat_and_dump(
        production_id: str,
        productions: List[BaseOutputProduction],
        dump_dir: str = None,
    ) -> str:
        if not productions:
            LOGGER.warning("Productions empty or None", production_id=production_id)
            return None
        LOGGER.debug("Concat starting", production_id=production_id)
        concat_production = BaseOutputProduction.concat(productions)
        LOGGER.debug("Concat done", production_id=production_id)
        LOGGER.debug("Dumping starting", production_id=production_id)
        filename = concat_production.dump(dump_dir=dump_dir)
        LOGGER.debug("Dumping done", production_id=production_id)
        return filename

    def compute(self, nproc: int = 1, dump_dir: str = None):
        """Computing components, related texts and exporting the result

        Args:
            nproc (int, optional): Numbers of CPU to use. Defaults to 1.
            dump_dir (str, optional): Directory where to dump the results.
                Defaults to None.
        """
        if dump_dir is None:
            dump_dir = Settings().output_dirname

        productions_filenames = []

        result = dict()

        def append_result(res: Tuple[str, BaseOutputProduction]):
            """callback function to append a value to the result dict.

            Args:
                res (Tuple[str, BaseOutputProduction]): Key-Value pair
                    to add to the result dict.
            """
            key, value = res
            if value is None:
                return None
            result.setdefault(key, []).append(value)

        parallel = Parallel(nproc)
        for component in self.components:
            name = f"{component.production_name} ({component.name} "
            if hasattr(component, "hazard_name"):
                name += component.hazard_name
            name += ")"

            parallel.apply(
                self.compute_single,
                args=(component,),
                callback=append_result,
                name=name,
            )

        parallel.run(timeout=Settings().timeout)
        parallel.clean()
        LOGGER.debug("Step 1 (multiproc) done")

        # step 2: concatenating and dumping results
        LOGGER.debug("Step 2 (multiproc) starting")
        for production_id, productions_list in result.items():
            parallel.apply(
                self.concat_and_dump,
                args=(production_id, productions_list, dump_dir,),
                callback=productions_filenames.append,
                name=production_id,
            )
        parallel.run(timeout=(Settings().timeout / 2))
        LOGGER.debug("Step 2 (multiproc) done.")

        # step 3 : archiving all the results in a single tar file
        LOGGER.debug("Step 3 starting")
        archive_name = os.path.join(dump_dir, "promethee_msb_poc.tgz")
        with tarfile.open(archive_name, "w:gz") as tar:
            for filename in productions_filenames:
                if filename is None:
                    continue
                full_path = os.path.abspath(filename)
                base_name = os.path.basename(filename)
                # On ajoute le fichier en utilisant son path global
                # Par contre on lui donne le nom local
                tar.add(full_path, arcname=base_name)
        LOGGER.debug("Step 3 done")


__all__ = ["ProductionManager"]
