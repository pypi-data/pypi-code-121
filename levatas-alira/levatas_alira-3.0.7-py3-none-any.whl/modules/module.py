import logging
from importlib import import_module


class ConnectionError(Exception):
    """
    We raise this exception when we can't connect to a third-party, online service.
    We expect this to happen whenever there's no internet connection.

    This exception is useful to reattempt operations when they are being processed
    by the Redis queue.
    """

    pass


class InternalError(Exception):
    """
    We raise this exception when there's an error in the execution of a module that
    is unrelated to the lack of connectivity.

    This exception is useful to signal to the pipeline runner that we shouldn't keep
    bubbling up this exception.
    """

    pass


class Module(object):
    def __init__(
        self,
        pipeline_id: str = None,
        configuration_directory: str = None,
        module_id=None,
        **kwargs,
    ):
        self.pipeline_id = pipeline_id
        self.configuration_directory = configuration_directory

        if module_id:
            self.module_id = module_id

    def _load_function(self, function_name: str):
        if function_name is None:
            return None

        try:
            module_path, _, fn_name = function_name.rpartition(".")
            function = getattr(import_module(module_path), fn_name)
            logging.info(f"Loaded function {function_name}")

            return function
        except Exception:
            raise InternalError(f"Unable to load function {function_name}")


class Dependency(Module):
    def __init__(
        self,
        function: str = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.function = function
        self.kwargs = kwargs

    def get(self, **kwargs):
        fn = self._load_function(self.function)
        if fn is None:
            raise RuntimeError(f"Unable to load function {self.function}")

        arguments = {"module": self, **self.kwargs, **kwargs}

        return fn(**arguments)


class Connection(Module):
    def __init__(
        self,
        module_id=None,
        schedule=None,
        **kwargs,
    ):
        super().__init__(module_id=module_id, **kwargs)

        max_retries = 180
        interval = 60
        self.schedule = schedule or [max_retries, interval]

    def run(self, instance, **kwargs):
        if not self.is_online():
            raise ConnectionError("No internet connection")

    def is_online(self):
        """
        This function checks whether there's internet connection.
        """

        import http.client as httplib

        connection = httplib.HTTPSConnection("8.8.8.8", timeout=5)
        try:
            connection.request("HEAD", "/")
            return True
        except Exception:
            return False
        finally:
            connection.close()
