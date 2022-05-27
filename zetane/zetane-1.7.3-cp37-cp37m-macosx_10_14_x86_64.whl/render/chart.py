

class Chart:
    """
        Chart is a container to hold Metric objects. This object is meant to be sent to zetane
        to be rendered in a particular manner.

    Args:
        title (str): the title for the Chart.
        metrics (list of Metrics): metrics contained by the Chart object.
        type (str): The method of representation.
        domain (float list): pair of floats containing domain info.
        range (float list): pair of floats containing range info.

    Returns:
        Chart: a Chart object.
    """
    def __init__(self, nsocket, title='', data_domain=[0.0, 1.0], data_range=[0.0, 1.0], visual_type='Line', metrics = []):
        pass


    def update(self):
        return self


    def include_metrics(self, metrics, append=True):
        """
            Includes the specified list of Metrics in the Chart to be rendered in Zetane.

        Args:
            metrics (list of Metrics): metrics to add to the Chart object.
            append (bool): decides whether these Metrics are appended or replace the current.

        Returns:
            Chart: Returns this object so calls can be chained.
        """
        return self


    def set_title(self, chart_title):
        """
            Sets the title of the Chart, which will denote it in the Zetane universe.

        Args:
            chart_title (str): the title for the Chart.

        Returns:
            Chart: Returns this object so calls can be chained.
        """
        return self


    def set_type(self, type):
        """
            Sets how the chart is going to represent it's data, methods available
            include: 'Line', 'Bar', 'Pie', 'Surface', 'Dial'.

        Args:
            type (str): The method of representation.

        Returns:
            Chart: Returns this object so calls can be chained.
        """
        return self


    def set_domain(self, min, max):
        """
            Sets the minimum and maximum of the domain.

        Args:
            min (float): domain minimum.
            max (float): domain maximum.

        Returns:
            Chart: Returns this object so calls can be chained.
        """
        return self


    def set_range(self, min, max):
        """
        Sets the minimum and maximum of the range.

        Args:
            min (float): range minimum.
            max (float): range maximum.

        Returns:
            Chart: Returns this object so calls can be chained.
        """
        return self


    def set_attribute(self, attributes = [], clear_attributes = False):
        """
            Adds attribute tags to the chart which may trigger certain features
            within the Zetane Universe.

            Attributes for 'Surface' charts:
                wireframe - shows the connections between points

        Args:
            attributes (str list): tags to add to the chart.

        Returns:
            Chart: Returns this object so calls can be chained.

        """
        return self


    def metric(self, x=None, y=None, z=None, label='', attributes=[]):
        """
            Creates a new metric object.

        Args:
            x (float list):  x axis data.
            y (float list):  y axis data.
            z (float list):  z axis data.
            label (str): name of metric.

        Returns:
            new_metric (Metric): a new metric object.
        """
        return self


    def set_window(self, window = 50, sparse=False):
        return self


    def clone(self):
        """Clones this chart in Zetane; returns the cloned Chart object

        Returns:
            Chart: a clone of this Chart.
        """
        return self
