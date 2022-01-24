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
import sysconfig
from typing import Optional

from .bluetooth_base import BluetoothBase
from .exceptions import BluetoothSupportMissingException, NotConnectedException


class BluetoothSocket(BluetoothBase):
    """
    Bluetooth connection using native Bluetooth socket support.
    """

    def __init__(self, mac_address: str, socket_timeout: Optional[float] = None):
        self.mac_address = mac_address
        self.sock: Optional[socket.socket] = None
        self.timeout = socket_timeout

        # workaround so we can at least make unit tests on python versions missing bluetooth support
        self.BTPROTO_RFCOMM = 3
        try:
            self.BTPROTO_RFCOMM = socket.BTPROTO_RFCOMM  # type: ignore
        except AttributeError:
            pass

        # check if bluetooth sockets are supported
        # see https://stackoverflow.com/a/29108576
        if (
            not sysconfig.get_config_vars()["HAVE_BLUETOOTH_H"]
            and not sysconfig.get_config_vars()["HAVE_BLUETOOTH_BLUETOOTH_H"]
        ):
            raise BluetoothSupportMissingException("Your Python interpreter is missing Bluetooth support.")

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, self.BTPROTO_RFCOMM)
        self.sock.connect((self.mac_address, 1))

        if self.timeout is not None:
            self.sock.settimeout(self.timeout)

    def get_in_waiting(self) -> int:
        return 0

    def flush(self) -> None:
        return

    def write(self, data: bytes) -> int:
        if self.sock is None:
            raise NotConnectedException("tried to write data")

        return self.sock.send(data)

    def read(self, count: int) -> bytes:
        if self.sock is None:
            raise NotConnectedException("tried to read data")

        return self.sock.recv(count)
