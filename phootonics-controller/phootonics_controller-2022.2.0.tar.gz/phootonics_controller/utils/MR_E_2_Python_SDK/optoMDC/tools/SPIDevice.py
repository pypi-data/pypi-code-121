import struct
import spidev
import time


class SPI:
    def __init__(self, bus: int = 0, device: int = 0):
        self._bus = bus
        self._device = device
        self._spi_comm = spidev.SpiDev()
        self.connect()
        self._spi_comm.max_speed_hz = 125000000//16
        self._spi_comm.mode = 0b01
        self._spi_comm.lsbfirst = False
        self.x_readback = 0
        self.y_readback = 0
        self.reg_value = 0
        self.status = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def set_values(self, system1, register1, system2, register2, data1, data2, data_type='>f'):
        ans = self.send(system1, register1, system2, register2, data1, data2, data_type)
        return [hex(i) for i in ans]

    def get_values(self, system, register, unit_type='>f'):
        resp = self._spi_comm.xfer([0, 0, system, register, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        return self.receive_r(resp, unit_type)

    def send(self,  system1, register1, system2, register2, data1, data2, data_type='>f'):
        byte_string = struct.pack('>B', 0) + \
                      struct.pack('>B', 1) + \
                      struct.pack('>B', system1) + \
                      struct.pack('>B', register1) + \
                      struct.pack('>B', system2) + \
                      struct.pack('>B', register2) + \
                      struct.pack(data_type, data1) + \
                      struct.pack(data_type, data2)
        print(byte_string.hex())
        return self._spi_comm.xfer(byte_string)

    def receive_r(self, response, unit_type):
        self.reg_value = struct.unpack(unit_type, bytes(response[2:6]))[0]
        self.x_readback = struct.unpack('>f', bytes(response[6:10]))[0]
        self.y_readback = struct.unpack('>f', bytes(response[10:14]))[0]

        return self.reg_value, self.x_readback, self.y_readback

    def connect(self):
        self._spi_comm.open(self._bus, self._device)

    def disconnect(self):
        self._spi_comm.close()
