from os import path, makedirs, listdir, unlink
from shutil import rmtree

from slug import slug
import yaml


class sql_code(str):
    """
    Wrap SQL code in sql_code() to have it dumped as multi-line string.
    """

    pass


def sql_code_representer(dumper, data):
    """
    Registers sql_code as scalar representer of block style (|)
    """
    return dumper.represent_scalar(u"tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(sql_code, sql_code_representer)


class Splitter:
    """
    Maps between export json file and directory/file structure, wich is easier to maintain in a source repository (to see diffs, merge, etc)

    Requirements:
    - yaml format (more diff friendly, because it's line based)
    - multiline values in block scalar format
    - all the map keys are sorted
    """

    def __init__(self, directory):
        self.directory = directory

    def store(self, json):
        self.clean_directory()
        self.store_mappings(json)
        self.store_datamodel(json)
        self.store_items(json["items"])

    def store_mappings(self, node):
        mappings = node["mappings"]

        self.store_to(mappings, "mappings")

    def store_datamodel(self, node):
        dbs = node["datamodel"]["databases"]

        for db_spec in dbs.values():
            db_file = slug(db_spec["name"])
            self.store_to(db_spec, "databases/{}".format(db_file))

    def store_items(self, items, prefix=[]):
        for i in items:
            if i["model"] == "card" or i["model"] == "dashboard":
                if i["model"] == "card":
                    self.format_query_as_block(i)

                file_name = slug(i["name"])
                loc = path.join("items", *prefix, file_name)

                self.store_to(i, loc)

            elif i["model"] == "collection":
                dir_name = slug(i["name"])
                loc = path.join("items", *prefix, dir_name, "__meta__")

                col_items = i["items"]
                del i["items"]
                self.store_to(i, loc)
                self.store_items(col_items, prefix + [dir_name])

    def format_query_as_block(self, card):
        if "dataset_query" in card and "native" in card["dataset_query"]:
            card["dataset_query"]["native"]["query"] = sql_code(
                card["dataset_query"]["native"]["query"]
            )

    def store_to(self, node, loc):
        floc = path.join(self.directory, loc) + ".yaml"
        fdir = path.dirname(floc)
        makedirs(fdir, 0o755, True)

        # Avoid overwriting files if two have the same slug (like card and dashboard)
        floc1 = floc
        idx = 1
        while path.exists(floc1):
            floc1 = "{}-{}".format(floc, idx)
            idx + 1

        with open(floc, "w") as out:
            yaml.dump(node, stream=out)

    def clean_directory(self):
        if not path.exists(self.directory):
            makedirs(self.directory, 0o755, True)
            return

        for f in listdir(self.directory):
            if f.startswith("."):
                continue
            try:
                unlink(path.join(self.directory, f))
            except IsADirectoryError:
                rmtree(path.join(self.directory, f))

    def load(self):
        data = {}

        data["items"] = self.load_items()
        data["datamodel"] = self.load_datamodel()
        data["mappings"] = self.load_from("mappings.yaml")

        return data

    def load_datamodel(self):
        databases = {}
        for f in listdir(path.join(self.directory, "databases")):
            db = self.load_from(path.join("databases", f))
            databases[str(db["id"])] = db
        return {"databases": databases}

    def load_items(self, prefix=[]):
        items = []
        ls = listdir(path.join(self.directory, "items", *prefix))
        ls.sort()
        for f in ls:
            if f == "__meta__.yaml":
                continue

            if path.isdir(path.join(self.directory, "items", *prefix, f)):
                col = self.load_from(path.join("items", *prefix, f, "__meta__.yaml"))

                col["items"] = self.load_items(prefix + [f])
                items.append(col)
            else:
                item = self.load_from(path.join("items", *prefix, f))
                items.append(item)
        return items

    def load_from(self, loc):
        floc = path.join(self.directory, loc)
        # fdir = path.dirname(floc)
        return yaml.load(open(floc))
