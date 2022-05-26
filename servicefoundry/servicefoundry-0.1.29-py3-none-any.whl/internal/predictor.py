from servicefoundry.internal.interceptor.interceptor import Interceptor


class Predictor:
    def __init__(self, predict_file):
        self.predict_file = predict_file
        self.interceptor = Interceptor.create(predict_file)

    def invoke(self, function, **kwargs):
        return self.interceptor.invoke(function, **kwargs)

    def predict(self, **kwargs):
        return self.invoke("predict", **kwargs)

    def get_dependencies(self):
        return self.interceptor.get_dependencies()

    def get_functions(self):
        return self.interceptor.get_functions()

    def close(self):
        self.interceptor.close()

    @classmethod
    def load_predictor(cls, file_name):
        return cls(file_name)
