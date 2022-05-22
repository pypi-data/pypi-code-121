import ckan.plugins as p


from ..interfaces import IFlakes


class FlakesTestPlugin(p.SingletonPlugin):
    p.implements(IFlakes)

    def get_flake_schemas(self):
        return {"empty": {}}
