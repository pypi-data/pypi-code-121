from serial.tools import list_ports

from .SPIDevice import SPI
import sys, os
import time

class MR1030:
    _valid_hwids = ['0483:A31E']
    _port = ''
    _endian = '>'
    _type_int = 'I'
    _type_flt = 'f'
    
    sysclk = 18000000
    clkdiv = 16
    def __init__(self, bus, device, freq0, amp0, freq1, amp1, iters):
        _int = self._endian + self._type_int
        _flt = self._endian + self._type_flt
        
        self.spi = SPI(bus=bus, device=device)
        self.spi._spi_comm.max_speed_hz = self.sysclk//self.clkdiv
        self.filename = 'point_cloud.txt'

        #### Set current example
        #ans = self.spi.set_values(0x50,0x00, 0x51, 0x00,0.05 , -0.08 , _flt) 
        #print(ans)

        #### Set analog mode example
        #ans = self.spi.set_values(0x40,0x00, 0x40, 0x05, 0x58, 0x59, _int) 
        #print(ans)

        ### Resonant mirror example
        ans = self.spi.set_values(0x40, 0x00, 0x40, 0x05, 0x60, 0x61, _int)   # Signal-Gen set as input
        print(ans)        
        
        ans = self.spi.set_values(0x40,0x02, 0x40, 0x07, 0xC0, 0xC1, _int)   # both axis closed loop
        #ans = self.spi.set_values(0x40,0x02, 0x40, 0x07, 0xC0, 0xB1, _int)   # X axis closed loop, Y axis open loop 
        print(ans)
        
        ans = self.spi.set_values(0x60, 0x00, 0x61, 0x00, 2, 2, _int)         # Signal-Gen Unit
        print(ans)
        
        ans = self.spi.set_values(0x60, 0x02, 0x61, 0x02, 1, 0, _int)         # Signal-Gen Shape
        print(ans)        
        
        ans = self.spi.set_values(0x60, 0x03, 0x61, 0x03, freq0, freq1, _flt) # Signal-Gen Frequency
        print(ans)
        
        ans = self.spi.set_values(0x60, 0x04, 0x61, 0x04, amp0, amp1, _flt)   # Signal-Gen Amplitude
        print(ans)
        
        ans = self.spi.set_values(0x60, 0x01, 0x61, 0x01, 1, 1, _int)         # Signal-Gen Run
        print(ans)
        
        ans = self.spi._spi_comm.xfer([0, 0,  0x30, 0x02, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        print([hex(i) for i in ans])

        time.sleep(2)
        #self.listen_raw(iters)  # only return raw values, not struct.unpacked
        self.listen(iters)  # unpack values
              
        ans = self.spi.set_values(0x60, 0x01, 0x61, 0x01, 0, 0, _int)  # Signal-Gen Stop
        ans = self.spi._spi_comm.xfer([0, 0, 0x22, 0x00, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        print([hex(i) for i in ans])

        ans = self.spi._spi_comm.xfer([0, 0, 0x22, 0x00, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        print([hex(i) for i in ans])
        
    def listen_raw(self, iterations):
        start = time.time()
        with open(self.filename, 'w') as file:
            self.spi._spi_comm.xfer([0, 0, 0x30, 0x02, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            for _ in range (iterations):
                res = self.spi._spi_comm.xfer([0, 0, 0x30, 0x02, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                file.write(str([hex(i) for i in res])+'\n')
            print("Time Taken: {}s".format(time.time()-start))
            file.close()
            
    def listen(self, iterations):
        start = time.time()
        with open(self.filename, 'w') as file:
            self.spi._spi_comm.xfer([0, 0, 0x30, 0x02, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            for _ in range (iterations):
                reg, x, y = self.spi.get_values(0x30, 0x02, '>I')
                file.write(str(reg)+','+str(x)+','+str(y)+'\n')
            print("Time Taken: {}s".format(time.time()-start))
            file.close()
        
if __name__ == '__main__':
    mr1030 = MR1030(bus=0, device=0, freq0=5.0, amp0=0.4, freq1=1.0, amp1=0.05, iters=10000)
