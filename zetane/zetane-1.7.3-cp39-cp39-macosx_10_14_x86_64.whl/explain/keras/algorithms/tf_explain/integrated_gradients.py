

class IntegratedGradients:
    """
    Perform Integrated Gradients algorithm for a given input

    Paper: [Axiomatic Attribution for Deep Networks](https://arxiv.org/pdf/1703.01365.pdf)
    """


    def explain(self, validation_data, model, class_index, n_steps=10, loss=None):
        """
        Compute Integrated Gradients for a specific class index

        Args:
            validation_data (Tuple[np.ndarray, Optional[np.ndarray]]): Validation data
                to perform the method on. Tuple containing (x, y).
            model (tf.keras.Model): tf.keras model to inspect
            class_index (int): Index of targeted class
            n_steps (int): Number of steps in the path
            loss (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)

        Returns:
            np.ndarray: Grid of all the integrated gradients
        """
        return self


    def get_integrated_gradients(interpolated_images, model, class_index, n_steps, loss_fn):
        """
        Perform backpropagation to compute integrated gradients.

        Args:
            interpolated_images (numpy.ndarray): 4D-Tensor of shape (N * n_steps, H, W, 3)
            model (tf.keras.Model): tf.keras model to inspect
            class_index (int): Index of targeted class
            n_steps (int): Number of steps in the path

        Returns:
            tf.Tensor: 4D-Tensor of shape (N, H, W, 3) with integrated gradients
        """
        return None


    def generate_interpolations(images, n_steps):
        """
        Generate interpolation paths for batch of images.

        Args:
            images (numpy.ndarray): 4D-Tensor of images with shape (N, H, W, 3)
            n_steps (int): Number of steps in the path

        Returns:
            numpy.ndarray: Interpolation paths for each image with shape (N * n_steps, H, W, 3)
        """
        return None


    def generate_linear_path(baseline, target, n_steps):
        """
        Generate the interpolation path between the baseline image and the target image.

        Args:
            baseline (numpy.ndarray): Reference image
            target (numpy.ndarray): Target image
            n_steps (int): Number of steps in the path

        Returns:
            List(np.ndarray): List of images for each step
        """
        return None


    def save(self, grid, output_dir, output_name):
        """
        Save the output to a specific dir.

        Args:
            grid (numpy.ndarray): Grid of all the heatmaps
            output_dir (str): Output directory path
            output_name (str): Output name
        """
        return self
