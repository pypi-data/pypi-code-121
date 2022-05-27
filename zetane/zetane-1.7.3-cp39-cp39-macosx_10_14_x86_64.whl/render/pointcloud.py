

class PointCloud:
    """The pointcloud object holds a reference to a pointcloud in the Zetane universe. Supports file formats las, laz, xml, obj, gltf, glb, and ply.

    Args:
        filepath (str): Set the filepath of the pointcloud object.

    Returns:
        PointCloud: Returns a zetane PointCloud object.
    """
    def __init__(self, nsocket, filepath=None):
        pass


    def obj(self, filepath=""):
        """
            Set the source pointcloud filepath.

        Args:
            filepath (str): Path to an pointcloud file. Relative or absolute. Supports las, laz, xml, obj, gltf, ply.

        Returns:
            PointCloud: Returns this pointcloud object so calls can be chained.
        """
        return self


    def elevation_texture(self, filepath=""):
        """Set the color of each points based on the y-axis of the texture
        and the y position of a point.

        Args:
            filepath (str): Path to a vertical texture file.
       
        Returns:
            PointCloud: Returns this pointcloud object so calls can be chained.

        """
        return self


    def particle_texture(self, filepath=""):
        """Replace each points by an image.

        Args:
            filepath (str): Path to an image file.

        Returns:
            PointCloud: Returns this pointcloud object so calls can be chained.
        """
        return self


    def point_is_circle(self, is_circle=False):
        """
            Set each points to a circle/square.

        Args:
            is_circle (bool): render points as circles.
     
        Returns:
            PointCloud: Returns this pointcloud object so calls can be chained.
        """
        return self


    def point_is_deep(self, is_deep=False):
        """
            Enable/Disable shading of each points.

        Args:
            is_deep: Boolean to enable/disable shading.
        
        Returns:
            PointCloud: Returns this pointcloud object so calls can be chained.
        """
        return self


    def point_size(self, size=0.1):
        """
            Set the size of each points. Must be > 0.

        Args:
            size: Float representing the size of each points.
       
        Returns:
            PointCloud: Returns this pointcloud object so calls can be chained.
        """
        return self


    def clone(self):
        """
            Clones this PointCloud in Zetane; returns the cloned PointCloud object

        Returns:
            PointCloud: cloned from this PointCloud.
        """
        return self
