from alira.instance import Instance
from alira.modules.module import Module


class Map(Module):
    def __init__(
        self,
        module_id: str = None,
        function: str = None,
        **kwargs,
    ):
        super().__init__(
            module_id=module_id or function.split(".")[-1],
            **kwargs,
        )

        self.function = function
        self.kwargs = kwargs

    def run(self, instance: Instance, **kwargs):
        fn = self._load_function(self.function)
        if fn is None:
            raise RuntimeError(f"Unable to load function {self.function}")

        arguments = {**self.kwargs, **kwargs}

        result = fn(instance=instance, **arguments)

        if not isinstance(result, dict):
            raise RuntimeError("The result of the map operation must be a dictionary")

        return result
