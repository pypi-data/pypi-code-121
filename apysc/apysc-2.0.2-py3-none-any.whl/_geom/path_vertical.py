"""This module is for implementing the SVG `vertical line` (V)
path data class.
"""

from typing import Any
from typing import Union

from apysc._geom.path_data_base import PathDataBase
from apysc._geom.path_y_interface import PathYInterface
from apysc._html.debug_mode import add_debug_info_setting
from apysc._type.boolean import Boolean
from apysc._type.int import Int
from apysc._type.string import String


class PathVertical(PathDataBase, PathYInterface):
    """
    Path data class for the SVG `vertical line` (V).

    Examples
    --------
    >>> import apysc as ap
    >>> stage: ap.Stage = ap.Stage()
    >>> sprite: ap.Sprite = ap.Sprite()
    >>> sprite.graphics.line_style(color='#fff', thickness=3)
    >>> path: ap.Path = sprite.graphics.draw_path(
    ...     path_data_list=[
    ...         ap.PathMoveTo(x=0, y=50),
    ...         ap.PathVertical(y=100),
    ...     ])
    """

    @add_debug_info_setting(
        module_name=__name__, class_name='PathVertical')
    def __init__(
            self, y: Union[int, Int], *,
            relative: Union[bool, Boolean] = False) -> None:
        """
        Path data class for the SVG `vertical line' (V).

        Parameters
        ----------
        y : Int or int
            Y-coordinate of the destination point.
        relative : bool or Boolean, default False
            The boolean value indicating whether the path
            coordinates are relative or not (absolute).

        Examples
        --------
        >>> import apysc as ap
        >>> stage: ap.Stage = ap.Stage()
        >>> sprite: ap.Sprite = ap.Sprite()
        >>> sprite.graphics.line_style(color='#fff', thickness=3)
        >>> path: ap.Path = sprite.graphics.draw_path(
        ...     path_data_list=[
        ...         ap.PathMoveTo(x=0, y=50),
        ...         ap.PathVertical(y=100),
        ...     ])
        """
        from apysc._converter.to_apysc_val_from_builtin import \
            get_copied_int_from_builtin_val
        from apysc._geom.path_label import PathLabel
        super(PathVertical, self).__init__(
            path_label=PathLabel.VERTICAL,
            relative=relative)
        self.y = get_copied_int_from_builtin_val(integer=y)

    @add_debug_info_setting(
        module_name=__name__, class_name='PathVertical')
    def _get_svg_str(self) -> str:
        """
        Get a path's SVG string created with the current setting.

        Returns
        -------
        svg_str : str
            An SVG path string was created with the current setting.
        """
        from apysc._type import value_util
        svg_char: String = self._get_svg_char()
        svg_char_str: str = value_util.get_value_str_for_expression(
            value=svg_char)
        y_str: str = value_util.get_value_str_for_expression(
            value=self._y)
        svg_str: str = f'{svg_char_str} + String({y_str})'
        return svg_str

    @add_debug_info_setting(
        module_name=__name__, class_name='PathVertical')
    def update_path_data(
            self, y: Union[int, Int],
            *,
            relative: Union[bool, Boolean] = False) -> None:
        """
        Update the path's data settings.

        Parameters
        ----------
        y : Int or int
            Y-coordinate of the destination point.
        relative : bool or Boolean
            A boolean value indicates whether the path
            coordinates are relative or not (absolute)..

        Examples
        --------
        >>> import apysc as ap
        >>> path_vertical: ap.PathVertical = ap.PathVertical(y=50)
        >>> path_vertical.update_path_data(y=100)
        >>> path_vertical.y
        Int(100)
        """
        from apysc._converter.to_apysc_val_from_builtin import \
            get_copied_boolean_from_builtin_val
        from apysc._converter.to_apysc_val_from_builtin import \
            get_copied_int_from_builtin_val
        self.y = get_copied_int_from_builtin_val(integer=y)
        self.relative = get_copied_boolean_from_builtin_val(
            bool_val=relative)

    @add_debug_info_setting(
        module_name=__name__, class_name='PathVertical')
    def __eq__(self, other: Any) -> Any:
        """
        Equal comparison method.

        Parameters
        ----------
        other : Any
            The other value to compare.

        Returns
        -------
        result : Boolean
            Comparison result.
        """
        import apysc as ap
        if not isinstance(other, PathVertical):
            result: ap.Boolean = ap.Boolean(False)
            return result
        return self.y == other.y and self.relative == other.relative

    @add_debug_info_setting(
        module_name=__name__, class_name='PathVertical')
    def __ne__(self, other: Any) -> Any:
        """
        The other value to compare.

        Parameters
        ----------
        other : Any
            Other value to compare.

        Returns
        -------
        result : Boolean
            Comparison result.
        """
        import apysc as ap
        result: ap.Boolean = self == other
        result = result.not_
        return result
