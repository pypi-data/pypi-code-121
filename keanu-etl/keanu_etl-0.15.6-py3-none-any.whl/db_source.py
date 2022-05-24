from .data_store import DataStore

class DBSource(DataStore):
    def __init__(self, spec, name=None, dry_run=False):
        super().__init__(name, spec, dry_run)

    def environ(self):
        env = {}

        if self.schema:
            env["SOURCE"] = self.schema

        if 'env' in self.config:
            env = {**self.config['env'], **env}

        return env

    def table(self, table):
        if self.schema:
            return "{}.{}".format(self.schema, table)
        else:
            return table
