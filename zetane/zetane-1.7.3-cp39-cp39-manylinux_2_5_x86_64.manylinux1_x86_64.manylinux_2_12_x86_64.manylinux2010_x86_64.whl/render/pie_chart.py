

class PieChart:
    """ A pie chart object holds a reference to a pie chart in the Zetane universe, which displays data as part of 360 degree arc.

    Args:
        nsocket (Socket): Socket to communicate with the Zetane Engine.

    Returns:
        PieChart: An object wrapping a zetane pie chart.
    """
    def __init__(self, nsocket):
        pass


    def pielabels(self, pielabels=None):
        """ Creates a pie chart from a dictionary. The keys are used as labels, and the values determine the size of the sectors in the pie chart.

        Args:
            pie_labels (dict): Pie sector labels and sector values

        Returns:
            PieChart: Returns the pie chart object so that calls can be chained.
        """
        return self


    def clone(self):
        return self
