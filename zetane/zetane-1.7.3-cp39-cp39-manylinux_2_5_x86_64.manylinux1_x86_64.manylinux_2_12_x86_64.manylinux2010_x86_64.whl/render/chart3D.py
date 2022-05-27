

class Chart3D:
    """The Chart3D object holds a reference to a 3D chart for displaying or animating 3D points. The object takes values either in a more traditional graphics style (a list of points (x,y,z)) or in the matplotlib style where x, y, and z vectors are all sent separately and their consistency is enforced by the developer.

      Args:
          points (list, optional): A list of (x,y,z) points by point : ((x,y,z),(x,y,z))
          x (list, optional): A list of x float values.
          y (list, optional): A list of y float values.
          z (list, optional): A list of z float values.

      Returns:
          Chart3D: Returns a Chart3D object.
      """
    def __init__(self, nsocket, points=[], x=[], y=[], z=[]):
        pass


    def set_3Dpoints(self, points=None, append=False):
        """Chart 3D coordinates on a surface. Sends a 3D numpy array of coordinates to the Zetane engine to be plotted as a mesh surface.

        Args:
          points (3D numpy array): a 3 dimensional vector of x,y,z coordinates.
          ex: [ [ [x0, y0, z0], [x1, y1, z1] ], [ [x2, y2, z2], [x3, y3, z3] ] ].

          append (bool): Whether to append points to th existing chart in Zetane or clear the data and start over again.

         Returns:
             Chart3D: Returns this object so that methods can be chained.
         """
        return self


    def set_points(self, x, y, z, append=False):
        """Add points to the x, y, and z vectors of the chart

           Args:
            x (float list): x coordinates to append
            y (float list): y coordinates to append
            z (float list): z coordinates to append
            append (bool): Whether to append points to th existing chart in Zetane or clear the data and start over again.

           Returns:
               Chart3D: Returns this object so that methods can be chained.
           """
        return self


    def as_surface(self, surface=False):
        """Set to change whether to render individual points or to render a surface between points.

        Args:
            surface (bool): toggles rendering a surface connecting the 3d points.
        """
        return self


    def wireframe(self, enable_wireframe=True):
        """Render the surface as a wireframe

          Args:
            enable_wireframe (bool): render as wireframe

         Returns:
             Chart3D: Returns this object so that methods can be chained.
          """
        return self


    def clone(self):
        """
            Clones this 3D chart in Zetane; returns the cloned Chart3D object

        Returns:
          Chart3D: a clone of this Chart3D.
        """
        return self
