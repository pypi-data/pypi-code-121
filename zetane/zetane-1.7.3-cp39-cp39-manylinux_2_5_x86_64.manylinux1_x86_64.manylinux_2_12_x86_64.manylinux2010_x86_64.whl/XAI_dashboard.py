

class XAIDashboard:
    """
    The XAIDashboard class provides the base of the XAI template.

    It requires a PyTorch or Keras model and a zcontext object, and visualizes the provided XAI algorithms, the original image and the predicted classes within panels. It also allows for visualizing certain XAI algorithms that work on a per-layer basis (e.g. Grad-CAM) on the model itself, under the associated Conv nodes.

    Attributes:
        model (torch.nn.Module or tf.Keras.nn.Model): Model to be used for XAI algorithms as well as visualization
        zcontext (zetane.context.Context): The context object all visual elements will be sent to
        zmodel (zetane.render.model.Model): The Zetane Model (converted from the Keras/PyTorch model) to be visualized
        algorithms (list(str)): The list of XAI algorithms to be visualized
        scale_factor (int): The scaling factor to scale images appropriately in the Zetane panels.
        xai_panel (zetane.render.panel.Panel): The main panel object that houses all other panels
        org_img_panel (zetane.render.panel.Panel): Panel for visualizing the original image
        topk_panel (zetane.render.panel.Panel): Panel for visualizing the top k predictions of the model as well as the target prediction if available
        explain_panel (zetane.render.panel.Panel): Panel that visualizes all global XAI algorithms
        radio_panel (zetane.render.panel.Panel): Panel to visualize the radio buttons for toggling per-layer XAI algorithms
    """
    def __init__(self, model, zcontext):
        """

        Args:
            model (torch.nn.Module or tf.Keras.nn.Model): Model to be used for XAI algorithms and visualization
            zcontext (zetane.context.Context): The context object all visual elements will be sent to
        """
        pass


    def set_model(self, model):
        """
        Updates the model used for XAI algorithms and visualization.

        Args:
            model (torch.nn.Module or tf.Keras.nn.Model): Model to be used for XAI algorithms as well as visualization

        Returns:
            None

        """
        return self


    def set_algorithms(self, algorithms):
        """
        Updates the list of XAI algorithms to be visualized.

        Args:
            algorithms (list(str)): The list of XAI algorithms to be visualized

        Returns:
            None

        """
        return self


    def normalize(self, x):
        """
        Applies 0-1 normalization.

        Args:
            x (ndarray): The numpy array to be normalized

        Returns:
            ndarray: The normalized array

        """
        return self


    def softmax(self, x):
        """Compute softmax values for each sets of scores in x."""
        return self


    def explain_torch(self, img_data, target_class=None, label_class=None, class_dict=None, algorithms=None, mean=None, std=None, opset_version=12):
        """
        Runs the explainability template on a PyTorch classification model. Given an image path or data, computes the desired XAI algorithms and the top k predicted classes, and displays them along with the model and the original image.

        Args:
            img_data (str, ndarray or torch.Tensor): The input image in filepath or Numpy/torch array form
            target_class (int): The output class for which the gradients will be calculated when generating the XAI images (default: None)
            label_class (int): If available, the ground truth class label (default: None)
            class_dict (dict): The class dictionary for the class names
            algorithms (list(str)): The list of XAI algorithms to be visualized
            mean (list(float)): The mean values for each channel if any in normalization is applied to the original image (default: None)
            std (list(float)): The standard deviation values for each channel if any in normalization is applied to the original image (default: None)
            opset_version (int): ONNX opset version (default: 12)

        Returns:
            None
        """
        return self


    def explain_keras(self, img_data, target_class=None, label_class=None, class_dict=None, algorithms=None, loss_fn=None, postprocess_fn=None):
        """
        Runs the explainability template on a Keras classification model. Given an image path or data, computes the desired XAI algorithms and the top k predicted classes, and displays them along with the model and the original image.

        Args:
            img_data (str or ndarray): The input image in filepath or Numpy array form
            target_class (int): The output class for which the gradients will be calculated when generating the XAI images (default: None)
            label_class (int): If available, the ground truth class label (default: None)
            class_dict (dict): The class dictionary for the class names
            algorithms (list(str)): The list of XAI algorithms to be visualized
            loss_fn (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)
            postprocess_fn (function): Custom postprocessing function to extract class probabilities from model outputs if needed. If set to None, this defaluts to indexing into the 1D outputs array, assuming softmaxed outputs (default: None)

        Returns:
            None
        """
        return self
