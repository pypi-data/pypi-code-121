

class InvertedRepresentation:
    """
        Converts matrix to vector then calculates the alpha norm
    """
    def __init__(self, model, out_dir):
        pass


    def alpha_norm(self, input_matrix, alpha):
        """
            Converts matrix to vector then calculates the alpha norm
        """
        return self


    def total_variation_norm(self, input_matrix, beta):
        """
            Total variation norm is the second norm in the paper
            represented as R_V(x)
        """
        return self


    def euclidian_loss(self, org_matrix, target_matrix):
        """
            Euclidian loss is the main loss function in the paper
            ||fi(x) - fi(x_0)||_2^2& / ||fi(x_0)||_2^2
        """
        return self


    def get_output_from_specific_layer(self, x, layer_id):
        """
            Saves the output after a forward pass until nth layer
            This operation could be done with a forward hook too
            but this one is simpler (I think)
        """
        return self


    def generate_inverted_image_specific_layer(self, input_image, inv_mean, inv_std, img_size, target_layer=3):
        return self
