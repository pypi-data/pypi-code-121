

class ChartDEPRECATED:
    def __init__(self, nsocket, points=None, data_domain=1.0, data_range=1.0):
        pass


    def points(self, points=None, append=False):
        """
        Sets a 1D numpy array of coords to be sent to the Zetane engine
        to be plotted as a graph at the next .update() call.

        :param points: a vector of points
        :type points: 1-dimensional list
        """
        return self


    def color(self, r=0.0, g=0.0, b=0.0):
        """
        sets the color of the visual data on the graph

        :params r: value (between 0 and 1) of the red color component
        :type r: Float
        :params g: value (between 0 and 1) of the green color component
        :type g: Float
        :params b: value (between 0 and 1) of the blue color component
        :type b: Float
        """
        return self


    def compress(self, compress=True):
        """
        Setting this causes the rendered points in zetane to remain within a
        predetermined space along the X-axis

        :param compress_points: compress the rendered point spacing
        :type compress_points: Boolean
        """
        return self


    def set_labels_with_indices(self, labels_with_indices_dict=None):
        """
          Intakes a dictionary where the keys are assigned to labels which will appear
          next to the data in the bar graph, and the values will decide which locations
          these labels appear at

          :params labels_with_indices: Labels as keys and index locations as values
          :type labels_with_indices:
        """
        return self


    def dimensions(self, data_domain, data_range):
        return self


    def smooth(self, smooth=True):
        """
        Sets the the graph to have it's points interpolated with a curved spline

        :param enable_smooth: Boolean to activate spline interpolation
        :type smooth: Bool
        """
        return self


    def as_bar_graph(self, enable_as_bar_graph=True):
        """
        Renders the points in the graph as bars

        :param enable_as_bar_graph: set rendering of bar graph
        :type enable_as_bar_graph: Bool
        """
        return self


    def color_floor(self, enable_color_floor=True):
        """Colors the entire bar according to the points value"""
        return self


    def add_border(self, enable_border=True):
        return self


    def filled(self, enable_filled=True):
        """Fills the space underneath the plotted line with a color gradient"""
        return self


    def heightmap(self, width, length, heightmap=True):
        """
        Sets the plotted vector to be rendered as a heightmap.
        shape of the plane can be set through the 'width' & 'depth'.
        If left empty, the square root of the vector point quantity
        is used for the both dimensions of the rendered plane.

        :param width: width of the plane
        :type width: Int
        :param length: depth of the plane
        :type length: Int
        """
        return self


    def wireframe(self, wireframe=True):
        """
        Sets the Chart object to be plotted as a wireframe

        Only has an effect if .heightmap() is called on the object
        """
        return self


    def clone(self):
        """
        Clones this chart in Zetane; returns the cloned Chart object

        .. todo:: move to zobj when other subclasses are also cloneable
        .. todo:: custom zobj.deep_copy function to fine-tune deepcopy() behaviour
        :return: a new Chart, cloned from this Chart.
        """
        return self
