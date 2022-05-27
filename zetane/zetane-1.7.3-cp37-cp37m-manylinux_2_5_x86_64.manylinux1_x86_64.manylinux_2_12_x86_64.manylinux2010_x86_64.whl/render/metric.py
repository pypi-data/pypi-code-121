

class Metric:
    """
        Metric is an object which contains 3 vectors of data to be represented in a visual way by adding them to Chart objects.

        Args:
            x (float list): A vector of X coordinate values.
            y (float list): A vector of Y coordinate values.
            z (float list): A vector of Z coordinate values.
            label (str): a word to describe the metric.

        Returns:
            Metric: a Metric object.
    """
    def __init__(self, x=None, y=None, z=None, label='', attributes=[]):
        pass


    def init_values(self):
        """
        initializes the x, y, z vectors to an empty state.

        Args:
            (none)

        Returns:
            Metric: Returns this object so calls can be chained.
        """
        return self


    def set_values(self, x=None, y=None, z=None):
        """
        Sets the vectors in the metric of specified parameters.

        Args:
            x (float list): A vector of X coordinate values.
            y (float list): A vector of Y coordinate values.
            z (float list): A vector of Z coordinate values.

        Returns:
            Metric: Returns this object so calls can be chained.
        """
        return self


    def set_3Dpoints(self, points):
        """
         takes a list of xyz coordinates to populate a metric's x, y and z vectors.

         Args:
            points (numpy): a 3D numpy array containing x,y,z point coordinates.
            ex: [ [ [x0, y0, z0], [x1, y1, z1] ], [ [x2, y2, z2], [x3, y3, z3] ] ].

        Returns:
            Metric: Returns this object so calls can be chained.
         """
        return self


    def append_values(self, x=None, y=None, z=None):
        """
        Appends values to the specified vector(s) in the parameter list.

        Args:
            x (float list): A vector of X coordinate values to append.
            y (float list): A vector of Y coordinate values to append.
            z (float list): A vector of Z coordinate values to append.

        Returns:
            Metric: Returns this object so calls can be chained.
        """
        return self


    def set_label(self, label):
        """
         Sets the label which will denote the metric in zetane.

        Args:
            label (str): a word to describe the metric.

        Returns:
            Metric: Returns this object so calls can be chained.
        """
        return self


    def set_attribute(self, attributes=[], clear_attributes=False):
        """
        Adds attribute tags to the metric which may trigger certain features
        within the Zetane Universe.
        Args:
            attributes (str list): tags to add to the metric.

        Returns:
          Metric: Returns this object so calls can be chained.

        Current possible attributes:
          line charts:
              points - render as points
              linked - connects coordinates when the 'points' attribute is in use
              smooth - Renders edges in the chart as splines.
              filled - fills the space underneath a chart with color.
        """
        return self


    def set_color(self, r=None, g=None, b=None):
        """
        Set a custom color to be used for the metric displayed in Zetane.
        (default color will be random if none is chosen)
        Args:
            r (float): intensity of red in the color.
            g (float): intensity of green in the color.
            b (float): intensity of blue in the color.

        Returns:
            Metric: Returns this object so calls can be chained.
        """
        return self
