from os import path, environ
import re
import yaml
import click
from .batch import Batch
from .db_source import DBSource
from .db_destination import DBDestination
from .sql_transform import SQLTransform
from .py_transform import PyTransform


class ConfigError(click.ClickException):
    pass


def configuration_from_argument(file_or_dir):
    if path.isfile(file_or_dir) and (
        file_or_dir.endswith("yml") or file_or_dir.endswith("yaml")
    ):
        conf = load(file_or_dir)
    elif path.isdir(file_or_dir):
        if not "DATABASE_URL" in environ:
            raise click.BadParameter(
                "SQL directory as argument but DATABASE_URL not set",
                param_hint="DATABASE_URL",
            )
        if not "SOURCE" in environ:
            raise click.BadParameter(
                "SQL directory as argument but SOURCE not set", param_hint="SOURCE"
            )

        conf = [
            {"source": {"db": {"schema": environ["SOURCE"]}}},
            {"destination": {"db": {"url": environ["DATABASE_URL"]}}},
            {"transform": {"sql": {"directory": file_or_dir}}},
        ]
    else:
        raise click.Abort("Cannot use config {}".format(file_or_dir))
    return conf


def load(file_path):
    with open(file_path) as f:
        txt = f.read()

        def get_var(m):
            return environ[m.group(1)]

        txt = re.subn(r"[$]{([A-Za-z1-9_]+)}", get_var, txt)[0]

        return yaml.safe_load(txt)


def build_batch(mode, configuration):
    batch = Batch(mode)
    for step in configuration:
        if "source" in step:
            step = step["source"]
            if "db" in step:
                source = DBSource(
                    step, name=step.get("name"), dry_run=batch.is_dry_run
                )
                batch.add_source(source)
            else:
                raise ConfigError("config file: source without db spec")
        elif "destination" in step:
            step = step["destination"]
            if "db" in step:
                destination = DBDestination(
                    step, name=step.get("name"), dry_run=batch.is_dry_run
                )
                batch.add_destination(destination)
            else:
                raise ConfigError("config file: destination without db spec")
        elif "transform" in step:
            step = step["transform"]
            if "sql" in step:
                dst = batch.destination
                if "source" in step:
                    source_spec = lambda s: s.name == step["source"] and s.local == True
                else:
                    source_spec = lambda s: s.local == True
                src = batch.find_source(source_spec)

                if src is None:
                    raise ConfigError("No local source found for SQL transform")

                if "directory" in step["sql"]:
                    transform = SQLTransform(
                        mode, src, dst, directory=step["sql"]["directory"]
                    )
                elif "file" in step["sql"]:
                    transform = SQLTransform(
                        mode, src, dst, filename=step["sql"]["file"]
                    )
                else:
                    raise ConfigError(
                        "config file: sql transform without directory or file field"
                    )

                batch.add_transform(transform)

            elif "py" in step:
                dst = batch.destination
                if "source" in step:
                    source_spec = lambda s: s.name == step["source"]
                else:
                    source_spec = lambda s: True
                src = batch.find_source(source_spec)

                if "directory" in step["py"]:
                    transform = PyTransform(
                        mode, src, dst, directory=step["py"]["directory"]
                    )
                elif "file" in step["py"]:
                    transform = PyTransform(mode, src, dst, filename=step["py"]["file"])
                else:
                    raise ConfigError(
                        "config file: py transform without directory or file field"
                    )

                batch.add_transform(transform)

            else:
                raise ConfigError("config file: not a sql or py transform")
    return batch
