# type: ignore
"""
This file is part of divo (https://github.com/spezifisch/divo).
Copyright (c) 2022 spezifisch (https://github.com/spezifisch)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
from unittest.mock import MagicMock, patch

from divo.bluetooth_serial import BluetoothSerial


@patch("serial.Serial", autospec=True)
class TestBluetoothSerial(unittest.TestCase):
    dev = "/dev/foo"

    def test_default(self, mock_serial: MagicMock) -> None:
        mock_serial.return_value.in_waiting = 1
        mock_serial.return_value.write.return_value = 2
        read_data = b"\x12\x34"
        mock_serial.return_value.read.return_value = read_data

        s = BluetoothSerial()
        mock_serial.assert_called_once_with("/dev/rfcomm0", timeout=1)

        assert s.connect() is None
        assert s.get_in_waiting() == 1
        assert s.flush() is None
        mock_serial.return_value.reset_output_buffer.assert_called_once_with()

        write_data = b"\x23\x42"
        assert s.write(write_data) == 2
        mock_serial.return_value.write.assert_called_once_with(write_data)

        assert s.read(2) == read_data
        mock_serial.return_value.read.assert_called_once_with(2)

    def test_args(self, mock_serial: MagicMock) -> None:
        BluetoothSerial(self.dev, timeout=23, foo=42)
        mock_serial.assert_called_once_with(self.dev, timeout=23, foo=42)
