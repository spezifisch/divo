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

from divo.command import Command, CommandParser
from divo.exceptions import PacketChecksumError, PacketParsingError
from divo.packet import Packet


class TestPacket(unittest.TestCase):
    def test_build(self) -> None:
        p = Packet.build(Command.SET_SYSTEM_BRIGHTNESS, 23)
        exp = b"\x01\x04\x00t\x17\x8f\x00\x02"
        assert p == exp

    def test_parse_not_impl(self) -> None:
        raw = b"\x01\x04\x00t\x17\x8f\x00\x02"
        p = Packet.parse(CommandParser, raw)
        assert p is None  # parser is not yet implemented so nothing is returned

    def test_parse_incomplete(self) -> None:
        raw = b"\x01\x04\x00t\x17"
        with self.assertRaises(PacketParsingError) as ctx:
            Packet.parse(CommandParser, raw)
        assert str(ctx.exception) == "packet incomplete"

    def test_parse_bad_start(self) -> None:
        raw = b"\x23\x04\x00t\x17\x8f\x00\x02"
        with self.assertRaises(PacketParsingError) as ctx:
            Packet.parse(CommandParser, raw)
        assert str(ctx.exception).startswith("START_OF_PACKET value wrong")

    def test_parse_bad_end(self) -> None:
        raw = b"\x01\x04\x00t\x17\x8f\x00\x23"
        with self.assertRaises(PacketParsingError) as ctx:
            Packet.parse(CommandParser, raw)
        assert str(ctx.exception).startswith("END_OF_PACKET value wrong")

    def test_parse_bad_checksum(self) -> None:
        raw = b"\x01\x04\x00t\x17\x12\x34\x02"
        with self.assertRaises(PacketChecksumError) as ctx:
            Packet.parse(CommandParser, raw)
