

class OcclusionSensitivity:
    """
    Perform Occlusion Sensitivity for a given input
    """
    def __init__(self, batch_size=None):
        pass


    def explain(self, validation_data, model, class_index, patch_size, postprocess_fn, colormap=cv2.COLORMAP_VIRIDIS, ):
        """
        Compute Occlusion Sensitivity maps for a specific class index.

        Args:
            validation_data (Tuple[np.ndarray, Optional[np.ndarray]]): Validation data
                to perform the method on. Tuple containing (x, y).
            model (tf.keras.Model): tf.keras model to inspect
            class_index (int): Index of targeted class
            patch_size (int): Size of patch to apply on the image
            postprocess_fn (function): Custom postprocessing function to extract class probabilities from model outputs if needed. If set to None, this defaluts to indexing into the 1D outputs array, assuming softmaxed outputs (default: None)
            colormap (int): OpenCV Colormap to use for heatmap visualization

        Returns:
            np.ndarray: Grid of all the sensitivity maps with shape (batch_size, H, W, 3)
        """
        return self


    def get_sensitivity_map(self, model, image, class_index, patch_size):
        """
        Compute sensitivity map on a given image for a specific class index.

        Args:
            model (tf.keras.Model): tf.keras model to inspect
            image:
            class_index (int): Index of targeted class
            patch_size (int): Size of patch to apply on the image

        Returns:
            np.ndarray: Sensitivity map with shape (H, W, 3)
        """
        return self


    def save(self, grid, output_dir, output_name):
        """
        Save the output to a specific dir.

        Args:
            grid (numpy.ndarray): Grid of all heatmaps
            output_dir (str): Output directory path
            output_name (str): Output name
        """
        return self
