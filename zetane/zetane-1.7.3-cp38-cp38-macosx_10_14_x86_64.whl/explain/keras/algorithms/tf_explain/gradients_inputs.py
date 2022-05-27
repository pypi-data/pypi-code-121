

class GradientsInputs:
    """
    Perform Gradients*Inputs algorithm (gradients ponderated by the input values).
    """


    def compute_gradients(images, model, class_index, use_guided_grads=False, loss=None):
        """
        Compute gradients ponderated by input values for target class.

        Args:
            images (numpy.ndarray): 4D-Tensor of images with shape (batch_size, H, W, 3)
            model (tf.keras.Model): tf.keras model to inspect
            class_index (int): Index of targeted class

        Returns:
            tf.Tensor: 4D-Tensor
        """
        return None
