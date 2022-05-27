

class Dial:
    """ A dial has a pointer and scale on a face and is used for showing measurements on that scale.

    Returns:
        Dial: Returns a Dial object.
    """
    def __init__(self, nsocket):
        pass


    def set_max(self, max_value=None):
        """Sets the maximum value on the right extremity of the dials arc

        Args:
          max_value (float): Maximum value on the dial's arc

        Returns:
            Dial: Returns this object so that methods can be chained.
        """
        return self


    def set_indicator_value(self, current_value=None):
        """Sets the current value which the indicator needle will point to on the dial arc.

        Args:
          current_value (float): current value to be indicated on the dial

        Returns:
            Dial: Returns this object so that methods can be chained.
        """
        return self


    def clone(self):
        """Clones this dial in Zetane; returns the cloned dial object

        Returns:
          Dial: a clone of this Dial.
        """
        return self
