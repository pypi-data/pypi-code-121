

class VanillaGradients:
    """
    Perform gradients backpropagation for a given input

    Paper: [Deep Inside Convolutional Networks: Visualising Image Classification
        Models and Saliency Maps](https://arxiv.org/abs/1312.6034)
    """


    def explain(self, validation_data, model, class_index, use_guided_grads=False, loss=None):
        """
        Perform gradients backpropagation for a given input

        Args:
            validation_data (Tuple[np.ndarray, Optional[np.ndarray]]): Validation data
                to perform the method on. Tuple containing (x, y).
            model (tf.keras.Model): tf.keras model to inspect
            class_index (int): Index of targeted class
            use_guided_grads (boolean): Whether to use guided grads or raw gradients
            loss (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)

        Returns:
            numpy.ndarray: Grid of all the gradients
        """
        return self


    def compute_gradients(images, model, class_index, use_guided_grads=False, loss_fn=None):
        """
        Compute gradients for target class.

        Args:
            images (numpy.ndarray): 4D-Tensor of images with shape (batch_size, H, W, 3)
            model (tf.keras.Model): tf.keras model to inspect
            class_index (int): Index of targeted class
            use_guided_grads (boolean): Whether to use guided grads or raw gradients

        Returns:
            tf.Tensor: 4D-Tensor
        """
        return None


    def save(self, grid, output_dir, output_name):
        """
        Save the output to a specific dir.

        Args:
            grid (numpy.ndarray): Gtid of all the smoothed gradients
            output_dir (str): Output directory path
            output_name (str): Output name
        """
        return self
