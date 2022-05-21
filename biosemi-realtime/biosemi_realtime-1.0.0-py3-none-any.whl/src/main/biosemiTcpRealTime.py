import numpy as np
import pyqtgraph as pg
import io
from src.main.py_averager import weightedAverage as WAverager
import datetime
from twisted.internet import protocol, defer
from twisted.internet.defer import DeferredLock

defer.setDebugging(True)
pg.setConfigOption('leftButtonPan', False)


class BiosemiPlotter(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.connected = True
        self.transport.write(b"Connected to biosemi system")

    def dataReceived(self, data):
        if self.factory.check_package_size:
            self.factory.check_package_size = False
            if np.mod(len(data), self.factory.bytes_in_tcp_array) != 0:
                print('Buffer size does not match the number of ' \
                      'selected channels ({:d}). Check that both biosemi and real-time average ' \
                      'match in configuration'.format(self.factory.number_channels))
                self.factory.stop()
        self.factory.streamer.fill_buffer(data)
        self.factory.ave_streamer.fill_buffer(data)

    def connectionLost(self, reason):
        self.factory.connected = False
        print("connection lost")


class StreamBuffer(object):
    def __init__(self, buffer_size=0, reactor=None, f=None, call_later=None):
        self.buffer_size = buffer_size
        self.buffer = io.BufferedRandom(io.BytesIO())
        self.buffer_idx = 0
        self.buffer_counter = 0
        self.reactor = reactor
        self.target_f = f
        self.call_later = call_later
        self._lock = DeferredLock()

    def fill_buffer(self, data):
        if len(data) > 2 * self.buffer_size:
            print("buffer overrunning, buffer size is {:d}, and current data size is {:d}".format(2 * self.buffer_size,
                                                                                                  len(data)))
            return
        _data = ''
        if self.buffer_idx == 0:
            if 2 * self.buffer_size > self.buffer.tell() + len(data) >= self.buffer_size:
                self.buffer.write(data)
                _c_pos = self.buffer.tell()
                self.buffer_idx = 1
                self.buffer_counter += 1
                # read from the beginning of the buffer
                self.buffer.seek(0, 0)
                _data = self.buffer.read(self.buffer_size)
                # set buffer position to end
                self.buffer.seek(_c_pos, 0)
            elif 2 * self.buffer_size < self.buffer.tell() + len(data):
                print("buffer overrunning, buffer size is {:d}, and current data size is {:d}".format(
                    2 * self.buffer_size, len(data)))
            else:
                self.buffer.write(data)
        elif self.buffer_idx == 1:
            if self.buffer.tell() + len(data) >= 2 * self.buffer_size:
                _end_data_idx = self.buffer_size * 2 - self.buffer.tell()
                self.buffer.write(data[0:_end_data_idx])
                self.buffer_idx = 0
                self.buffer_counter += 1
                self.buffer.seek(self.buffer_size, 0)
                _data = self.buffer.read(self.buffer_size)
                self.buffer.seek(0, 0)
                self.buffer.write(data[_end_data_idx:])
            else:
                self.buffer.write(data)
        if _data:
            _d = self._lock.run(self.target_f, _data)
            if self.call_later is not None:
                _d.addCallback(self.call_later)


class StreamAveraging(object):
    def __init__(self,
                 min_buffer_size=0,
                 number_channels=0,
                 number_samples_per_epoch=0,
                 reactor=None,
                 f=None,
                 call_later=None):
        self.buffer_size = np.maximum(min_buffer_size, number_channels * number_samples_per_epoch * 3 * 2)
        self.buffer = io.BufferedRandom(io.BytesIO())
        self.buffer_idx = 0
        self.buffer_counter = 0
        self.reactor = reactor
        self.target_f = f
        self.call_later = call_later
        self.overlap_samples = 1 * number_channels * 3
        self._lock = DeferredLock()

    def fill_buffer(self, data):
        if len(data) > 2 * self.buffer_size:
            print("buffer overrunning, buffer size is {:d}, and current data size is {:d}".format(2 * self.buffer_size,
                                                                                                  len(data)))
            return
        _data = ''
        if self.buffer_idx == 0:
            if 2 * self.buffer_size > self.buffer.tell() + len(data) >= self.buffer_size:
                self.buffer.write(data)
                _c_pos = self.buffer.tell()
                self.buffer_idx = 1
                self.buffer_counter += 1
                # read from the beginning of the buffer
                if self.buffer_counter > 0 and self.overlap_samples:
                    self.buffer.seek(2 * self.buffer_size - self.overlap_samples, 0)
                    _data = self.buffer.read()
                self.buffer.seek(0, 0)
                _data = _data + self.buffer.read(self.buffer_size)
                # set buffer position to end
                self.buffer.seek(_c_pos, 0)
            elif 2 * self.buffer_size < self.buffer.tell() + len(data):
                print("buffer overrunning, buffer size is {:d}, and current data size is {:d}".format(
                    2 * self.buffer_size, len(data)))
            else:
                self.buffer.write(data)
        elif self.buffer_idx == 1:
            if self.buffer.tell() + len(data) >= 2 * self.buffer_size:
                _end_data_idx = self.buffer_size * 2 - self.buffer.tell()
                self.buffer.write(data[0:_end_data_idx])
                self.buffer_idx = 0
                self.buffer_counter += 1
                self.buffer.seek(self.buffer_size - self.overlap_samples, 0)
                _data = self.buffer.read(self.buffer_size + self.overlap_samples)
                self.buffer.seek(0, 0)
                self.buffer.write(data[_end_data_idx:])
            else:
                self.buffer.write(data)
        if _data:
            # _d = threads.deferToThread(self.target_f, _data)
            _d = self._lock.run(self.target_f, _data)
            if self.call_later is not None:
                _d.addCallback(self.call_later)


class BiosemiFactory(protocol.ClientFactory):
    def __init__(self, reactor):
        self.reactor = reactor
        self.lp_in_data = None
        self.lp_average = None
        self.plotting_in_data = False
        self.plotting_average_data = False
        self.reactor_port = None
        self.ip = None
        self.port = None
        self.protocol = BiosemiPlotter
        self.fs = None
        self.number_channels = None
        self.samples_per_channel = None
        self.bytes_in_tcp_array = None
        self.samples_per_record = None
        self.number_samples_per_epoch = None
        self.channels_to_plot = None
        self.ref_channel = None
        self.trigger_channel = None
        self.channels_to_read = None
        self.channels_to_plot_idx = None
        self.channels_to_ref = None
        self.trigger_code = None
        self.trigger_start_code = None
        self._signal_buffer = np.array([])
        self._signal_plot_buffer = np.array([])
        self._time = np.array([])
        self.buffer_length_in_sec = 0.2
        self.buffer_size = None
        self._ax = None
        self.buffer_writer = None
        self._current_sample_position = 0
        self.records_per_epoch_count = 0
        self.j_ave = None
        self.physical_maximum = 262143.0
        self.physical_minimum = -262144.0
        self.digital_maximum = 8388607.0
        self.digital_minimum = -8388608.0
        self.gain = (self.physical_maximum - self.physical_minimum) / (self.digital_maximum - self.digital_minimum)
        self._incoming_data_curves = []
        self._in_data = np.empty(0)
        self._in_time = np.empty(0)
        self.channels_offset = 100.0
        self._in_records_read = 0
        self.time_window_rt = 10
        self._win_trigger = None
        self._ax_trigger = None
        self._trigger_count = 0
        self.graphic_window_average = None
        self.graphic_window_data_in = None
        self._d_ave = None
        self.settings = None
        self.restart_average = False
        self.connected = False
        self.check_package_size = True
        self.streamer = None
        self.ave_streamer = None
        self.initial_offset = None

    def buildProtocol(self, addr):
        return BiosemiPlotter(self)

    def apply_settings(self, **kwargs):
        ip = kwargs.get('host', "127.0.0.1")
        port = kwargs.get('port', 8888)
        fs = kwargs.get('sampling_rate', 16384)
        number_channels = kwargs.get('number_channels', 65)
        samples_per_channel = kwargs.get('samples_per_channel', 16)
        samples_per_epoch = kwargs.get('samples_per_epoch', 512)
        channels_to_plot_idx = np.atleast_1d(kwargs.get('channels_to_plot_idx', [0]))
        ref_channel = np.atleast_1d(kwargs.get('ref_channel', 0))
        trigger_channel = np.atleast_1d(kwargs.get('trigger_channel', 65))
        trigger_code = kwargs.get('trigger_average_code', 0)
        trigger_start_code = kwargs.get('trigger_start_code', None)
        graphic_window_average = kwargs.get('graphic_window_average', None)
        graphic_window_data_in = kwargs.get('graphic_window_data_in', None)

        self.ip = ip
        self.port = port
        self.protocol = BiosemiPlotter
        self.fs = float(fs)
        self.number_channels = number_channels
        self.samples_per_channel = samples_per_channel
        self.bytes_in_tcp_array = number_channels * samples_per_channel * 3
        self.samples_per_record = number_channels * samples_per_channel
        self.number_samples_per_epoch = samples_per_epoch
        self.channels_to_plot = np.array(channels_to_plot_idx, dtype=np.int)
        self.ref_channel = ref_channel
        ref_channel = ref_channel if ref_channel is not None else np.array([], dtype=np.int)
        self.trigger_channel = trigger_channel
        self.channels_to_read = np.unique(
            np.concatenate((channels_to_plot_idx, ref_channel, trigger_channel))).astype(np.int)
        self.channels_to_plot_idx = np.in1d(self.channels_to_read, self.channels_to_plot)
        self.channels_to_ref = ~np.in1d(self.channels_to_read, [trigger_channel])
        self.trigger_code = trigger_code
        self.trigger_start_code = trigger_start_code
        self.graphic_window_average = graphic_window_average
        self.graphic_window_data_in = graphic_window_data_in
        self.buffer_length_in_sec = 0.2
        self.buffer_size = self.number_channels * self.samples_per_channel * 3 * np.maximum(
            int(self.fs * self.buffer_length_in_sec / self.samples_per_channel), 1)
        self.buffer_writer = io.BytesIO()
        self.settings = kwargs
        self.check_package_size = True
        self.streamer = StreamBuffer(self.buffer_size, self.reactor, self.plot_incoming_data)
        self.ave_streamer = StreamAveraging(self.buffer_size,
                                            self.number_channels,
                                            self.number_samples_per_epoch,
                                            self.reactor,
                                            self.do_average, self.return_average_thread)
        self.restart_average = False
        self.connected = False

    def clientConnectionFailed(self, connector, reason):
        self.connected = False
        print("Connection failed - goodbye!")

    def clientConnectionLost(self, connector, reason):
        self.connected = False
        print("Connection lost - goodbye!")

    def initialize_ave_plot_data(self):
        self.graphic_window_average.clear()
        self.plotting_average_data = False
        self._trigger_count = 0
        self._signal_plot_buffer = np.zeros((self.number_samples_per_epoch, len(self.channels_to_plot)))
        self._signal_buffer = np.zeros((self.number_samples_per_epoch, len(self.channels_to_read)))
        self._time = np.arange(self.number_samples_per_epoch, dtype=np.float) / self.fs
        self._current_sample_position = 0
        self.j_ave = WAverager.JAverager()
        self.j_ave.figure_handle = self.graphic_window_average
        self.j_ave.splits = len(self.channels_to_plot)
        self.j_ave.fs = self.fs
        self.j_ave.demean = False
        noise_samples_step = np.maximum(self.number_samples_per_epoch / self.settings['number_tracked_points'], 1)
        self.j_ave.t_p_snr = np.arange(0, self.number_samples_per_epoch, noise_samples_step) / self.fs
        self.j_ave.analysis_window = self.settings['snr_time_window'] * 1e-3
        self.j_ave.time_offset = 0.0
        self.j_ave.channels_offset = self.settings['average_offset']
        self.j_ave.alpha_level = 0.05
        self.j_ave.min_block_size = 10
        self.j_ave.min_block_samples = 5
        self.j_ave.fft_analysis = self.settings['frequency_analysis']
        self.j_ave.frequencies_to_analyze = self.settings['frequencies_of_interest']
        self.j_ave.blanking = self.settings['blanking']
        self.j_ave.blanking_duration = self.settings['blanking_duration'] * 1e-3
        self.j_ave.plot_sweeps = False
        self.j_ave.rejection_level = np.Inf
        self.j_ave.rejection_window = np.array([0, 2])
        self.j_ave.plot_frequency_range = np.array([0, self.fs / 2.0])
        if self.settings['filtering']:
            self.j_ave.low_pass = self.settings['low_pass']
            self.j_ave.high_pass = self.settings['high_pass']

    def initialize_incoming_plot_data(self):
        self.initial_offset = None
        self.plotting_in_data = False
        self.graphic_window_data_in.clear()
        pg.QtGui.QApplication.processEvents()
        if not isinstance(self.graphic_window_data_in, pg.graphicsWindows.GraphicsWindow):
            self.graphic_window_data_in = pg.GraphicsWindow()
        self._ax = self.graphic_window_data_in.addPlot()
        self._ax.setDownsampling(ds=100, mode='peak')
        self._ax.showGrid(True, True)
        self._in_data = np.zeros((int(self.fs * self.time_window_rt), self.channels_to_read.size))
        self._in_time = np.arange(int(self.fs * self.time_window_rt), dtype=np.float) / self.fs
        self._in_records_read = 0
        self._incoming_data_curves = []
        for _i, _ch in enumerate(self.channels_to_plot):
            self._incoming_data_curves.append(self._ax.plot(self._in_time, self._in_data[:, _i] -
                                                            _i * self.channels_offset,
                                                            pen=pg.intColor(_i, self.channels_to_plot.size))
                                              )
        self._ax.setXRange(self._in_time[0], self._in_time[-1])
        self._ax.setYRange(-self.channels_to_plot.size * (self.channels_offset + 1), self.channels_offset)
        pg.QtGui.QApplication.processEvents()

    def return_average_thread(self, value):
        try:
            self.update_ave_plot()
        except Exception as e:
            print(str(e))
        if self.restart_average:
            self.stop()
            self.restart()
            return

    def do_average(self, data):
        try:
            print('ave' + str(datetime.datetime.now()))
            data = np.frombuffer(data, dtype=np.uint8, count=-1, offset=0)
            data = self.decode_raw_data(data)
            trigger_data = data[:, self.trigger_channel]
            trigger_positions = self.detect_trigger(trigger_data)

            # check if restart code is present and apply it
            _restart, _pos = self.detect_re_start_trigger(trigger_data)
            if _restart:
                trigger_positions = trigger_positions[trigger_positions < _pos]

            # keep filling buffer if started in previous call
            if self._current_sample_position:
                if trigger_positions.size:
                    _t_pos = trigger_positions[0] - 1
                else:
                    _t_pos = data.shape[0]
                c_epoch_size = np.minimum(self.number_samples_per_epoch, self._current_sample_position + _t_pos)
                _end_block = np.minimum(_t_pos, c_epoch_size - self._current_sample_position)
                _pos = self._current_sample_position
                self._signal_buffer[_pos: _pos + _end_block, :] = data[1:_end_block + 1, self.channels_to_read]
                self._current_sample_position += _end_block
                if self._current_sample_position == c_epoch_size:
                    self.add_epochs()
                    self._current_sample_position = 0

            for _i, _t_pos, in enumerate(trigger_positions):
                c_epoch_size = self.number_samples_per_epoch
                if trigger_positions.size > 1 and _i < trigger_positions.size - 1:
                    trigger_distance = np.diff(trigger_positions)
                    c_epoch_size = np.minimum(trigger_distance[_i], c_epoch_size)

                _end_block = np.minimum(data.shape[0] - _t_pos, c_epoch_size - self._current_sample_position)
                _pos = self._current_sample_position
                self._signal_buffer[_pos: _pos + _end_block, :] = data[
                                                                  _t_pos:_t_pos + _end_block, self.channels_to_read]
                self._current_sample_position += _end_block
                if self._current_sample_position == c_epoch_size:
                    self.add_epochs()
                    self._current_sample_position = 0
            return True
        except Exception as e:
            print(str(e))
            return False

    def sample_to_buffer_pos(self, sample_pos):
        return 3 * self.number_channels * sample_pos

    def buffer_size_to_n_samples(self, num_bytes):
        return num_bytes / 3 / self.number_channels

    def detect_trigger(self, trigger_channel=np.empty(0)):
        positive_trigger = np.diff((trigger_channel.astype(np.int) == self.trigger_code).astype(np.int), axis=0) > 0
        positions = np.where(np.append(0, positive_trigger))
        events = [int(_t) for _t in trigger_channel[positions].astype(np.int) if _t > 0]
        u_events = np.unique(events)
        for _u_e in u_events:
            print('Code {:d} found {:d} times'.format(_u_e, len(np.where(np.array(events) == _u_e)[0])))
        self._trigger_count += positions[0].size
        print('Total triggers found: {:.1f}'.format(self._trigger_count))
        return positions[0]

    def detect_re_start_trigger(self, trigger_channel=np.empty(0)):
        matched_triggers = (trigger_channel.astype(np.int) == self.trigger_start_code)
        _pos = None
        if matched_triggers.any():
            self.restart_average = True
            _pos = np.where(matched_triggers)[0]
            _pos = _pos[0]
        return self.restart_average, _pos

    def add_epochs(self):
        data = self._signal_buffer
        # assign last value to rest of buffer if not complete to reduce filtering artifacts
        if self._current_sample_position < self.number_samples_per_epoch:
            data[self._current_sample_position - 1:, :] = data[self._current_sample_position - 2, :]
        data = self.apply_reference(data)
        _data = data[:, self.channels_to_plot_idx]
        for _col in range(_data.shape[1]):
            self.j_ave.add_sweep(_data[:, _col], split_id=_col)
        self._signal_buffer.fill(0.0)

    def plot_incoming_data(self, data):
        try:
            aux = np.frombuffer(data, dtype=np.uint8, count=-1, offset=0)
            data = self.decode_raw_data(aux)
            _data = data[:, self.channels_to_read]
            if self.initial_offset is None:
                self.initial_offset = np.mean(_data, axis=0)
            _data = _data - self.initial_offset
            _data = self.apply_reference(_data)
            self._in_data = np.roll(self._in_data, -_data.shape[0], axis=0)
            self._in_data[-_data.shape[0]:, :] = _data
            data_to_plot = self._in_data[:, self.channels_to_plot_idx]
            for _i, _ax in enumerate(self._incoming_data_curves):
                _ax.setData(self._in_time, data_to_plot[:, _i] - _i * self.channels_offset)
            pg.QtGui.QApplication.processEvents()
        except Exception as e:
            print(str(e))

    def decode_raw_data(self, in_data):
        data = np.reshape(in_data, (-1, 3)).astype(np.int32)
        data = (np.int32((data[:, 0] << 8) | (data[:, 1] << 16) | (data[:, 2] << 24)) >> 8)
        # data = ((data[:, 0]) + (data[:, 1] << 8) + (data[:, 2] << 16))
        # data[data >= (1 << 23)] -= (1 << 24)
        data = data.reshape((-1, self.number_channels))
        data[:, self.trigger_channel] = data[:, self.trigger_channel] & 255
        data = data.astype(np.float)
        if ~np.alltrue(np.array(self.channels_to_read == self.trigger_channel)):
            data[:, np.array(self.channels_to_read[self.channels_to_read != self.trigger_channel])] = data[:, np.array(
                self.channels_to_read[self.channels_to_read != self.trigger_channel])] * self.gain
        return data

    def apply_reference(self, data=np.empty(0)):
        if self.ref_channel is None or self.ref_channel.size == 0:
            return data
        ref_channel_data = data[:, np.in1d(self.channels_to_read, self.ref_channel)]
        if ref_channel_data.shape[1] > 1:
            ref_channel_data = np.atleast_2d(np.mean(ref_channel_data, axis=1)).T

        data[:, self.channels_to_ref] -= ref_channel_data
        return data

    def update_ave_plot(self):
        self.j_ave.plot_current_data()

    def update_input_offset(self, value):
        self.channels_offset = value
        if self._ax is not None:
            self._ax.enableAutoRange(True, True)

    def update_average_offset(self, value):
        # make sure averager is assigned
        if self.j_ave is not None:
            self.j_ave.channels_offset = value

    def start_listening(self):
        self.reactor_port = self.reactor.connectTCP(self.ip, self.port, self, timeout=30)
        print("starting")

    def start(self, settings={}):
        self.stop()
        self.apply_settings(**settings)
        self.initialize_incoming_plot_data()
        self.initialize_ave_plot_data()
        self.start_listening()

    def stop(self):
        if self.reactor_port is not None and self.reactor_port.transport is not None:
            self.reactor_port.transport.loseConnection()

    def restart(self):
        self.restart_average = False
        self.apply_settings(**self.settings)
        self.initialize_incoming_plot_data()
        self.initialize_ave_plot_data()
        self.start_listening()

