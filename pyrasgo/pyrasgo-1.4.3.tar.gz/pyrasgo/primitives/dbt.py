"""
dbt Primitives
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Union


class DbtSourceParent:
    """
    Represents a dbt source
    """

    def __init__(
        self,
        name: str,
        config_args: Dict[str, Any] = None,
    ):
        """
        Initializes a DbtSource class
        """
        self.name = name
        self.config_args = config_args


class DbtSource:
    """
    Represents a dbt source
    """

    def __init__(
        self,
        name: str,
        fqtn: str,
        parent: DbtSourceParent,
        columns_schema: Dict[str, str] = None,
        config_args: Dict[str, Any] = None,
    ):
        """
        Initializes a DbtSource class
        """
        self.name = name
        self.parent = parent
        self.fqtn = fqtn
        self.columns_schema = columns_schema
        self.config_args = config_args


class DbtModel:
    """
    Represents a dbt model
    """

    def __init__(
        self,
        name: str,
        sql_definition: str,
        fqtn: str,
        columns_schema: Dict[str, str] = None,
        config_args: Dict[str, Any] = None,
    ):
        """
        Initializes a DbtModel class
        """
        self.name = name
        self.sql_definition = sql_definition
        self.fqtn = fqtn
        self.columns_schema = columns_schema
        self.config_args = config_args

    # def save_file(
    #     self,
    #     models_directory: Union[os.PathLike, str],
    #     config_args: Dict[str, Any] = None,
    #     ref_tables: Dict[str, str] = None,
    # ) -> None:
    #     """
    #     Writes this dbt model to a file in the models dir
    #     """
    #     from pyrasgo.utils.dbt import save_model_file

    #     if self.config_args:
    #         if config_args:
    #             config_args = self.config_args.update(config_args)
    #         else:
    #             config_args = self.config_args
    #     return save_model_file(
    #         sql_definition=self.sql_definition,
    #         output_directory=Path(models_directory),
    #         file_name=self.name,
    #         schema=self.schema,
    #         config_args=config_args,
    #         ref_tables=ref_tables,
    #         include_schema=True if self.schema else False,
    #     )


class DbtProject:
    """
    Represents a dbt project
    """

    def __init__(
        self,
        name: str,
        project_directory: Union[os.PathLike, str],
        models_directory: Union[os.PathLike, str],
        models: List[DbtModel],
        sources: List[DbtSource],
        model_args: Dict[str, Any] = None,
    ):
        """
        Initializes a DbtProject class
        """
        self.name = name
        self.project_directory = Path(project_directory)
        self.models_directory = Path(models_directory)
        self.models = models
        self.sources = sources
        self.model_args = model_args

    def save_files(self):
        """
        Writes all dbt models in this project as files to the project dir
        """
        from pyrasgo.utils.dbt import write_dbt_files

        return write_dbt_files(
            project_name=self.name,
            project_directory=self.project_directory,
            models_directory=self.models_directory,
            models=self.models,
            sources=self.sources,
            model_args=self.model_args,
        )
