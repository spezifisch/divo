"""
This file is part of divo (https://github.com/spezifisch/divo).
Copyright (c) 2021 spezifisch (https://github.com/spezifisch).

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

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
