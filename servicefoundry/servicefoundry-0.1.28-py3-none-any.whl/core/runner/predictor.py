from .interceptor import Interceptor
from .service_wrapper import ServiceWrapper


class Predictor:
    def __init__(self, predict_file):
        self.interceptor = Interceptor.create(predict_file)

    def invoke(self, function, **kwargs):
        return self.interceptor.invoke(function, **kwargs)

    def predict(self, **kwargs):
        return self.invoke("predict", **kwargs)

    def get_dependencies(self):
        return self.interceptor.get_dependencies()

    def get_functions(self):
        return self.interceptor.get_functions()

    def create_service(self, parameters):
        return ServiceWrapper(parameters, self.interceptor)

    def close(self):
        self.interceptor.close()

    @classmethod
    def load_predictor(cls, file_name):
        return cls(file_name)


def create_service(predictor, parameters):
    if isinstance(predictor, str):
        predictor = Predictor.load_predictor(predictor)
    elif isinstance(predictor, Predictor):
        predictor = predictor
    else:
        raise TypeError(
            f"`predictor` should either be a name of a file (`str`) or a `Predictor` instance."
        )
    return predictor.create_service(parameters)
