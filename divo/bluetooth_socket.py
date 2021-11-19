import socket
from typing import Optional

from bluetooth_base import BluetoothBase
from exceptions import NotConnectedException


class BluetoothSocket(BluetoothBase):
    """
    Bluetooth connection using native Bluetooth socket support.
    """
    def __init__(self, mac_address, **kwargs):
        self.mac_address = mac_address
        self.sock = None
        self.timeout = kwargs.get("socket_timeout", None)  # type: Optional[float]

    def connect(self):
        self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.sock.connect((self.mac_address, 1))

        if self.timeout is not None:
            self.sock.settimeout(self.timeout)

    def get_in_waiting(self) -> int:
        return 0

    def flush(self):
        pass

    def write(self, data: bytes) -> int:
        if self.sock is None:
            raise NotConnectedException("tried to write data")

        return self.sock.send(data)

    def read(self, count: int) -> bytes:
        if self.sock is None:
            raise NotConnectedException("tried to read data")

        return self.sock.recv(count)
