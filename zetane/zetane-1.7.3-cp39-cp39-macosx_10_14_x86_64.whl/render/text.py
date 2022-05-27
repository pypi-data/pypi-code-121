

class Text:
    """The text object holds a reference to renderable text in the Zetane universe. Text has a number of methods that adjust how the text is rendered.

    Args:
        text (str): the text to be displayed in the engine

    Returns:
        Text: A zetane text object
    """
    def __init__(self, nsocket, text=None):
        pass


    def color(self, color_l=(0,0,0)):
        """
            Set the base color of the text.

        Args:
            r (float): Red channel value [0,1].
            g (float): Green channel value [0,1].
            b (float): Blue channel value [0,1].

        Returns:
            self: .
        """
        return self


    def highlight(self, highlight_l=(0,0,0,0)):
        """
            Set the highlight color of the text overlayed over the base color

        Args:
            r (float): Red channel value [0,1].
            g (float): Green channel value [0,1].
            b (float): Blue channel value [0,1].
            a (float): Alpha channel value [0,1], higher values implies more opaque overlay.

        Returns:
            self: .
        """
        return self


    def gradient(self, color_list=((0, 0, 0), (1, 1, 1))):
        """
            Define a gradient of colors to be applied over the text.

        Args:
            color_list (tuple list): list of colors to interpolate the gradient from, from left to right.
            Should be 3-tuples of color values in [0,1] range.

        Returns:
            self: .
        """
        return self


    def font(self, font):
        """
            Set the text font.

        Args:
            font (str): name of the selected font.
            .. note::
                Some supported fonts include::
                - slab, slab-bold
                - roboto-mono, roboto-mono-bold
                - fira-mono, fira-mono-bold
                - office-code-pro, office-code-pro-bold

        Returns:
            self:  .
        """
        return self


    def font_size(self, font_size):
        """
            Set the font Size.

        Args:
            font_size (float): Size of the font.
        """
        return self


    def scale(self):
        return self


    def prefix(self, prefix):
        """
            Set a prefix string to be prepended to the text.

        Args:
            prefix (str): prefix to append to text.
        """
        return self


    def postfix(self, postfix):
        """
            Set a postfix string to be appended to the text.

        Args:
            prefix (str): prefix to append to text.
        """
        return self


    def precision(self, precision):
        """
            Set the precision of numerical values. """
        return self


    def chars_per_line(self, num=20):
        """
            Set the max number of characters per line.

        Args:
            num (int): Limit of characters per line.
        """
        return self


    def fixed(self, fixed=True):
        """
            Set if a fixed precision is to be used.

        Args:
            fixed (bool): setting of fixed precision.
        """
        return self


    def billboard(self, billboard=True):
        """
            Set if the characters of the text should always face the camera.

        Args:
            billboard (bool): setting of billboard.
        """
        return self


    def align(self, alignment: str = ''):
        """Set the text alignment, with respect to the Text's position.

        An empty string ('') indicates unaligned text which does not guarantee
        precise placement with respect to this Text's position.

        Args:
            alignment (str): one of '', 'left', 'center', or 'right'. Defaults to ''.

        Returns:
            Text: Returns this text object so calls can be chained.

        Raises:
            ValueError: if 'alignment' is not one of '', 'left', 'center', or 'right'
        """
        return self


    def valign(self, alignment: str = ''):
        """Set the vertical text alignment, with respect to the Text's position.

        An empty string ('') indicates unaligned text which does not guarantee
        precise placement with respect to this Text's position.

        Args:
            alignment (str): one of '', 'top', 'middle', or 'bottom'. Defaults to ''.

        Returns:
            Text: Returns this text object so calls can be chained.

        Raises:
            ValueError: if 'alignment' is not one of '', 'top', 'middle', or 'bottom'
        """
        return self


    def text(self, text):
        """
            Set the text to be rendered in Zetane

        Args:
            text (str): The text to be rendered in Zetane. It can be a string or a number.

        Returns:
            Text: Returns this text object so calls can be chained.
        """
        return self


    def clone(self):
        return self
