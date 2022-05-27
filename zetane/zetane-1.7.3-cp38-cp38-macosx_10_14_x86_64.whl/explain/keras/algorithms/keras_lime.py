

class Lime:
    def __init__(self):
        pass


    def transform_img_fn(self, path_list):
        """
        transform function to transform the image into numpy array so that it can be taken as input to model.
        Args:
            path_list (list): Provides the paths of the images
        Returns:
        np.vstack(out): numpy stack of the image
        """
        return self


    def lime_image(self, img_path, model, result_dir, visualize = False):
        """
        Calculate the lime for the particular image for a model.
        Args:
            img_path (String): Provides the path of the image 
            model:Provides the input model for calculating lime
            result_dir: Provides the resulting directory to save the lime image
        Returns:
        temp(numpy array): numpy array of the image
        mask(numpy array): numpy array of the mask of the image to determine Lime area
        """
        return self
