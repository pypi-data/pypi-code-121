"""
dbt functions
"""
import copy
import logging
import os
from pathlib import Path
import re
import string
from typing import Any, Dict, List, Union

import yaml

from pyrasgo.primitives import Dataset, DbtModel, DbtSource, DbtSourceParent

__all__ = [
    "dataset_to_model",
    "dataset_to_source",
    "save_model_file",
    "write_dbt_files",
]


logger = logging.getLogger("dbt")

DBT_MODEL_CONFIG_TEMPLATE = """
  config(
    {config_args}
  )
"""

DBT_PROJECT_TEMPLATE = {
    "name": "",
    "version": "1.0.0",
    "config-version": 2,
    "profile": "default",
    "model-paths": ["models"],
    "analysis-paths": ["analyses"],
    "test-paths": ["tests"],
    "seed-paths": ["seeds"],
    "macro-paths": ["macros"],
    "snapshot-paths": ["snapshots"],
    "target-path": "target",
    "log-path": "logs",
    "packages-install-path": "dbt_packages",
    "clean-targets": ["target", "dbt_packages"],
    "models": None,
}


def check_project_name(project_name: str):
    """
    Checks a project name for dbt compliance
    """
    allowed = set(string.ascii_lowercase + "_")
    if any(char for char in project_name.lower() if char not in allowed):
        logger.warning(
            "per dbt: Project names should contain only lowercase characters "
            "and underscores. A good package name should reflect your organization's "
            "name or the intended use of these models"
        )
    return project_name.lower()


def dataset_to_model(dataset: Dataset) -> DbtModel:
    """
    Primitive conversion: accepts a Rasgo Dataset and returns a DbtModel
    """
    database, schema, table = dataset.fqtn.split(".")
    return DbtModel(
        name=table,
        fqtn=dataset.fqtn,
        sql_definition=dataset._get_cte_for_dataset(),
        columns_schema=dataset.schema,
        config_args={"database": database, "schema": schema, "+materialized": dataset.table_type},
    )


def dataset_to_source(dataset: Dataset) -> DbtSource:
    """
    Primitive conversion: accepts a Rasgo Dataset and returns a DbtSource
    """
    database, schema, table = dataset.fqtn.split(".")
    return DbtSource(
        name=table,
        fqtn=dataset.fqtn,
        parent=DbtSourceParent(
            name=f"{database}_{schema}",
            config_args={"database": database, "schema": schema},
        ),
        columns_schema=dataset.schema,
    )


def determine_sources_and_refs(
    models: List[DbtModel],
    known_sources: List[DbtSource],
):
    """
    Finds fqtns in all models and splits them into two lists:
    refs: tables created by one of these models
    sources: tables created prior to / outside of these models
    """
    fqtn_set = set()
    source_set = {s.fqtn for s in known_sources}
    ref_dict = {m.fqtn: m.name for m in models}
    for model in models:
        fqtn_set.update(extract_fqtns(model.sql_definition))
    source_set.update({t for t in fqtn_set if t not in ref_dict.keys()})
    source_dict = {f"{d}.{s}.{n}": {"parent": f"{d}_{s}", "name": n} for d, s, n in (t.split(".") for t in source_set)}
    return source_dict, ref_dict


def extract_fqtns(sql_definition: str) -> List[str]:
    """
    Returns all fully qualified table names in a sql string
    """
    fqtn_list = re.findall(r"[^\w]+\.[^\w]+\.[^\w]+", sql_definition)
    return fqtn_list


def prepare_dbt_path(project_directory: Union[os.PathLike, str]) -> os.PathLike:
    """
    Checks for a specified filepath and creates one if it doesn't exist
    """
    project_directory = Path(project_directory)
    for dir_name in ("analyses", "dbt_packages", "logs", "macros", "models", "seeds", "target", "tests"):
        (project_directory / dir_name).mkdir(exist_ok=True, parents=True)
    return project_directory


def replace_sources_and_refs(
    sql_definition: str,
    model_name: str,
    ref_tables: Dict[str, str] = None,
    source_tables: Dict[str, Dict[str, str]] = None,
):
    """
    Combs a sql statement for fqtns and replaces them with dbt ref or source functions
    """
    if ref_tables:
        for fqtn, alias in ref_tables.items():
            if alias != model_name:
                sql_definition = sql_definition.replace(fqtn, "{} ref('{}') {}".format("{{", alias, "}}"))
    if source_tables:
        for fqtn, table_parts in source_tables.items():
            sql_definition = sql_definition.replace(
                fqtn, "{} source('{}', '{}') {}".format("{{", table_parts.get("parent"), table_parts.get("name"), "}}")
            )
    return sql_definition


def save_project_file(
    project_name: str,
    project_directory: Union[os.PathLike, str],
    overwrite: bool = False,
    model_args: Dict[str, Any] = None,
) -> Path:
    """
    Writes a yaml definition to a dbt project file
    """
    filepath = Path(project_directory) / "dbt_project.yml"
    if not os.path.exists(filepath) or overwrite:
        yml_definition = copy.deepcopy(DBT_PROJECT_TEMPLATE)
        yml_definition["name"] = project_name
        model_config = {project_name: model_args}
        yml_definition["models"] = model_config
        with open(filepath, "w") as _yaml:
            yaml.dump(data=yml_definition, Dumper=yaml.SafeDumper, stream=_yaml, sort_keys=False)
    return filepath


def save_model_file(
    sql_definition: str,
    output_directory: Union[os.PathLike, str],
    file_name: str,
    ref_tables: Dict[str, str] = None,
    source_tables: Dict[str, Dict[str, str]] = None,
) -> str:
    """
    Writes a sql script to a dbt model file
    """
    output_directory = Path(output_directory)
    file_name = f"{file_name}.sql" if file_name[-4:] != ".sql" else file_name
    model_name = file_name.replace(".sql", "")
    filepath = output_directory / file_name
    os.makedirs(output_directory, exist_ok=True)
    sql_definition = replace_sources_and_refs(
        sql_definition=sql_definition,
        model_name=model_name,
        ref_tables=ref_tables,
        source_tables=source_tables,
    )
    with open(filepath, "w") as _file:
        _file.write(sql_definition)
    return filepath


def save_schema_file(
    output_directory: Union[os.PathLike, str],
    file_name: str = None,
    models: List[DbtModel] = None,
    sources: List[DbtSource] = None,
) -> str:
    """
    Writes dbt model and source details to a schema yml file
    """
    file_name = file_name or "schema.yml"
    file_name = f"{file_name}.yml" if file_name[-4:] not in (".yml", "yaml") else file_name
    filepath = Path(output_directory) / file_name

    existing_schema = None
    if os.path.exists(filepath):
        with open(filepath, "r") as _file:
            existing_schema = yaml.safe_load(_file)
    schema_definition = existing_schema or {"version": 2, "sources": [], "models": []}

    # Add sources to schema
    for source in sources:
        columns_list = [{"name": row[0]} for row in source.columns_schema]
        parent_found = False
        source_found = False
        for p in schema_definition["sources"]:
            if p.get("name") == source.parent.name:
                parent_found = True
                for t in p.get("tables"):
                    if t.get("name") == source.name:
                        t["columns"] = columns_list
                        if source.config_args:
                            for k, v in source.config_args.items():
                                t[k] = v
                        source_found = True
        if not parent_found:
            schema_definition["sources"].append({"name": source.parent.name})
        if not source_found:
            source_dict = {"name": source.name, "columns": columns_list}
            if source.config_args:
                source_dict.update(source.config_args)
            for p in schema_definition["sources"]:
                if p.get("name") == source.parent.name:
                    if source.parent.config_args:
                        for k, v in source.parent.config_args.items():
                            p[k] = v
                    if not p.get("tables"):
                        p["tables"] = []
                    p["tables"].append(source_dict)

    # Add models to schema
    for model in models:
        columns_list = [{"name": row[0]} for row in model.columns_schema]
        model_found = False
        for m in schema_definition["models"]:
            if m.get("name") == model.name:
                m["columns"] = columns_list
                if model.config_args:
                    m["config"] = model.config_args
                model_found = True
        if not model_found:
            model_dict = {"name": model.name, "columns": columns_list}
            if model.config_args:
                model_dict.update({"config": model.config_args})
            schema_definition["models"].append(model_dict)
    with open(filepath, "w") as _file:
        yaml.dump(data=schema_definition, Dumper=yaml.SafeDumper, stream=_file, sort_keys=False)
    return filepath


def write_dbt_files(
    project_name: str,
    project_directory: Union[os.PathLike, str],
    models_directory: Union[os.PathLike, str],
    models: List[DbtModel],
    sources: List[DbtSource],
    model_args: Dict[str, Any] = None,
) -> str:
    """
    Saves a dbt_project.yml and model.sql files to a directory
    """
    check_project_name(project_name)
    project_directory = Path(project_directory)
    models_directory = Path(models_directory)
    prepare_dbt_path(project_directory)
    save_project_file(
        project_name=project_name,
        project_directory=project_directory,
        model_args=model_args,
    )
    source_tables, ref_tables = determine_sources_and_refs(models, sources)
    for model in models:
        save_model_file(
            sql_definition=model.sql_definition,
            output_directory=models_directory,
            file_name=f"{model.name}.sql",
            ref_tables=ref_tables,
            source_tables=source_tables,
        )
    save_schema_file(
        output_directory=models_directory,
        models=models,
        sources=sources,
    )
    return project_directory
