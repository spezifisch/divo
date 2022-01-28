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

from divo.command import Command, CommandParser
from divo.exceptions import PacketChecksumError, PacketParsingError
from divo.packet import Packet, ResponsePacket


class TestPacket(unittest.TestCase):
    def test_build(self) -> None:
        p = Packet.build(Command.SET_SYSTEM_BRIGHTNESS, 23)
        exp = b"\x01\x04\x00t\x17\x8f\x00\x02"
        assert p == exp

    def test_build_bytes_payload(self) -> None:
        p = Packet.build(Command.SET_SYSTEM_BRIGHTNESS, b"\x17")
        exp = b"\x01\x04\x00t\x17\x8f\x00\x02"
        assert p == exp

    def test_build_no_payload(self) -> None:
        p = Packet.build(Command.SET_SYSTEM_BRIGHTNESS)
        exp = b"\x01\x03\x00tw\x00\x02"
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
        with self.assertRaises(PacketChecksumError):
            Packet.parse(CommandParser, raw)

    def test_validating(self) -> None:
        raw_good = b"\x01\x04\x00t\x17\x8f\x00\x02"
        raw_bad = b"\x01\x23\x00t\x17\x8f\x00\x02"
        assert Packet.is_valid(CommandParser, raw_good) is True
        assert Packet.is_valid(CommandParser, raw_bad) is False


class TestResponsePacket(unittest.TestCase):
    def test_build_not_impl(self) -> None:
        with self.assertRaises(NotImplementedError):
            ResponsePacket.build(Command.SET_BOX_MODE, 123)

    def test_parse_success(self) -> None:
        raw = b"\x01\x03\x00\x04\x17\x55\x02"
        p = ResponsePacket.parse(CommandParser, raw)
        assert p is None

    def test_parse_incomplete(self) -> None:
        raw = b"\x01"
        with self.assertRaises(PacketParsingError) as ctx:
            ResponsePacket.parse(CommandParser, raw)
        assert str(ctx.exception) == "packet incomplete"

    def test_parse_bad_start(self) -> None:
        raw = b"\x23\x03\x00\x04\x17\x55\x02"
        with self.assertRaises(PacketParsingError) as ctx:
            ResponsePacket.parse(CommandParser, raw)
        assert str(ctx.exception).startswith("START_OF_PACKET value wrong")

    def test_parse_bad_end(self) -> None:
        raw = b"\x01\x03\x00\x04\x17\x55\x23"
        with self.assertRaises(PacketParsingError) as ctx:
            ResponsePacket.parse(CommandParser, raw)
        assert str(ctx.exception).startswith("END_OF_PACKET value wrong")

    def test_parse_bad_magic1(self) -> None:
        raw = b"\x01\x03\x00\x23\x17\x55\x02"
        with self.assertRaises(PacketParsingError) as ctx:
            ResponsePacket.parse(CommandParser, raw)
        assert str(ctx.exception).startswith("MAGIC_CHECK value wrong")

    def test_parse_bad_magic2(self) -> None:
        raw = b"\x01\x03\x00\x04\x17\x23\x02"
        with self.assertRaises(PacketParsingError) as ctx:
            ResponsePacket.parse(CommandParser, raw)
        assert str(ctx.exception).startswith("MAGIC_UNK1 value wrong")

    def test_validating(self) -> None:
        raw_good = b"\x01\x03\x00\x04\x17\x55\x02"
        raw_bad = b"\x01\x23\x00\x04\x17\x55\x02"
        assert ResponsePacket.is_valid(CommandParser, raw_good) is True
        assert ResponsePacket.is_valid(CommandParser, raw_bad) is False
