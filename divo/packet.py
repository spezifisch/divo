"""
This file is part of divo (https://github.com/spezifisch/divo).
Copyright (c) 2021 spezifisch (https://github.com/spezifisch), carolosf (https://github.com/carolosf).

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

from typing import Any, Optional, Union

from .command_base import CommandBase, CommandParserBase
from .exceptions import PacketChecksumError, PacketParsingError
from .packet_base import PacketBase


class Packet(PacketBase):
    @classmethod
    def build(cls, cmd: CommandBase, payload: Union[bytes, int, None] = None) -> bytes:
        # many commands only have one or no bytes payload
        if isinstance(payload, int):
            # for convenience if only a single byte is sent
            payload = bytes([payload])
        elif payload is None:
            payload = b""

        # add header
        size = len(payload) + 3
        size_lo = size & 0xFF
        size_hi = (size >> 8) & 0xFF
        command = cmd.value & 0xFF
        packet = bytes([cls.START_OF_PACKET, size_lo, size_hi, command])

        # add payload
        packet += payload

        # add checksum and end marker
        checksum = sum(packet[1:]) & 0xFFFF
        checksum_lo = checksum & 0xFF
        checksum_hi = (checksum >> 8) & 0xFF
        packet += bytes([checksum_lo, checksum_hi, cls.END_OF_PACKET])

        return packet

    @staticmethod
    def __hex_checksum(checksum: int) -> str:
        tmp = hex(checksum)
        return tmp[4:7] + tmp[2:4]

    @classmethod
    def parse(cls, parser: CommandParserBase, packet: bytes) -> Any:
        try:
            start = packet[0]
            size_lo = packet[1]
            size_hi = packet[2]
            size = ((size_hi & 0xFF) << 8) | (size_lo & 0xFF)
            cmd_type = packet[3]
            data = packet[4 : 3 + size - 2]
            checksum_lo = packet[3 + size - 2]
            checksum_hi = packet[3 + size - 1]
            checksum = ((checksum_hi & 0xFF) << 8) | (checksum_lo & 0xFF)
            end = packet[3 + size]
        except IndexError:
            raise PacketParsingError("packet incomplete")

        if start != PacketBase.START_OF_PACKET:
            raise PacketParsingError(f"START_OF_PACKET value wrong: {start}")
        if end != PacketBase.END_OF_PACKET:
            raise PacketParsingError(f"END_OF_PACKET value wrong: {end}")

        wanted_checksum = sum(packet[1 : 3 + size - 2]) & 0xFFFF
        if checksum != wanted_checksum:
            raise PacketChecksumError(
                f"checksum wrong, got: {Packet.__hex_checksum(checksum)} "
                + f"wanted: {Packet.__hex_checksum(wanted_checksum)}"
            )

        return parser.parse(cmd_type, data)


class ResponsePacket(PacketBase):
    MAGIC_CHECK = 4
    MAGIC_UNK1 = 85

    @classmethod
    def build(cls, cmd: CommandBase, payload: Optional[Union[bytes, int]] = None) -> bytes:
        raise NotImplementedError

    @classmethod
    def parse(cls, parser: CommandParserBase, packet: bytes) -> Any:
        try:
            start = packet[0]
            size_lo = packet[1]
            size_hi = packet[2]
            size = ((size_hi & 0xFF) << 8) | (size_lo & 0xFF)
            cmd_chk = packet[3]
            cmd_type = packet[4]
            unk1 = packet[5]
            data = packet[6 : 2 + size + 1]
            end = packet[2 + size + 1]
        except IndexError:
            raise PacketParsingError("packet incomplete")

        if start != cls.START_OF_PACKET:
            raise PacketParsingError(f"START_OF_PACKET value wrong: {start}")
        if end != cls.END_OF_PACKET:
            raise PacketParsingError(f"END_OF_PACKET value wrong: {end}")
        if cmd_chk != cls.MAGIC_CHECK:
            raise PacketParsingError(f"MAGIC_CHECK value wrong: {cmd_chk}")
        if unk1 != cls.MAGIC_UNK1:
            raise PacketParsingError(f"MAGIC_UNK1 value wrong: {unk1}")

        return parser.parse_response(cmd_type, data)
