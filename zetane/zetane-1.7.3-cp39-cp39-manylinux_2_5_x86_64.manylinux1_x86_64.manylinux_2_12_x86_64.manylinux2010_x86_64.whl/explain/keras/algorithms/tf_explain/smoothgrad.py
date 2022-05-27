

class SmoothGrad:
    """
    Perform SmoothGrad algorithm for a given input

    Paper: [SmoothGrad: removing noise by adding noise](https://arxiv.org/abs/1706.03825)
    """


    def explain(self, validation_data, model, class_index, num_samples=5, noise=1.0, loss=None):
        """
        Compute SmoothGrad for a specific class index

        Args:
            validation_data (Tuple[np.ndarray, Optional[np.ndarray]]): Validation data
                to perform the method on. Tuple containing (x, y).
            model (tf.keras.Model): tf.keras model to inspect
            class_index (int): Index of targeted class
            num_samples (int): Number of noisy samples to generate for each input image
            noise (float): Standard deviation for noise normal distribution
            loss (function): Custom loss function for the provided model if needed. If set to None, this defaults to categorical cross-entropy, which is the standard for most multiclass classification tasks (default: None)

        Returns:
            np.ndarray: Grid of all the smoothed gradients
        """
        return self


    def generate_noisy_images(images, num_samples, noise):
        """
        Generate num_samples noisy images with std noise for each image.

        Args:
            images (numpy.ndarray): 4D-Tensor with shape (batch_size, H, W, 3)
            num_samples (int): Number of noisy samples to generate for each input image
            noise (float): Standard deviation for noise normal distribution

        Returns:
            np.ndarray: 4D-Tensor of noisy images with shape (batch_size*num_samples, H, W, 3)
        """
        return None


    def get_averaged_gradients(noisy_images, model, class_index, num_samples, loss_fn):
        """
        Compute average of gradients for target class.

        Args:
            noisy_images (tf.Tensor): 4D-Tensor of noisy images with shape
                (batch_size*num_samples, H, W, 3)
            model (tf.keras.Model): tf.keras model to inspect
            class_index (int): Index of targeted class
            num_samples (int): Number of noisy samples to generate for each input image

        Returns:
            tf.Tensor: 4D-Tensor with smoothed gradients, with shape (batch_size, H, W, 1)
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
