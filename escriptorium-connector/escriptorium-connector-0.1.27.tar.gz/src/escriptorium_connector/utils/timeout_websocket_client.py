from websocket import WebSocket
from websocket._abnf import ABNF
from websocket._exceptions import WebSocketProtocolException, WebSocketTimeoutException
from websocket._core import trace, isEnabledForTrace
import time


class TimeoutWebsocket(WebSocket):
    def recv(self, timeout=60):
        """
        Receive string data(byte array) from the server.
        Returns
        ----------
        data: string (byte array) value.
        """
        with self.readlock:
            opcode, data = self.recv_data(timeout=timeout)
        if opcode == ABNF.OPCODE_TEXT:
            return data.decode("utf-8")
        elif opcode == ABNF.OPCODE_TEXT or opcode == ABNF.OPCODE_BINARY:
            return data
        else:
            return ""

    def recv_data(self, control_frame=False, timeout=60):
        """
        Receive data with operation code.
        Parameters
        ----------
        control_frame: bool
            a boolean flag indicating whether to return control frame
            data, defaults to False
        Returns
        -------
        opcode, frame.data: tuple
            tuple of operation code and string(byte array) value.
        """
        opcode, frame = self.recv_data_frame(control_frame, timeout=timeout)
        return opcode, frame.data

    def recv_data_frame(self, control_frame=False, timeout=60):
        """
        Receive data with operation code.
        If a valid ping message is received, a pong response is sent.
        Parameters
        ----------
        control_frame: bool
            a boolean flag indicating whether to return control frame
            data, defaults to False
        Returns
        -------
        frame.opcode, frame: tuple
            tuple of operation code and string(byte array) value.
        """
        start_time = int(time.time())
        while True and (int(time.time()) - start_time) <= timeout:
            frame = self.recv_frame()
            if isEnabledForTrace():
                trace("++Rcv raw: " + repr(frame.format()))
                trace("++Rcv decoded: " + frame.__str__())
            if not frame:
                # handle error:
                # 'NoneType' object has no attribute 'opcode'
                raise WebSocketProtocolException("Not a valid frame %s" % frame)
            elif frame.opcode in (
                ABNF.OPCODE_TEXT,
                ABNF.OPCODE_BINARY,
                ABNF.OPCODE_CONT,
            ):
                self.cont_frame.validate(frame)
                self.cont_frame.add(frame)

                if self.cont_frame.is_fire(frame):
                    return self.cont_frame.extract(frame)

            elif frame.opcode == ABNF.OPCODE_CLOSE:
                self.send_close()
                return frame.opcode, frame
            elif frame.opcode == ABNF.OPCODE_PING:
                if len(frame.data) < 126:
                    self.pong(frame.data)
                else:
                    raise WebSocketProtocolException("Ping message is too long")
                if control_frame:
                    return frame.opcode, frame
            elif frame.opcode == ABNF.OPCODE_PONG:
                if control_frame:
                    return frame.opcode, frame
        raise WebSocketTimeoutException(
            f"Request exceeded {timeout} seconds and timed out."
        )
