

class ExtractActivations:
    """ Draw activations of a specific layer for a given input """
    def __init__(self, batch_size=None):
        pass


    def explain(self, validation_data, model, layers_name):
        """
        Compute activations at targeted layers.

        Args:
            validation_data (Tuple[np.ndarray, Optional[np.ndarray]]): Validation data
                to perform the method on. Tuple containing (x, y).
            model (tf.keras.Model): tf.keras model to inspect
            layers_name (List[str]): List of layer names to inspect

        Returns:
            np.ndarray: Grid of all the activations
        """
        return self


    def generate_activations_graph(model, layers_name):
        """
        Generate a graph between inputs and targeted layers.

        Args:
            model (tf.keras.Model): tf.keras model to inspect
            layers_name (List[str]): List of layer names to inspect

        Returns:
            tf.keras.Model: Subgraph to the targeted layers
        """
        return None


    def save(self, grid, output_dir, output_name):
        """
        Save the output to a specific dir.

        Args:
            grid (numpy.ndarray): Grid of all the activations
            output_dir (str): Output directory path
            output_name (str): Output name
        """
        return self
