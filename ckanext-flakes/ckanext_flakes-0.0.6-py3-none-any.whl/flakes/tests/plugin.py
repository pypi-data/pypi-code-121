import ckan.plugins as p

from ..interfaces import IFlakes


def identity(payload):
    return payload


class FlakesTestPlugin(p.SingletonPlugin):
    p.implements(IFlakes)

    def get_flake_schemas(self):
        return {"empty": {}}

    def get_flake_factories(self):
        return {"identity": identity}
