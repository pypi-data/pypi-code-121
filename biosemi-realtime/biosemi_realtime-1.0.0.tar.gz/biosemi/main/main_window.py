from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from PyQt5.QtCore import QSettings
import sys
import numpy as np
from os.path import expanduser, sep


class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class QNumpyLineEdit(QtWidgets.QLineEdit):
    textModified = QtCore.pyqtSignal(str, str)  # (before, after)

    def __init__(self, contents='', parent=None, n_max=None, n_min=None):
        super(QNumpyLineEdit, self).__init__(contents, parent)
        self.editingFinished.connect(self.__handleEditingFinished)
        self.textChanged.connect(self.__handleTextChanged)
        self._before = contents
        self.n_max = n_max
        self.n_min = n_min

    def __handleTextChanged(self, text):
        if not self.hasFocus():
            self._before = text

    def __handleEditingFinished(self):
        before, after = self._before, self.text()
        if before != after:
            try:
                _vector = np.fromstring(str(after), dtype=np.float, sep=',')
                if not _vector.any():
                    self.setText(self._before)
                    return
                if self.n_max is not None and _vector.size > self.n_max:
                    self.setText(self._before)
                    return
                if self.n_min is not None and _vector.size < self.n_min:
                    self.setText(self._before)
                    return
                after = ",".join(['{:f}'.format(_v) for _v in _vector])
                self.setText(after)
                self._before = after
                self.textModified.emit(before, after)
            except Exception as e:
                print(str(e))

    def get_array(self):
        return np.fromstring(str(self._before), dtype=np.float, sep=',')


class BiosemiRealTimeMainWindow(QtWidgets.QMainWindow):
    def __init__(self, reactor):
        super(BiosemiRealTimeMainWindow, self).__init__()
        self.reactor = reactor
        self.in_data_widget = None
        self.ave_data_widget = None
        self.init_ui()
        self.gui_restore_settings()
        # detect when debugging app
        if sys.gettrace() is None:
            sys.stdout = EmittingStream(textWritten=self.normal_output_written)

    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__

    def closeEvent(self, evnt):
        self.reactor.stop()

    def normal_output_written(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        text_edit = self.findChild(QtWidgets.QTextEdit, 'console')
        cursor = text_edit .textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        text_edit.setTextCursor(cursor)
        text_edit.ensureCursorVisible()

    def init_ui(self):
        exit_action = QtWidgets.QAction(QtGui.QIcon(''), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.closeEvent)
        menu_bar = self.menuBar()
        exit_menu = menu_bar.addMenu('&Exit')
        exit_menu.addAction(exit_action)

        save_settings_action = QtWidgets.QAction(QtGui.QIcon(''), '&Save Settings', self)
        save_settings_action.setShortcut('Ctrl+S')
        save_settings_action.setStatusTip('Save current settings')
        settings_menu = menu_bar.addMenu('&Settings')
        save_settings_action.triggered.connect(lambda: self.gui_save_settings_to_file())
        settings_menu.addAction(save_settings_action)

        load_settings_action = QtWidgets.QAction(QtGui.QIcon(''), '&Read Settings', self)
        load_settings_action.setShortcut('Ctrl+O')
        load_settings_action.setStatusTip('Read settings')
        load_settings_action.triggered.connect(lambda: self.gui_load_settings_from_file())
        settings_menu.addAction(load_settings_action)

        help_action = QtWidgets.QAction(QtGui.QIcon(''), '&Help', self)
        help_action.setShortcut('Ctrl+H')
        help_action.setStatusTip('Help about application')
        help_action.triggered.connect(self.about_dialog)
        help_menu = menu_bar.addMenu('&Help')
        help_menu.addAction(help_action)
        tabs = QtWidgets.QTabWidget()
        self.set_in_data_tab(tabs)
        self.set_average_tab(tabs)
        self.setCentralWidget(tabs)
        tabs.adjustSize()
        tabs.show()
        self.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Biosemi real-time averager')
        # self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, True)

        self.setWindowFlags(QtCore.Qt.Window |
                            QtCore.Qt.WindowMaximizeButtonHint |
                            QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.WindowSystemMenuHint |
                            QtCore.Qt.WindowTitleHint |
                            QtCore.Qt.WindowCloseButtonHint |
                            QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def set_in_data_tab(self, tabs):
        tab_1 = QtWidgets.QWidget()
        main_frame = QtWidgets.QFrame()
        main_lay_out = QtWidgets.QVBoxLayout(main_frame)
        # set left options frame

        frames = list()
        frames.append(self.set_host_frame())
        frames.append(self.set_plot_options_frame())
        frames.append(self.set_time_frequency_options_frame())
        frames.append(self.set_filter_options_frame())
        frames.append(self.set_blanking_options_frame())
        frames.append(self.set_offset_frame())
        frames.append(self.set_start_stop_frame())
        frames.append(self.set_messages_frame())

        # add vertical splitter between frames
        _v_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        [_v_splitter.addWidget(_f) for _f in frames]

        left_frame = QtWidgets.QFrame()
        left_f_layout = QtWidgets.QVBoxLayout(left_frame)
        # for _frame in frames:
        left_f_layout.addWidget(_v_splitter)

        # add splits between frames
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(left_frame)

        self.in_data_widget = pg.GraphicsWindow()
        right_frame = QtWidgets.QFrame()
        right_f_layout = QtWidgets.QVBoxLayout(right_frame)
        right_f_layout.addWidget(self.in_data_widget)
        splitter.addWidget(right_frame)
        main_lay_out.addWidget(splitter)

        tab_1.setLayout(main_lay_out)
        tab_1.setObjectName('tab_in_data')
        tabs.addTab(tab_1, 'Real Time')

    def set_host_frame(self):
        frame = QtWidgets.QFrame()
        options_box = QtWidgets.QGridLayout(frame)
        options_box.addWidget(QtWidgets.QLabel('Sampling Rate'), *[0, 0])
        qcb_fs = QtWidgets.QComboBox()
        qcb_fs.setObjectName('qt_cb_sampling_frequency')
        qcb_fs.addItems(['16384', '8192', '4096', '2048'])
        qcb_fs.setToolTip('The sampling frequency MUST match that shown in ActiveView.')
        options_box.addWidget(qcb_fs, *[0, 1])

        options_box.addWidget(QtWidgets.QLabel('Host IP'), *[1, 0])
        qline_edit_host = QtWidgets.QLineEdit('localhost')
        qline_edit_host.setObjectName('q_line_edit_host')
        qline_edit_host.setToolTip('The host IP MUST match that shown in ActiveView.')
        options_box.addWidget(qline_edit_host, *[1, 1])

        options_box.addWidget(QtWidgets.QLabel('Port'), *[2, 0])
        qline_edit_port = QtWidgets.QLineEdit('8888')
        obj_validator = QtGui.QIntValidator()
        qline_edit_port.setValidator(obj_validator)
        qline_edit_port.setObjectName('q_line_edit_port')
        qline_edit_port.setToolTip('The port MUST match that shown in ActiveView.')
        options_box.addWidget(qline_edit_port, *[2, 1])

        options_box.addWidget(QtWidgets.QLabel('TCP Subset'), *[3, 0])
        qcb_n_ch = QtWidgets.QComboBox()
        qcb_n_ch.addItems(['None', 'A1-A8 (8)', 'A1-A16 (16)', 'A1-A32 (32)', 'A1-B32 (64)'])
        qcb_n_ch.setObjectName('cb_channels')
        qcb_n_ch.currentIndexChanged['QString'].connect(self.on_channels_changed)
        qcb_n_ch.setToolTip('Make sure ActiveView is streaming via TCP. Selected channels MUST match those streamed by'
                            ' ActiveView.')
        options_box.addWidget(qcb_n_ch, *[3, 1])

        qtchb_ex_electrodes = QtWidgets.QCheckBox('Add 8 EX Electrodes')
        qtchb_ex_electrodes.setObjectName('qt_checkbox_ex_electrodes')
        qtchb_ex_electrodes.stateChanged.connect(self.on_channels_changed)
        qtchb_ex_electrodes.setToolTip('Selected channels MUST match those streamed by ActiveView.')
        options_box.addWidget(qtchb_ex_electrodes, *[4, 0, 1, 2])

        qtchb_7_sensors = QtWidgets.QCheckBox('Add 7 Sensors')
        qtchb_7_sensors.setObjectName('qt_checkbox_7_sensors')
        qtchb_7_sensors.stateChanged.connect(self.on_channels_changed)
        qtchb_7_sensors.setToolTip('Selected channels MUST match those streamed by ActiveView.')
        options_box.addWidget(qtchb_7_sensors, *[5, 0, 1, 2])

        qtchb_9_jazz = QtWidgets.QCheckBox('Add 9 Jazz')
        qtchb_9_jazz.setObjectName('qt_checkbox_9_jazz')
        qtchb_9_jazz.stateChanged.connect(self.on_channels_changed)
        qtchb_9_jazz.setToolTip('Selected channels MUST match those streamed by ActiveView.')
        options_box.addWidget(qtchb_9_jazz, *[6, 0, 1, 2])

        qtchb_32_aib = QtWidgets.QCheckBox('Add 32 AIB Chan')
        qtchb_32_aib.setObjectName('qt_checkbox_32_aib')
        qtchb_32_aib.stateChanged.connect(self.on_channels_changed)
        qtchb_32_aib.setToolTip('Selected channels MUST match those streamed by ActiveView.')
        options_box.addWidget(qtchb_32_aib, *[7, 0, 1, 2])

        qtchb_trigger = QtWidgets.QCheckBox('Add Trigger/Status Chan')
        qtchb_trigger.setObjectName('qt_checkbox_trigger_channel')
        qtchb_trigger.stateChanged.connect(self.on_channels_changed)
        qtchb_trigger.setToolTip('Make sure trigger/status channels is being streamed by ActiveView if you are going '
                                 'to perform online average.')
        options_box.addWidget(qtchb_trigger, *[8, 0, 1, 2])
        return frame

    @staticmethod
    def set_plot_options_frame():
        frame = QtWidgets.QFrame()
        options_box = QtWidgets.QGridLayout(frame)
        obj_validator = QtGui.QIntValidator()
        options_box.addWidget(QtWidgets.QLabel('Samples/channel'), *[0, 0])
        qle_samples_channel = QtWidgets.QLineEdit('128')
        qle_samples_channel.setValidator(obj_validator)
        qle_samples_channel.setObjectName('line_edit_samples_per_channel')
        qle_samples_channel.setToolTip('This value is automatically set and must be identical to that shown in '
                                       'ActiveView TCP panel.')
        options_box.addWidget(qle_samples_channel, *[0, 1])

        options_box.addWidget(QtWidgets.QLabel('Epoch length [ms]'), *[1, 0])
        qsb_epoch_length = QtWidgets.QDoubleSpinBox()
        qsb_epoch_length.setValue(1.0)
        qsb_epoch_length.setMinimum(1.0)
        qsb_epoch_length.setMaximum(10000000.0)
        qsb_epoch_length.setObjectName('spin_box_epoch_length')
        qsb_epoch_length.setToolTip('This defines the length of the average window used for time and frequency '
                                    'analysis.')
        options_box.addWidget(qsb_epoch_length, *[1, 1])

        options_box.addWidget(QtWidgets.QLabel('Channels to Plot'), *[2, 0])
        qlist_channels = QtWidgets.QListWidget()
        qlist_channels.setObjectName('list_channels')
        qlist_channels.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        qlist_channels.setToolTip('Selected channels will be shown and used for online-average.')
        options_box.addWidget(qlist_channels, *[2, 1])

        options_box.addWidget(QtWidgets.QLabel('Ref Channel'), *[3, 0])
        qlist_ref = QtWidgets.QListWidget()
        qlist_ref.setObjectName('list_ref')
        qlist_ref.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        qlist_ref.setToolTip('Selected channels will be averaged and subtracted from Channel to plot.')
        options_box.addWidget(qlist_ref, *[3, 1])

        options_box.addWidget(QtWidgets.QLabel('Trigger Average code'), *[4, 0])
        qel_trigger_code = QtWidgets.QLineEdit('65')
        qel_trigger_code.setObjectName('average_trigger_code')
        qel_trigger_code.setValidator(obj_validator)
        qel_trigger_code.setToolTip('Trigger code that will be used to extract trials for averaging. Make sure this '
                                    'number correspond the trigger number shown in ActiveView.')
        options_box.addWidget(qel_trigger_code, *[4, 1])

        options_box.addWidget(QtWidgets.QLabel('Trigger Start code'), *[5, 0])
        qel_start_trigger_code = QtWidgets.QLineEdit('-1')
        qel_start_trigger_code.setObjectName('start_trigger_code')
        qel_start_trigger_code.setToolTip('Trigger code that will be used to restart data averaging. '
                                          'Please set it -1 to ignore this option.')
        qel_start_trigger_code.setValidator(obj_validator)
        options_box.addWidget(qel_start_trigger_code, *[5, 1])
        return frame

    def set_start_stop_frame(self):
        frame = QtWidgets.QFrame()
        options_box = QtWidgets.QHBoxLayout(frame)
        pb_start = QtWidgets.QPushButton('Start')
        pb_start.setObjectName('pb_start')
        pb_start.clicked.connect(lambda: self.gui_save_settings())
        pb_start.setToolTip('By pressing this bottom, both data acquisition and averaging will begin.')
        options_box.addWidget(pb_start)
        pb_stop = QtWidgets.QPushButton('Stop')
        pb_stop.setObjectName('pb_stop')
        options_box.addWidget(pb_stop)
        return frame

    @staticmethod
    def set_messages_frame():
        frame = QtWidgets.QFrame()
        options_box_t1_4 = QtWidgets.QVBoxLayout(frame)
        te_output = QtWidgets.QTextEdit()
        te_output.setObjectName('console')
        options_box_t1_4.addWidget(te_output)
        return frame

    @staticmethod
    def set_time_frequency_options_frame():
        frame = QtWidgets.QFrame()
        options_box = QtWidgets.QGridLayout(frame)

        qtchb_fft = QtWidgets.QCheckBox('Perform frequency analisys')
        qtchb_fft.setObjectName('qt_checkbox_frequency_analysis')
        qtchb_fft.setToolTip('Select this box if you want to perform frequency analysis.')
        options_box.addWidget(qtchb_fft, *[0, 0])

        options_box.addWidget(QtWidgets.QLabel('Frequencies of interests [Hz]'), *[1, 0])
        qsb_freqs_of_interest = QNumpyLineEdit('8.0, 16.0, 32.0')
        qsb_freqs_of_interest.setObjectName('line_edit_frequencies_of_interest')
        qsb_freqs_of_interest.setToolTip('Comma separated frequencies (e.g. 8.0, 16.0, 32.0) which will be '
                                         'statistically analyzed using the Hotelling t-squred test. '
                                         'The signal-to-noise ratio (SNR) is shown for each frequency peak (F - 1) in '
                                         'linear scale.')
        options_box.addWidget(qsb_freqs_of_interest, *[1, 1])

        obj_validator = QtGui.QIntValidator()
        options_box.addWidget(QtWidgets.QLabel('N residual noise points'), *[2, 0])
        qle_number_points = QtWidgets.QLineEdit('32')
        qle_number_points.setToolTip('This determine the number of evenly separated time points that will be used to '
                                     'obtain time-based estimations of signal-to-noise ratio (SNR) and residual noise'
                                     ' (RN). Both SNR [dB] and RN (uV) are shown for each trace in the time-domain'
                                     ' average panel for weighted (w) and standard (s) average.')
        qle_number_points.setValidator(obj_validator)
        qle_number_points.setObjectName('line_edit_number_tracked_points')
        options_box.addWidget(qle_number_points, *[2, 1])

        options_box.addWidget(QtWidgets.QLabel('SNR time window [ms]'), *[3, 0])
        qle_time_window = QNumpyLineEdit('0.0, 100.0', n_min=2, n_max=2)
        qle_time_window.setObjectName('line_edit_snr_time_window')
        qle_time_window.setToolTip('Comma separated time interval (e.g. 0.0, 100.0) indicating the beginning and '
                                   'end of the time interval where the signal of interest is to be expected. '
                                   'This time window will be used to estimate the signal-to-noise ratio (SNR) in '
                                   'time-based averages. Make sure that your high pass-filter is higher than '
                                   '1 / length of this window to produce accurate estimations of both residual noise '
                                   '(RN) and SNR. For example, if your SNR time windows is between 2 and 12 ms (10 ms '
                                   'length), set the High pass filter to 100 Hz (1 / 10 ms). Not doing this will '
                                   'result in inaccurate estimations of the RN and SNR. The selected window is shown by'
                                   ' vertical lines in the time-domain average plot.')
        options_box.addWidget(qle_time_window, *[3, 1])

        return frame

    @staticmethod
    def set_filter_options_frame():
        frame = QtWidgets.QFrame()
        options_box = QtWidgets.QGridLayout(frame)

        qtchb_filter = QtWidgets.QCheckBox('Perform filtering')
        qtchb_filter.setObjectName('qt_checkbox_perform_filtering')
        qtchb_filter.setToolTip('Select this box if you want to perform filtering of the signal (only applied to '
                                'averaged signal)')
        options_box.addWidget(qtchb_filter, *[0, 0])

        options_box.addWidget(QtWidgets.QLabel('High-pass [Hz]'), *[1, 0])
        qle_high_pass = QtWidgets.QLineEdit()
        qle_high_pass.setObjectName('qt_spin_box_high_pass')
        qle_high_pass.setValidator(QtGui.QDoubleValidator(0.0, 16384.0/2.0, 2))
        qle_high_pass.setText('0.0')
        qle_high_pass.setToolTip('High-pass cutoff  frequency (only applied to averaged signal). Set to 0 to ignore.')
        options_box.addWidget(qle_high_pass, *[1, 1])

        options_box.addWidget(QtWidgets.QLabel('Low-pass [Hz]'), *[2, 0])
        qle_low_pass = QtWidgets.QLineEdit()
        qle_low_pass.setObjectName('qt_spin_box_low_pass')
        qle_low_pass.setValidator(QtGui.QDoubleValidator(0.0, 16384.0/2.0, 2))
        qle_low_pass.setText('0.0')
        qle_low_pass.setToolTip('Low-pass cutoff  frequency (only applied to averaged signal). Set to 0 to ignore.')
        options_box.addWidget(qle_low_pass, *[2, 1])
        return frame

    @staticmethod
    def set_blanking_options_frame():
        frame = QtWidgets.QFrame()
        options_box = QtWidgets.QGridLayout(frame)

        qtchb_blanking = QtWidgets.QCheckBox('Perform blanking')
        qtchb_blanking.setObjectName('qt_checkbox_perform_blanking')
        qtchb_blanking.setToolTip('Select this to perform blanking of the signal')
        options_box.addWidget(qtchb_blanking, *[0, 0])

        options_box.addWidget(QtWidgets.QLabel('Duration [ms]'), *[1, 0])
        qle_blanking_duration = QtWidgets.QLineEdit()
        qle_blanking_duration.setObjectName('qt_spin_box_blanking_duration')
        qle_blanking_duration.setValidator(QtGui.QDoubleValidator(0.0, 10000000, 0))
        qle_blanking_duration.setText('0.0')
        qle_blanking_duration.setToolTip('This determines the duration of the blanking (starting from zero). '
                                         'Blanking will replace all the samples between zero and the selected amount of'
                                         ' blanking time by a constant value corresponding to that of the first sample '
                                         'beyond the blanking time. This is useful to cancel the effects of earphones '
                                         'or other onset artifacts as filtering is performed after blanking.')
        options_box.addWidget(qle_blanking_duration, *[1, 1])
        return frame

    @staticmethod
    def set_offset_frame():
        frame = QtWidgets.QFrame()
        options_box = QtWidgets.QGridLayout(frame)
        options_box.addWidget(QtWidgets.QLabel('Input Offset [uV]'), *[0, 0])
        qle_offset = QtWidgets.QLineEdit()
        qle_offset.setObjectName('qt_spin_box_channel_offset')
        qle_offset.setValidator(QtGui.QDoubleValidator(0.0, 1000., 2))
        qle_offset.setText('100.0')
        qle_offset.setToolTip('Offset (in uV) to visually separate incoming data.')
        options_box.addWidget(qle_offset, *[0, 1])

        options_box.addWidget(QtWidgets.QLabel('Average Offset [uV]'), *[1, 0])
        qle_ave_offset = QtWidgets.QLineEdit()
        qle_ave_offset.setObjectName('qt_spin_box_channel_average_offset')
        qle_ave_offset.setValidator(QtGui.QDoubleValidator(0.0, 1000., 2))
        qle_ave_offset.setText('10.0')
        qle_ave_offset.setToolTip('Offset (in uV) to visually separate average traces. The same value is used for both '
                                  'time- and frequency-based plots')
        options_box.addWidget(qle_ave_offset, *[1, 1])
        return frame

    def set_average_tab(self, tabs):
        tab_2 = QtWidgets.QWidget()
        layout_tab_2 = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
        options_box_t2 = QtWidgets.QHBoxLayout()
        layout_tab_2.addLayout(options_box_t2, stretch=0)
        self.ave_data_widget = pg.GraphicsWindow()
        layout_tab_2.addWidget(self.ave_data_widget)
        tab_2.setLayout(layout_tab_2)
        tab_2.setObjectName('tab_average')
        tabs.addTab(tab_2, 'Average')

    def on_channels_changed(self, _):
        self.update_qt_lists()

    def update_qt_lists(self):
        cb_channels = self.findChild(QtWidgets.QComboBox, 'cb_channels')
        selection = cb_channels.currentText()
        lists = list()
        lists.append(self.findChild(QtWidgets.QListWidget, 'list_channels'))
        lists.append(self.findChild(QtWidgets.QListWidget, 'list_ref'))
        chb_ex_electrode = self.findChild(QtWidgets.QCheckBox, 'qt_checkbox_ex_electrodes')
        chb_7_sensors = self.findChild(QtWidgets.QCheckBox, 'qt_checkbox_7_sensors')
        chb_9_jazz = self.findChild(QtWidgets.QCheckBox, 'qt_checkbox_9_jazz')
        chb_32_aib = self.findChild(QtWidgets.QCheckBox, 'qt_checkbox_32_aib')
        trigger = self.findChild(QtWidgets.QCheckBox, 'qt_checkbox_trigger_channel')

        for ch_list in lists:
            _selected_items = ch_list.selectedItems()
            current_selection = [(_c_i.text(), _c_i.isSelected()) for _c_i in _selected_items]
            ch_list.clear()
            if selection == 'A1-A8 (8)':
                [ch_list.addItem('A{:d}'.format(_i + 1)) for _i in range(8)]
            if selection == 'A1-A16 (16)':
                [ch_list.addItem('A{:d}'.format(_i + 1)) for _i in range(16)]
            if selection == 'A1-A32 (32)':
                [ch_list.addItem('A{:d}'.format(_i + 1)) for _i in range(32)]
            if selection == 'A1-B32 (64)':
                [ch_list.addItem('A{:d}'.format(_i + 1)) for _i in range(32)]
                [ch_list.addItem('B{:d}'.format(_i + 1)) for _i in range(32)]
            if chb_ex_electrode.isChecked():
                [ch_list.addItem('EXG{:d}'.format(_i + 1)) for _i in range(8)]
            if chb_7_sensors.isChecked():
                [ch_list.addItem('Sensor{:d}'.format(_i + 1)) for _i in range(7)]
            if chb_9_jazz.isChecked():
                [ch_list.addItem('Jazz{:d}'.format(_i + 1)) for _i in range(9)]
            if chb_32_aib.isChecked():
                [ch_list.addItem('AIB{:d}'.format(_i + 1)) for _i in range(32)]
            if ch_list.objectName() == 'list_channels' and trigger.isChecked():
                ch_list.addItem('Triggers')
            if current_selection:
                for idx_n in range(ch_list.count()):
                    for _item, _selected in current_selection:
                        if ch_list.item(idx_n).text() == _item:
                            ch_list.item(idx_n).setSelected(_selected)
                            break

    def get_current_settings(self):
        # read host configuration
        host = self.findChild(QtWidgets.QLineEdit, 'q_line_edit_host')
        port = self.findChild(QtWidgets.QLineEdit, 'q_line_edit_port')
        samples_per_channel = self.findChild(QtWidgets.QLineEdit, 'line_edit_samples_per_channel')
        epoch_length = self.findChild(QtWidgets.QDoubleSpinBox, 'spin_box_epoch_length')
        sampling_rate = self.findChild(QtWidgets.QComboBox, 'qt_cb_sampling_frequency')
        channels = self.findChild(QtWidgets.QListWidget, 'list_channels')
        ref_channels = self.findChild(QtWidgets.QListWidget, 'list_ref')
        trigger = self.findChild(QtWidgets.QCheckBox, 'qt_checkbox_trigger_channel')
        trigger_ave_code = self.findChild(QtWidgets.QLineEdit, 'average_trigger_code')
        trigger_start_code = self.findChild(QtWidgets.QLineEdit, 'start_trigger_code')

        # filtering parameters
        filtering = self.findChild(QtWidgets.QCheckBox, 'qt_checkbox_perform_filtering')
        high_pass = self.findChild(QtWidgets.QLineEdit, 'qt_spin_box_high_pass')
        low_pass = self.findChild(QtWidgets.QLineEdit, 'qt_spin_box_low_pass')

        # blanking parameters
        blanking = self.findChild(QtWidgets.QCheckBox, 'qt_checkbox_perform_blanking')
        blanking_duration = self.findChild(QtWidgets.QLineEdit, 'qt_spin_box_blanking_duration')

        # average offset
        average_offset = self.findChild(QtWidgets.QLineEdit, 'qt_spin_box_channel_average_offset')

        channels_to_plot_idx = []
        channel_labels = []
        for _idx in range(channels.count()):
            channel_labels.append(channels.item(_idx).text())
            if channels.item(_idx).isSelected():
                channels_to_plot_idx.append(_idx)

        ref_channel_idx = []
        for _idx in range(ref_channels.count()):
            if ref_channels.item(_idx).isSelected():
                ref_channel_idx.append(_idx)

        trigger_channel = channels.count() - 1 if trigger.isChecked() else []
        n_channels = channels.count()
        print(('number of channels {:d}'.format(n_channels)))
        # get time-frequency analysis options
        frequency_analysis = self.findChild(QtWidgets.QCheckBox, 'qt_checkbox_frequency_analysis')
        number_tracked_points = self.findChild(QtWidgets.QLineEdit, 'line_edit_number_tracked_points')
        snr_time_window = self.findChild(QtWidgets.QLineEdit, 'line_edit_snr_time_window')
        frequencies_of_interest = self.findChild(QNumpyLineEdit, 'line_edit_frequencies_of_interest')
        current_settings = {'host': host.text(),
                            'port': int(port.text()),
                            'samples_per_channel': int(samples_per_channel.text()),
                            'samples_per_epoch': int(epoch_length.value() / 1000.0 *
                                                     float(sampling_rate.currentText())),
                            'sampling_rate': float(sampling_rate.currentText()),
                            'trigger_channel': trigger_channel,
                            'trigger_average_code': int(trigger_ave_code.text()),
                            'trigger_start_code': int(trigger_start_code.text()),
                            'number_channels': n_channels,
                            'channel_labels': channel_labels,
                            'channels_to_plot_idx': channels_to_plot_idx,
                            'ref_channel': ref_channel_idx,
                            'graphic_window_data_in': self.in_data_widget,
                            'graphic_window_average': self.ave_data_widget,
                            'frequency_analysis': frequency_analysis.isChecked(),
                            'number_tracked_points': int(number_tracked_points.text()),
                            'frequencies_of_interest': frequencies_of_interest.get_array(),
                            'snr_time_window': snr_time_window.get_array(),
                            'filtering': filtering.isChecked(),
                            'high_pass': float(high_pass.text()),
                            'low_pass': float(low_pass.text()),
                            'blanking': blanking.isChecked(),
                            'blanking_duration': float(blanking_duration.text()),
                            'average_offset': float(average_offset.text())
                            }
        return current_settings

    def gui_save_settings(self, _settings=None):
        if _settings is None:
            _settings = QSettings(expanduser('~') + sep + '.biosemi_averager' + sep + 'settings.ini', QSettings.IniFormat)
        _settings.setFallbacksEnabled(False)
        _settings.setValue('size', self.size())
        _settings.setValue('pos', self.pos())

        for obj in self.findChildren(QtWidgets.QWidget):
            name = obj.objectName()
            if not name:
                continue
            if isinstance(obj, QtWidgets.QComboBox):
                index = obj.currentIndex()
                text = obj.itemText(index)
                _settings.setValue(name, text)

            if isinstance(obj, QtWidgets.QLineEdit):
                value = obj.text()
                _settings.setValue(name, value)

            if isinstance(obj, QtWidgets.QSpinBox):
                value = obj.value()
                _settings.setValue(name, value)

            if isinstance(obj, QtWidgets.QDoubleSpinBox):
                value = obj.value()
                _settings.setValue(name, value)

            if isinstance(obj, QtWidgets.QCheckBox):
                state = obj.isChecked()
                _settings.setValue(name, state)

            if isinstance(obj, QtWidgets.QRadioButton):
                value = obj.isChecked()
                _settings.setValue(name, value)
            if isinstance(obj, QtWidgets.QListWidget):
                _settings.beginGroup(name)
                for idx_n in range(obj.count()):
                    _settings.setValue(obj.item(idx_n).text(), obj.item(idx_n).isSelected())
                _settings.endGroup()

    def gui_save_settings_to_file(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setNameFilter('*.ini')
        dialog.setDefaultSuffix('ini')
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        if dialog.exec_():
            _file = str(dialog.selectedFiles()[0])
            _settings = QSettings(_file, QSettings.IniFormat)
            self.gui_save_settings(_settings)

    def gui_load_settings_from_file(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setNameFilter('*.ini')
        dialog.setDefaultSuffix('ini')
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        if dialog.exec_():
            _file = str(dialog.selectedFiles()[0])
            _settings = QSettings(_file, QSettings.IniFormat)
            self.gui_restore_settings(_settings)

    def gui_restore_settings(self, _settings=None):
        if _settings is None:
            _settings = QSettings(expanduser('~') + sep + '.biosemi_averager' + sep + 'settings.ini', QSettings.IniFormat)
        _settings.setFallbacksEnabled(False)
        try:
            # Restore geometry
            self.resize(_settings.value('size', QtCore.QSize(500, 500)))
            self.move(_settings.value('pos', QtCore.QPoint(60, 60)))

            for obj in self.findChildren(QtWidgets.QWidget):
                name = obj.objectName()
                # we look for named objects only
                # skip selected channels to read them at the end
                if not name or name in ['list_channels', 'list_ref']:
                    continue
                value = _settings.value(name)
                self.set_object_state(obj, value, _settings)

            # read selected channels after populating all available channels
            obj = self.findChild(QtWidgets.QListWidget, 'list_channels')
            if isinstance(obj, QtWidgets.QListWidget):
                value = _settings.value('list_channels')
                self.set_object_state(obj, value, _settings)

            obj = self.findChild(QtWidgets.QListWidget, 'list_ref')
            if isinstance(obj, QtWidgets.QListWidget):
                value = _settings.value('list_ref')
                self.set_object_state(obj, value, _settings)

        except Exception as e:
            print(str(e))

    @staticmethod
    def set_object_state(obj, new_value, settings):
        if isinstance(obj, QtWidgets.QComboBox):
            value = (new_value)
            if not value:
                return
            index = obj.findText(value)
            if index != -1:
                obj.setCurrentIndex(index)

        if isinstance(obj, QtWidgets.QLineEdit):
            if new_value:
                obj.setText(new_value)

        if isinstance(obj, QtWidgets.QSpinBox):
            value = int(new_value)
            if value:
                obj.setValue(value)

        if isinstance(obj, QtWidgets.QDoubleSpinBox):
            if new_value is not None:
                obj.setValue(float(new_value))

        if isinstance(obj, QtWidgets.QCheckBox):
            if new_value is not None:
                obj.setChecked(new_value == 'true')

        if isinstance(obj, QtWidgets.QRadioButton):
            if new_value is not None:
                obj.setChecked(new_value == 'true')
        if isinstance(obj, QtWidgets.QListWidget):
            name = obj.objectName()
            settings.beginGroup(name)
            saved_keys = settings.childKeys()
            for _i in range(obj.count()):
                for _saved in saved_keys:
                    _item_val = settings.value(_saved)
                    if obj.item(_i).text() == _saved:
                        obj.item(_i).setSelected(_item_val == 'true')
                        break
            settings.endGroup()

    @staticmethod
    def about_dialog():
        d = QtWidgets.QDialog()
        d.setWindowTitle("About")
        text = QtWidgets.QTextEdit()
        text.setText('Copyright (C) 2020  Jaime Undurraga \n '
                     'This program is free software; you can redistribute it and/or '
                     'modify it under the terms of the GNU General Public License '
                     'as published by the Free Software Foundation; either version 2 '
                     'of the License, or (at your option) any later version. \n '
                     'This program is distributed in the hope that it will be useful, '
                     'but WITHOUT ANY WARRANTY; without even the implied warranty of '
                     'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the '
                     'GNU General Public License for more details. \n '
                     'You should have received a copy of the GNU General Public License '
                     'along with this program; if not, write to the Free Software '
                     'Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.')
        text.setReadOnly(True)
        d.layout = QtWidgets.QGridLayout(d)
        d.layout.addWidget(text, 0, 0, 1, 1)
        d.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        d.exec_()





