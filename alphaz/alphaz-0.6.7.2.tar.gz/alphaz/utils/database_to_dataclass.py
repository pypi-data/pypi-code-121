import argparse
import os

FILE_STRUCTURE = """ 
from timeit import default_timer as timer
from datetime import timedelta

from datetime import datetime
from alphaz.models.main import (
    AlphaDataclass, 
    dataclass,
    List
)

@dataclass
class {class_name}(AlphaDataclass):
{fields}

def load_{table_name_lower}(limit:int=None) -> List[{class_name}]:
    print("Loading table {table_name} ...")
    start = timer()
    from core import core
    DB = core.db

    raw_results = DB.get_query_results("select * from {table_name}" + ("" if not limit else " LIMIT " + str(limit)), bind="{bind}")
    end = timer()
    print("Table {table_name} loaded in " + str(timedelta(seconds=end-start)))
    
    print("Converting table {table_name} ...")
    start = timer()
    results = [{class_name}.auto_map_from_dict(x) for x in raw_results]
    end = timer()
    print("Table {table_name} loaded in " + str(timedelta(seconds=end-start)))
    return results
"""

INIT_CONTENT = ""


def get_field_type(field_type_raw):
    field_type = None
    if "int" in field_type_raw:
        field_type = "int"
    elif "float" in field_type_raw:
        field_type = "float"
    elif "var" in field_type_raw:
        field_type = "str"
    elif "bit" in field_type_raw:
        field_type = "bool"
    elif "date" in field_type_raw:
        field_type = "datetime"
    elif "text" in field_type_raw:
        field_type = "str"
    elif "double" in field_type_raw:
        field_type = "float"
    else:
        print(f"type {field_type_raw} is not recognized")
    return field_type


def convert_database_structure_to_dataclass(db, bind, output, tables=None):
    print(f"Converting {bind} ...")
    tables = [x.lower() for x in tables]
    global INIT_CONTENT
    db_type = db.app.db_cnx[bind]["type"]
    owner = db.app.db_cnx[bind]["user"]

    class_fields = {}

    if db_type == "oracle":
        database_structure = db.get_query_results(
            query=f"SELECT * FROM ALL_TAB_COLS where owner = '{owner.upper()}'",
            bind=bind,
        )
        for d in database_structure:
            if not "table_name" in d:
                continue
            table_name = d["table_name"]

            if tables is not None:
                if not table_name.lower() in tables:
                    print(f"Table {table_name} if not in {tables}")
                    continue
            if not table_name in class_fields:
                class_fields[table_name] = []
            field_type = get_field_type(d["data_type"])
            class_fields[table_name].append(
                f"   {d['column_name'].lower()}: {field_type}"
            )
    else:
        database_structure = db.get_query_results(query="SHOW TABLES;", bind=bind)

        for structure in database_structure:
            print(f"Analyzing {structure}")
            table_name = list(structure.values())[0]
            if tables is not None:
                if not table_name.lower() in tables:
                    print(f"Table {table_name} if not in {tables}")
                    continue
            table_structure = db.get_query_results(
                query=f"DESCRIBE {table_name};", bind=bind
            )

            fields = []
            for field_structure in table_structure:
                field_type = get_field_type(field_structure["Type"])
                if field_type is not None:
                    fields.append(
                        f"   {field_structure['Field'].lower()}: {field_type}"
                    )
            class_fields[table_name] = fields

    modules = []
    for table_name, fields in class_fields.items():
        class_name = "".join([x.lower().capitalize() for x in table_name.split("_")])
        directory = f"{os.getcwd()}{os.sep}{output}{os.sep}{bind.lower()}"
        output_file_content = FILE_STRUCTURE.format(
            class_name=class_name,
            fields="\n".join(fields),
            table_name_lower=table_name.lower(),
            table_name=table_name,
            bind=bind,
        )
        os.makedirs(directory, exist_ok=True)

        output_file_path = f"{directory}{os.sep}{table_name.lower()}.py"
        with open(output_file_path, "w") as f:
            f.write(output_file_content)
        module_path = f"{bind.lower()}.{table_name.lower()}"
        modules.append(module_path)

    INIT_CONTENT += "\n".join([f"from .{x} import *" for x in modules])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Alpha", description="Api")
    parser.add_argument(
        "--configuration", "-c", help="Set configuration", required=True
    )
    parser.add_argument("--output", "-o", help="Output directory", required=True)
    parser.add_argument(
        "--binds", "-b", type=str, nargs="+", help="Binds", required=True
    )
    parser.add_argument("--tables", "-t", type=str, nargs="+", help="Tables")

    args = parser.parse_args()

    os.environ["ALPHA_CONF"] = args.configuration
    from core import core

    core.prepare_api(configuration=args.configuration)

    core.api.init()

    for bind in args.binds:
        convert_database_structure_to_dataclass(
            core.db, bind=bind, output=args.output, tables=args.tables
        )

    init_dir = f"{os.getcwd()}{os.sep}{args.output}"
    init_path = f"{init_dir}{os.sep}__init__.py"
    os.makedirs(init_dir, exist_ok=True)
    with open(init_path, "w") as f:
        f.write(INIT_CONTENT)
