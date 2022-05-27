"""Generates a schema file from a data file."""
from pathlib import Path
from typing import Any

import fire

from bitfount.data.datasources.csv_source import CSVSource
from bitfount.data.schema import BitfountSchema


def gen_schema(data_file: str, schema_file: str, **datasource_kwargs: Any) -> None:
    """Generates a schema file from a data file.

    Args:
        data_file: The path to the data file.
        schema_file: The path to save the generated schema to.
        datasource_kwargs: Additional keyword arguments to pass to the schema
                           alongside the data.
    """
    # Create data source
    datasource = CSVSource(Path(data_file).expanduser())

    # Create schema
    if datasource_kwargs:
        print(f"CSVSource kwargs: {datasource_kwargs}")
    schema = BitfountSchema(datasource, **datasource_kwargs)

    # Save schema
    schema.dump(Path(schema_file).expanduser())


def main() -> None:
    """Script entry point."""
    fire.Fire(gen_schema)


if __name__ == "__main__":
    main()
