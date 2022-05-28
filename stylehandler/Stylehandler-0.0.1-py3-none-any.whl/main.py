from typing import Dict


# TODO: Add enable debug function
# TODO: Add debug to output config args in terminal (failed and non-failed)
# TODO: Add try except for invalid config calls -> iterate through each config arg if they fail
# TODO: Add in set_styles which sets the style and runs pre-calculations for any style extends
# TODO: Add in "cache" for pre-calculations, checks for if a style has been calculated already and pulls the
#  pre-calculation if it has

class Stylehandler:
    """
    A custom, Tkinter Style Handler for widgets. Allows the use of a minimalistic, CSS-like structure that can be easily
    applied to any TK widgets (does not work for TTK widgets).

    This also supports inheritance between styles and applying multiple styles to a single widget.

    TTKs style handling exists but has flaws. A major one being that it doesn't function as expected:
    https://stackoverflow.com/questions/17635905/ttk-entry-background-colour
    """

    styles = {}

    @staticmethod
    def apply(widget, *styles: str):
        """
        Static method for applying styles to a given Widget

        :param widget: The widget you want stylised
        :param styles: The names of the styles you want to use
        :return: the stylised Widget
        """

        final_attributes = {}

        # Iterate through provided styles and generate a final dict using a recursive helper function
        for style in styles:
            final_attributes.update(Stylehandler.__apply_helper(style, {}))

        # Remove extend styles if present
        if "extends" in final_attributes:
            del final_attributes["extends"]

        widget.configure(**final_attributes)
        return widget

    @staticmethod
    def __apply_helper(style: str, attributes_aggregate: Dict[str, str]) -> Dict[str, str]:
        """
        Helper for the apply method to enable recursive searching through extended styles

        :param style: the style to search the extended styles of
        :param attributes_aggregate: an updating dict of the current style attributes to apply to the widget
        :return: an updated attributes_aggregate
        """

        # Recursive calls through inherited styles to get style attributes back to front
        for child_style in Stylehandler.styles[style].get("extends", ()):
            attributes_aggregate = Stylehandler.__apply_helper(child_style, attributes_aggregate)

        attributes_aggregate.update(Stylehandler.styles[style])
        return attributes_aggregate
