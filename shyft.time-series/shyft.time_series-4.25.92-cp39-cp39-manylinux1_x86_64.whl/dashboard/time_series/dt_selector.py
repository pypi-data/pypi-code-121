from typing import List, Tuple
from enum import Enum

from shyft.time_series import Calendar, time

from shyft.dashboard.base.ports import Receiver, Sender, States
from shyft.dashboard.base.selector_model import SelectorModelBase
from shyft.dashboard.base.selector_presenter import SelectorPresenter


class CalendarDtStr(Enum):
    Year = int(Calendar.YEAR)
    Quarter = int(Calendar.QUARTER)
    Month = int(Calendar.MONTH)
    Week = int(Calendar.WEEK)
    Day = int(Calendar.DAY)
    Hour = int(Calendar.HOUR)
    Minute = int(Calendar.MINUTE)
    Second = int(Calendar.SECOND)


def calendar_unit_to_str(dt: Tuple[int, time]) -> str:
    if isinstance(dt, int):
        enum = CalendarDtStr(dt)
    elif isinstance(dt, time):
        enum = CalendarDtStr(int(dt))
    else:
        raise TypeError()
    return str(enum.name)


def dt_to_str(dt: Tuple[int, time]) -> str:
    """ Convert fix dt to human-readable string (w/o calendar semantics)"""
    counts = []
    dts_options = [e.value for e in CalendarDtStr]
    tres = int(dt)

    for option in dts_options:
        n = tres // option
        tres -= option * n
        counts.append(n)

    ses = ['s' if n > 1 else '' for n in counts]
    return ' '.join([f'{n} {calendar_unit_to_str(t)}{s}' for n, t, s in zip(counts, dts_options, ses) if n != 0])


def tdiff_to_str(cal: Calendar, t1: int, t2: int, simple: bool = True) -> str:
    """ Convert time difference as human-readable string using calendar semantics, like '1 Year 3 Months'"""
    if t2 < t1:
        t1, t2 = t2, t1

    counts = []
    dts = [e.value for e in CalendarDtStr]
    if simple:
        dts.remove(int(cal.QUARTER))

    tres = t1
    for dt in dts:
        if tres < t2:
            n = cal.diff_units(tres, t2, dt)
            tres = cal.add(tres, dt, n)
        else:
            n = 0
        counts.append(n)

    ses = ['s' if n > 1 else '' for n in counts]
    return ' '.join([f'{n} {calendar_unit_to_str(t)}{s}' for n, t, s in zip(counts, dts, ses) if n != 0])


class DeltaTSelector(SelectorModelBase):
    def __init__(self, presenter: SelectorPresenter, logger=None) -> None:
        """
        dt selctor model used with TsViewer

        Parameters
        ----------
        presenter: SelectorPresenter instance to use
        logger: optional logger instance
        """
        super(DeltaTSelector, self).__init__(presenter=presenter, logger=logger)
        self.presenter.default = 'Auto'
        self.receive_selection_options = Receiver(parent=self, name='receive dt options',
                                                  func=self._receive_selection_options, signal_type=List[int])
        self.send_dt = Sender(parent=self, name='send dt', signal_type=int)
        self.state = States.DEACTIVE

    def on_change_selected(self, selection_list: List[str]) -> None:
        if self.state == States.DEACTIVE or not selection_list or not selection_list[0]:
            return
        dt = self._convert_selected_dt(selection_list[0])
        self.send_dt(dt)

    @staticmethod
    def _convert_selected_dt(selected_dt: str) -> int:
        if 'Auto' in selected_dt:
            selected_dt = selected_dt.split('Auto: ')[-1]
        return int(selected_dt)

    def _receive_selection_options(self, dt_list: List[int]):
        if not isinstance(dt_list, List):
            self.presenter.set_selector_options(callback=False)
            return
        # generate options
        dt_list = sorted(dt_list)
        options = [(str(int(dt)), dt_to_str(dt)) for dt in dt_list]
        if options:
            self.presenter.default = ('Auto: {}'.format(options[0][0]), 'Auto: {}'.format(options[0][1]))
        else:
            self.presenter.default = 'Auto'

        # selection
        curr_select = None
        if len(dt_list) != 0:
            if not self.presenter.selected_values or not self.presenter.selected_values[0]:
                curr_select = dt_list[0]
            else:
                selected_value = self.presenter.selected_values[0]
                # if Auto
                if 'Auto' in selected_value:
                    if options:
                        curr_select = 'Auto: {}'.format(options[0][0])
                    else:
                        curr_select = None
                # if not Auto
                else:
                    selected_value = int(selected_value)
                    if selected_value in dt_list:
                        curr_select = str(selected_value)
                    else:
                        if dt_list[0] > selected_value:
                            curr_select = str(int(dt_list[0]))
                        elif dt_list[-1] < selected_value:
                            curr_select = str(int(dt_list[-1]))

            self.presenter.set_selector_options(options, sort=False, selected_value=curr_select, callback=False)
        if curr_select:
            self.send_dt(self._convert_selected_dt(curr_select))

    def _receive_state(self, state: States) -> None:
        if state == self.state:
            return
        self.state = state
        if state == States.ACTIVE:
            self.presenter.state_ports.receive_state(state)
            # Not sending active state since this only done if we can send data to the next widget
        elif state == States.DEACTIVE:
            self.presenter.default = ('', 'Auto')
            self.presenter.state_ports.receive_state(state)
            self.state_port.send_state(state)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)
