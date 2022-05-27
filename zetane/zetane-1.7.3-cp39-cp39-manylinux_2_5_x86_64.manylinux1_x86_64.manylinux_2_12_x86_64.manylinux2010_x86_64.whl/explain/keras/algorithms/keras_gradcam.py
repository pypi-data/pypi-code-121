

class Keras_gradcam:
    """keras gradcam provides the gradcam prediction of the image.
       Grad-CAM uses the gradients of any target concept (say logits for 'dog' or even a caption),
       flowing into the final convolutional layer to produce a coarse localization map
       highlighting the important regions in the image for predicting the concept.
    """
    def __init__(self, model=None):
        pass


    def load_image(self, path, preprocess=True):
        """Load and preprocess image.
        Args:
            path (String): Provides the path of the image 
            preprocess (Boolean): Check whether the image is preprocessed or Not.
        Returns:
        x(numpy array): numpy array of the image
        """
        return self


    def deprocess_image(self, x):
        """Deprocess the image.
        Args:
            x(numpy array): x is the numpy array 
        Returns:
        x(uint8): deprocessed uint array of the image array 
        """
        return self


    def normalize(self, x):
        """Utility function to normalize a tensor by its L2 norm
        Args:
            x(numpy array): x is the normalized numpy array
        """
        return self


    def build_guided_model(self):
        """Function returning modified model.

        Changes gradient function for all ReLu activations
        according to Guided Backpropagation.
        """
        return self


    def guided_backprop(self, input_model, images, layer_name):
        """Guided Backpropagation method for visualizing input saliency.
        Args:
            input_model: Provides the input_model for calculating guided_backprop 
            images(list): list of images.
            layer_name: Name of the layer for which guided_backprop needs to be calculated.
        Returns:
        grads_val(numpy array): returns the gradient value.
        """
        return self


    def grad_cam(self, input_model, image, layer_name, cls, H, W):
        """GradCAM method for visualizing input saliency.
        Args:
            input_model: Provides the input_model for calculating grad cam 
            image(string):  Takes input image.
            layer_name: Name of the layer for which grad_cam needs to be calculated.
            H(Height): Height of the image
            W(Width): Width of the image
            cls:class number to localize (-1 for most probable class)
        Returns:
        cam(numpy array): returns the grad_cam value.
        """
        return self


    def grad_cam_batch(self, input_model, images, classes, layer_name, H = 224, W = 224):
        """GradCAM method for visualizing input saliency.
        Same as grad_cam but processes multiple images in one run.
        Args:
            input_model: Provides the input_model for calculating grad cam 
            images(list): list of images.
            layer_name: Name of the layer for which grad_cam needs to be calculated.
            H(Height): Height of the image
            W(Width): Width of the image
            classes: classes for which grad_cam is calculated
        Returns:
        new_cams(numpy array): returns the grad_cam value.
        """
        return self


    def compute_saliency(self, model, guided_model, img_path, result_dir, layer_name, cls=-1, save=False):
        """Compute saliency using all three approaches.
        
        Args:
            model: Provides the input model for calculating grad cam
            img_path(list): list of image paths.
            layer_name: Name of the layer for which grad_cam needs to be calculated.
            cls: class number to localize (-1 for most probable class).
            result_dir:Provides the resulting directory to save the Gradcam image
            save(Boolean): To save the results

        Returns:
            gradcam(numpy array): returns the grad_cam value.
            gb(numpy array): returns the guided_backprop value.
            guided_gradcam(numpy array): returns the guided_gradcam value.
        
        """
        return self
