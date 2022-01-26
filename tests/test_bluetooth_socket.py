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
from unittest.mock import patch

from divo.bluetooth_socket import BluetoothSocket
from divo.exceptions import BluetoothSupportMissingException, NotConnectedException


class TestBluetoothSocket(unittest.TestCase):
    mac = "00:11:22:33:44:55"
    timeout = 23
    config_vars_with_bluetooth = {
        "HAVE_BLUETOOTH_H": 0,
        "HAVE_BLUETOOTH_BLUETOOTH_H": 1,
    }
    config_vars_without_bluetooth = {
        "HAVE_BLUETOOTH_H": 0,
        "HAVE_BLUETOOTH_BLUETOOTH_H": 0,
    }

    def test_args(self) -> None:
        with patch("sysconfig.get_config_vars", autospec=True) as mock:
            mock.return_value = self.config_vars_with_bluetooth

            s = BluetoothSocket(self.mac)
            mock.assert_called_with()
            assert s.BTPROTO_RFCOMM == 3
            assert s.mac_address == self.mac
            assert s.timeout is None

            s = BluetoothSocket(self.mac, self.timeout)
            assert s.BTPROTO_RFCOMM == 3
            assert s.mac_address == self.mac
            assert s.timeout == self.timeout

    def test_btsupport_exception(self) -> None:
        with patch("sysconfig.get_config_vars", autospec=True) as mock:
            mock.return_value = self.config_vars_without_bluetooth

            with self.assertRaises(BluetoothSupportMissingException) as ctx:
                BluetoothSocket(self.mac)
            assert str(ctx.exception).startswith("Your Python")

    def test_stubs(self) -> None:
        with patch("sysconfig.get_config_vars", autospec=True) as mock:
            mock.return_value = self.config_vars_with_bluetooth

            s = BluetoothSocket(self.mac)
            assert s.sock is None
            assert s.get_in_waiting() == 0
            assert s.flush() is None

            with self.assertRaises(NotConnectedException):
                s.write(b"\x23")

            with self.assertRaises(NotConnectedException):
                s.read(1)

    def test_connect(self) -> None:
        with patch("sysconfig.get_config_vars", autospec=True) as mock:
            mock.return_value = self.config_vars_with_bluetooth

            s = BluetoothSocket(self.mac)
            assert s.sock is None
            assert s.get_in_waiting() == 0
            assert s.flush() is None

            with self.assertRaises(NotConnectedException):
                s.write(b"\x23")

            with self.assertRaises(NotConnectedException):
                s.read(1)
