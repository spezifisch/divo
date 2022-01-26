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

    # to run unit tests in python builds without bt support we need this...
    @patch("socket.AF_BLUETOOTH", 23, create=True)
    @patch("socket.BTPROTO_RFCOMM", 42, create=True)
    def test_connect(self) -> None:
        with patch("sysconfig.get_config_vars", autospec=True) as mock_cfg:
            mock_cfg.return_value = self.config_vars_with_bluetooth

            with patch("socket.socket", autospec=True) as mock_sock:
                s = BluetoothSocket(self.mac)
                assert s.sock is None

                s.connect()
                assert s.sock is not None
                mock_sock.assert_called_once()
                # check for our fake values patched with the decorators
                assert mock_sock.call_args.args[0] == 23
                assert mock_sock.call_args.args[2] == 42
                mock_sock.return_value.connect.assert_called_once_with((self.mac, 1))
                mock_sock.return_value.settimeout.assert_not_called()

                # send data
                data = b"\x12\x34"
                s.write(data)
                mock_sock.return_value.send.assert_called_once_with(data)

                # receive data
                data = b"\x12\x23"
                count = 2
                mock_sock.return_value.recv.return_value = data
                received_data = s.read(count)
                mock_sock.return_value.recv.assert_called_once_with(count)
                assert received_data == data

            # test timeout setting
            with patch("socket.socket", autospec=True) as mock_sock:
                timeout = 123.45
                s = BluetoothSocket(self.mac, timeout)
                assert s.sock is None

                s.connect()
                assert s.sock is not None
                mock_sock.assert_called_once()
                assert mock_sock.call_args.args[0] == 23
                assert mock_sock.call_args.args[2] == 42
                mock_sock.return_value.connect.assert_called_once_with((self.mac, 1))
                mock_sock.return_value.settimeout.assert_called_once_with(timeout)
