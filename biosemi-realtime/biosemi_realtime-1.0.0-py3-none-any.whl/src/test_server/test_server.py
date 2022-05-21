import sys
from twisted.python import log
from twisted.internet import reactor
import twisted.internet.protocol as protocol
from twisted.protocols import basic
import numpy as np
from twisted.internet import task


class DataServerProtocol(basic.LineReceiver):
    def __init__(self):
        # define streaming parameters
        self.fs = 16384.
        self.n_channels = 8
        self.n_samples_per_ch = 128
        self.epoch_length = 1/21  # seconds
        # define trigger parameters
        self.trigger_width = 0.0005  # seconds
        self.trigger_code = 15   # integer between 0 and 255
        self.include_trigger = True
        # define test stimuli
        self.stimulus_duration = 0.012  # seconds
        self.freq = np.round(self.stimulus_duration * 1000.) / self.stimulus_duration

        # we generate time vector and stimuli
        self.time = np.arange(0, self.fs * self.epoch_length) / self.fs
        self.c_pos = 0
        amp = 128. / 2 ** 23
        self.test_signal = np.zeros(self.time.shape)
        _signal_vector = np.arange(0, int(self.fs * self.stimulus_duration))
        t_signal = _signal_vector / self.fs
        self.test_signal[_signal_vector] = (amp * np.sin(2. * np.pi * self.freq * t_signal)) * 2 ** 23
        self.test_signal = self.test_signal - np.mean(self.test_signal)
        self.test_signal = self.test_signal.astype(np.int32)
        self.trigger = np.zeros(self.test_signal.shape, dtype=np.int32)
        # define a positive trigger
        self._v_t = np.arange(0, int(self.fs * self.trigger_width))
        self.trigger[self._v_t] = self.trigger_code = 15
        self.lp = None
        self.blocks_sent = 0
        self.loops_sent = 0

        self.std_signal = np.std(self.test_signal[_signal_vector])
        n = 5000
        desired_snr = 10.0
        self.ini_std = 10.0 ** (-desired_snr / 20.0) * self.std_signal * n ** 0.5
        self.noise = (self.ini_std * 1. * np.random.randn(self.test_signal.size)).astype(np.int32)
        print('Theoretical_rn: {:.1f} for {:d} averages'.format(self.std_signal / (n ** 0.5), n))

    def dataReceived(self, data):
        log.msg('Data received {}'.format(data))

    def connectionMade(self):
        log.msg('Client connection from {}'.format(self.transport.getPeer()))
        self.start_data_loop()

    def start_data_loop(self):
        self.lp = task.LoopingCall(self.send_data)
        self.lp.start(128./self.fs)

    def send_data(self):
        if not self.connected:
            print('no data')
            return

        self.setRawMode()
        _trigger = self.trigger
        if self.c_pos >= self.epoch_length * self.fs:
            self.c_pos = 0
            self.noise = (self.ini_std * np.random.randn(self.test_signal.size)).astype(np.int32)
            self.loops_sent += 1

        # if 150 > self.loops_sent + 1 > 100:
        #     self.trigger[self._v_t] = 0
        #     _f = 0
        # elif np.mod(self.loops_sent + 1, 150) == 0:
        #     self.trigger[self._v_t] = 20
        #     _f = 0
        # else:
        self.trigger[self._v_t] = 15
        _f = 1

        # if self.loops_sent > 199:
        #     _f = 0

        if self.n_channels > 0:
            _current_signal = self.test_signal[self.c_pos:self.c_pos + self.n_samples_per_ch] + \
                              self.noise[self.c_pos:self.c_pos + self.n_samples_per_ch]
            aux = np.tile(_current_signal * _f, [self.n_channels, 1])
            if self.include_trigger:
                aux = np.vstack((aux, _trigger[self.c_pos:self.c_pos + self.n_samples_per_ch]))
        else:
            aux = _trigger[self.c_pos:self.c_pos + self.n_samples_per_ch]
        data = np.squeeze(np.reshape(aux, (1, -1), order='F'))
        data_bytes = data.tobytes()
        _buffer = [data_bytes[i: i + 3] for i in range(0, len(data) * data.dtype.itemsize, data.dtype.itemsize)]

        self.transport.write(b''.join(_buffer))
        self.blocks_sent += 1
        self.c_pos += self.n_samples_per_ch

    def connectionLost(self, reason):
        self.lp.stop()
        log.msg('Lost connection because {}'.format(reason))


class DataServerFactory(protocol.ServerFactory):
    def buildProtocol(self, addr):
        return DataServerProtocol()


def main():
    log.startLogging(sys.stdout)
    log.msg('Start your engines...')
    server = protocol.ServerFactory()
    server.protocol = DataServerProtocol
    reactor.listenTCP(8888, server)
    reactor.run()


if __name__ == '__main__':
    main()
