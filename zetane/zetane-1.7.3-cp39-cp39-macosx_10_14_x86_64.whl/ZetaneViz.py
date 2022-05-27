

class ZetaneViz:
    def __init__(self):
        pass


    def show_input(self, inputs):
        return self


class TorchViz:


    def create_torch_model(self, model, inputs):
        return self


    def model_inference(self, inputs, sleep=None):
        """
        Args:
            inputs (torch.tensor): Input torch tensor(s)
        """
        return self


    def model_debug(self, inputs):
        """
        Args:
            inputs (torch.tensor): Input torch tensor(s)
        """
        return self


class OnnxViz:


    def create_onnx_model(self, path):
        return self


    def model_inference(self, inputs, sleep=None):
        return self


    def model_debug(self, inputs):
        return self


class KerasViz:


    def create_keras_model(self, model, input_spec):
        return self


    def model_inference(self, inputs, sleep=None):
        return self


    def model_debug(self, inputs):
        return self
