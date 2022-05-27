

class Mesh:
    """The mesh object holds a reference to a mesh in the Zetane universe.

    Args:
        nsocket (Socket): Socket to communicate with the Zetane Engine.
        filepath (str, optional): A string to a mesh filepath.

    Returns:
        Mesh: A zetane object for a mesh.
    """
    def __init__(self, nsocket, filepath=None):
        pass


    def obj(self, filepath=""):
        """
            Set the source mesh OBJ filepath (.obj).

        Args:
            filepath (str): Path to an OBJ mesh file (.obj). Relative or absolute.

        Returns:
            Mesh: self
        """
        return self


    def highlight(self, r=0, g=0, b=0, a=0):
        """
            Set the highlight color of the text overlayed over the base color.

        Args:
            r (float): Red channel value [0,1].
            g (float): Green channel value [0,1].
            b (float): Blue channel value [0,1].
            a (float): Alpha channel value [0,1]; strength of highlight.

        Returns:
            Mesh: self
        """
        return self


    def transparency(self, amount=0.0):
        """
            Set mesh transparency from opaque (0.0) to fully transparent (1.0).

        Args:
            amount (float): transparency [0.0 = opaque, 1.0 = transparent].

        Returns:
            Mesh: self
        """
        return self


    def backface_culling(self, enable=True):
        """
            Enable/disable backface culling.

        Args:
            enable (bool): enable/disable backface culling.

        Returns:
            Mesh: self
        """
        return self


    def wireframe(self, show=True):
        """
            Set wireframe visibility status.

        Args:
            enable (bool): show/hide wireframe.

        Returns:
            Mesh: self
        """
        return self


    def clone(self):
        """
        Clones this mesh in Zetane; returns the cloned Mesh object

        Returns:
            Mesh: A new mesh object, cloned from this mesh.
        """
        return self
