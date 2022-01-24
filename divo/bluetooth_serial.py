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

from typing import Any

import serial

from .bluetooth_base import BluetoothBase


class BluetoothSerial(BluetoothBase):
    """
    Communicate with Bluetooth device using rfcomm device. Deprecated in favor of bluetooth_socket.

    To use this you would run the `rfcomm` command from bluez separately to establish the connection:
    $ sudo rfcomm connect rfcomm0 11:75:58:xx:xx:xx 1
    """

    def __init__(self, serial_device_file: str = "/dev/rfcomm0", **serial_args: Any):
        if "timeout" not in serial_args:
            serial_args["timeout"] = 1

        self.fd = serial.Serial(serial_device_file, **serial_args)

    def connect(self) -> None:
        pass

    def get_in_waiting(self) -> int:
        ret = self.fd.in_waiting
        assert isinstance(ret, int)
        return ret

    def flush(self) -> None:
        self.fd.reset_output_buffer()

    def write(self, data: bytes) -> int:
        ret = self.fd.write(data)
        assert isinstance(ret, int)
        return ret

    def read(self, count: int) -> bytes:
        ret = self.fd.read(count)
        assert isinstance(ret, bytes)
        return ret
