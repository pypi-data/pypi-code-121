from pydmt.api.one_source_one_target import OneSourceOneTarget


class Fail(OneSourceOneTarget):
    """
    This is a builder that fails.
    Why do we need it? Tests
    Why does it need a source and target?
    Because otherwise it would not get triggered
    """
    def build(self):
        raise ValueError("fail")
