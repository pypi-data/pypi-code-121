

class Model:
    """The model class creates a reference to a machine learning model in the Zetane engine and renders the model architecture. Additionally, the model has data about the model internals and inputs. There are UI elements that allow the model intermediate information to be expanded and explored in order to examine weight and convolutional feature maps.

    Returns:
        Model: A zetane model object
    """
    from enum import Enum
    class Verbosity(Enum):
        """An enumeration of the debug levels to set for debugging model issues

        :meta private:
        """
        DEFAULT = 'default'
        TRACE = 'trace'
        DEBUG = 'debug'
        INFO = 'info'
        WARNING = 'warning'
        ERROR = 'error'
        FATAL = 'fatal'
    def __init__(self, nsocket, visualize_inputs=False):
        pass


    def update(self, inputs=None):
        """Send data to Zetane to update the model.

        Args:
            inputs (str, numpy.array): file path to the inputs (.npy or .npz files), or numpy array of raw data.

        Returns:
            self: .
        """
        return self


    def onnx(self, model, run_model_check=False):
        """Update model data with an ONNX model

        Args:
            model (str): File path to a `.onnx` file.
            run_model_check(bool): Runs the onnx model validity checker, which will throw errors for models that are improperly structured.

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def tensorflow(self, sess, inputs, outputs, names=('saved_model.ckpt', 'tensorflow_model.onnx'), run_model_check=False):
        """Update model data with a tensorflow model

        * Temporarily saves Tensorflow model to a checkpoint file and freezes the graph during call.
        * Requires installation of tensorflow.

        Args:
            sess (str): Running tensorflow session.
            inputs (list): List of input names in tf graph, formatted as node_name:port_id.
            outputs (list): List of output names in tf graph, formatted as node_name:port_id.
            names (tuple): Tuple of size 2 with filenames for checkpoint and onnx files.
            run_model_check(bool): Runs the onnx model validity checker, which will throw errors for models that are improperly structured.

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def keras(self, model, input_signature, opset=13, output_path='keras_model.onnx', run_model_check=False):
        """Update model data with a keras model

        Args:
            model (tf.keras.Model): Keras model to be rendered.
            input_signature (tf.TensorSpec, np.array): a tf.TensorSpec or a numpy array defining the shape/dtype of the input
            output_path (str): Name for the keras model save file. Define it uniquely if rendering multiple models.
            run_model_check(bool): Runs the onnx model validity checker, which will throw errors for models that are improperly structured.

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def torch(self, model, inputs, name='torch_model.onnx', run_model_check=False, opset_version=12, input_names=None, output_names=None):
        """Update model data with a pytorch model

        Args:
            model (torch.nn.Module): Pytorch model to be rendered.
            inputs (torch.Tensor): Pytorch tensor to serve as input to the network. This can be the actual model input which will be displayed in Zetane, or a dummy tensor with the proper shape.
            name (str): Name for the pytorch model. Define it uniquely if rendering multiple models.
            run_model_check(bool): Runs the onnx model validity checker, which will throw errors for models that are improperly structured.

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def model(self, model=None, run_model_check=False, expose_onnx_outputs=False, overwrite_onnx=False, overwrite_conv_names=False):
        """
            Set the absolute file path to the .onnx object.

        Args:
            model (str): relative path to .onnx object

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def prep_model_for_onnx_runtime(self, overwrite=False, run_model_validity_checker=False, verbose=False, overwrite_conv_names=False):
        return self


    def inputs(self, inputs=None):
        """Set the numpy file to be loaded into the input of the ONNX model.

        Args:
            inputs (str, numpy.array): path to the .npy/.npz file or a numpy array of the raw data.

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def execute_model(self, execute_model=True):
        """Sets whether the model will run an inference pass in the Zetane engine.

        Args:
            execute_model (bool): Sets whether the model will run an inference pass.

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def visualize_inputs(self, visualize=True):
        """
            Set up the model to either visualize the inputs or not.

        Args:
            visualize (bool): if true, the model's inputs will be visualized when they are loaded in.

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def run_model_checker(self, run_checker=True):
        """
            If true, will run ONNX Model validity checker every time we expose nodes for ONNX Runtime.

        Args:
            run_checker (bool): If true, will run onnx model checker when exposing nodes for ONNX Runtime.

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def disable_gpu(self, disable=True):
        """
            Tell model to avoid using GPU for inference and prefer CPU passes. (Only valid if using deprecated runtime).

        Args:
            disable (bool): If true, GPU will not be used for inference passes.

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def use_hierarchical_layout(self, use_hierarchical=True):
        """
            Model will be loaded using a hierarchical layout (aka dot/sugiyama/layered layout). Otherwise, will use a basic layout.

        Args:
            use_hierarchical (bool): If true, ONNX Model will be rendered using hierarchical graph layout

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def use_deprecated_runtime(self, use_deprecated=False):
        """
            Tell model to use deprecated runtime (Libtorch) instead of ONNX Runtime for inference passes.

        Args:
            use_deprecated (bool): If true, model will use deprecated runtime (Libtorch) for inference passes.

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def set_verbosity(self, verbosity=Verbosity.DEFAULT):
        """
            Set the verbosity of the logs in-engine when executing the ONNX model.

        Args:
            verbosity (Verbosity): The verbosity of the logs printed by the engine during inference.

        Returns:
            Model: Returns self so that calls can be chained.
        """
        return self


    def set_output_toggle(self, state=True):
        """
                    If True, will retrieve and store output data for each ONNX node, else will not.

                Args:
                    state (bool): If true, all nodes will be toggled on to store their output data by default.

                Returns:
                    Model: Returns self so that calls can be chained.
                """
        return self


    def xai_previews(self, name_preview_pairs, xai_type, clearfields=False):
        return self
