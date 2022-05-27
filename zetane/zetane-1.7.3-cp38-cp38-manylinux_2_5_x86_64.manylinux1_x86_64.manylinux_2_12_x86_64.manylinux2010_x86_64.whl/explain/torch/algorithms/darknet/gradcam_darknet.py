

class CamExtractorDarknet:
    def __init__(self, model, target_layer):
        pass


    def save_gradient(self, grad):
        return self


    def forward_pass_on_convolutions(self, x):
        return self


    def forward_pass(self, x):
        return self


class GradCamDarknet:
    """
    produces class activation map
    """
    def __init__(self, model, target_layer):
        pass


    def generate_cam(self, input_image, target_class=None):
        return self
