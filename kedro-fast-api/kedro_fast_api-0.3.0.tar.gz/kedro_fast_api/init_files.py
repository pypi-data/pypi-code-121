import shutil
import os
from kedro_fast_api.utils import project_path


def create_init_files(kedro_project: str) -> None:
    pipeline_path = f"src/{kedro_project}/pipelines/api_pipeline"
    catalog_path = f"conf/base/api_pipeline/" 

    os.makedirs(pipeline_path, exist_ok=True)
    os.makedirs(catalog_path, exist_ok=True)

    init_file = project_path("init_files/api_pipeline/__init__.py")
    nodes = project_path("init_files/api_pipeline/nodes.py")
    pipline = project_path("init_files/api_pipeline/pipeline.py")
    catalog = project_path("init_files/catalog.yml")
    api_yml = project_path("init_files/api.yml")

    shutil.copy(init_file, pipeline_path)
    shutil.copy(nodes, pipeline_path)
    shutil.copy(pipline, pipeline_path)
    shutil.copy(catalog, catalog_path)
    shutil.copy(api_yml, "conf/")
