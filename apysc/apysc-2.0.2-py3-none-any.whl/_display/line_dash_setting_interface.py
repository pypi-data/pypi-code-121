"""Class implementation for line dash setting interface.
"""

from typing import Dict
from typing import Optional

from apysc._display.line_dash_setting import LineDashSetting
from apysc._html.debug_mode import add_debug_info_setting
from apysc._type.revert_interface import RevertInterface
from apysc._type.variable_name_interface import VariableNameInterface


class LineDashSettingInterface(VariableNameInterface, RevertInterface):

    _line_dash_setting: Optional[LineDashSetting]

    def _initialize_line_dash_setting_if_not_initialized(self) -> None:
        """
        Initialize the _line_dash_setting attribute if this
        interface does not initialize it yet.
        """
        if hasattr(self, '_line_dash_setting'):
            return
        self._line_dash_setting = None

    @property
    @add_debug_info_setting(
        module_name=__name__, class_name='LineDashSettingInterface')
    def line_dash_setting(self) -> Optional[LineDashSetting]:
        """
        Get current line dash setting.

        Returns
        -------
        line_dash_setting : LineDashSetting or None
            Line dash setting.

        References
        ----------
        - Graphics line_dash_setting interface document
            - https://simon-ritchie.github.io/apysc/graphics_line_dash_setting.html  # noqa

        Examples
        --------
        >>> import apysc as ap
        >>> stage: ap.Stage = ap.Stage()
        >>> sprite: ap.Sprite = ap.Sprite()
        >>> sprite.graphics.line_style(color='#fff', thickness=10)
        >>> line: ap.Line = sprite.graphics.draw_line(
        ...     x_start=50, y_start=50, x_end=150, y_end=50)
        >>> line.line_dash_setting = ap.LineDashSetting(
        ...     dash_size=5, space_size=2)
        >>> line.line_dash_setting.dash_size
        Int(5)

        >>> line.line_dash_setting.space_size
        Int(2)
        """
        self._initialize_line_dash_setting_if_not_initialized()
        return self._line_dash_setting

    @line_dash_setting.setter
    def line_dash_setting(self, value: Optional[LineDashSetting]) -> None:
        """
        Set line dash setting.

        Parameters
        ----------
        value : LineDashSetting or None
            Line dash setting to set.

        References
        ----------
        - Graphics line_dash_setting interface document
            - https://simon-ritchie.github.io/apysc/graphics_line_dash_setting.html  # noqa
        """
        from apysc._html.debug_mode import DebugInfo
        with DebugInfo(
                callable_='line_dash_setting', args=[value], kwargs={},
                module_name=__name__,
                class_name=LineDashSettingInterface.__name__):
            from apysc._validation import display_validation
            self._update_line_dash_setting_and_skip_appending_exp(value=value)
            self._append_line_dash_setting_update_expression()
            display_validation.validate_multiple_line_settings_isnt_set(
                any_instance=self)

    def _update_line_dash_setting_and_skip_appending_exp(
            self, *, value: Optional[LineDashSetting]) -> None:
        """
        Update line dash setting and skip appending expression.

        Parameters
        ----------
        value : LineDashSetting or None
            Line dash setting to set.
        """
        if value is not None and not isinstance(value, LineDashSetting):
            raise TypeError(
                'Not supported line_dash_setting type specified: '
                f'{type(value)}'
                '\nAcceptable ones are: LineDashSetting or None.')
        self._line_dash_setting = value

    @add_debug_info_setting(
        module_name=__name__, class_name='LineDashSettingInterface')
    def _append_line_dash_setting_update_expression(self) -> None:
        """
        Append line dash setting updating expression.
        """
        import apysc as ap
        if self._line_dash_setting is None:
            setting_str: str = '""'
        else:
            setting_str = (
                'String('
                f'{self._line_dash_setting.dash_size.variable_name})'
                ' + " " + '
                'String('
                f'{self._line_dash_setting.space_size.variable_name})'
            )
        expression: str = (
            f'{self.variable_name}.css("stroke-dasharray", {setting_str});'
        )
        ap.append_js_expression(expression=expression)

    _line_dash_setting_snapshots: Dict[str, Optional[LineDashSetting]]

    def _make_snapshot(self, *, snapshot_name: str) -> None:
        """
        Make value's snapshot.

        Parameters
        ----------
        snapshot_name : str
            Target snapshot name.
        """
        self._initialize_line_dash_setting_if_not_initialized()
        self._set_single_snapshot_val_to_dict(
            dict_name='_line_dash_setting_snapshots',
            value=self._line_dash_setting, snapshot_name=snapshot_name)

    def _revert(self, *, snapshot_name: str) -> None:
        """
        Revert value if snapshot exists.

        Parameters
        ----------
        snapshot_name : str
            Target snapshot name.
        """
        if not self._snapshot_exists(snapshot_name=snapshot_name):
            return
        self._line_dash_setting = self._line_dash_setting_snapshots[
            snapshot_name]
