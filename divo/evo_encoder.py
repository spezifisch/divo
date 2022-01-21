"""
This file is part of divo (https://github.com/spezifisch/divo).
Copyright (c) 2019 johsam (https://github.com/johsam).

Original file: https://github.com/johsam/timebox-evo-rest/blob/80820d010a242a45d26e6ff3f9b2b53546beb66b/evo/encoder.py
No modifications were made.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

import binascii
import math
import struct
from collections import OrderedDict
from typing import List


class EvoEncoder:
    def __init__(self) -> None:
        pass

    @staticmethod
    def encode_colours(colour_array: List[int]) -> str:
        colour_dict = OrderedDict()  # type: OrderedDict[int,int]
        colour_order = []
        for colour in colour_array:
            if colour not in colour_dict:
                colour_dict[colour] = len(colour_dict)
            colour_order.append(colour_dict[colour])

        bits_needed = int(math.ceil(math.log(len(colour_dict), 2)))
        if bits_needed == 0:
            bits_needed = 1
        img_data = "{0:02x}".format(len(colour_dict) % 256)
        for colour in colour_dict:
            img_data += "{0:06x}".format(colour)

        c_data = ""
        for i in colour_order:
            c_data += "{0:08b}".format(i)[-1::-1][:bits_needed]
        for i in range(-1, len(c_data) - 1, 8):
            if i == -1:
                img_data += "{0:02x}".format(int(c_data[i + 8 :: -1], 2))
                continue
            img_data += "{0:02x}".format(int(c_data[i + 8 : i : -1], 2))
        return img_data

    @staticmethod
    def crc(pl: bytes) -> bytes:
        csum = sum(pl)
        lsb = csum & 0xFF
        msb = (csum >> 8) & 0xFF
        return b"%c%c" % (lsb, msb)

    @staticmethod
    def length(pl: bytes) -> bytes:
        return struct.pack("<H", 2 + len(pl))

    @staticmethod
    def image_bytes(colour_array: List[int]) -> bytes:
        hex_data = "44000A0A04AA2D00000000" + EvoEncoder.encode_colours(colour_array)
        payload = binascii.unhexlify(hex_data)
        payload = EvoEncoder.length(payload) + payload
        return b"\x01" + payload + EvoEncoder.crc(payload) + b"\x02"

    @staticmethod
    def encode_hex(hex_data: bytes) -> bytes:
        payload = binascii.unhexlify(hex_data)
        payload = EvoEncoder.length(payload) + payload
        return b"\x01" + payload + EvoEncoder.crc(payload) + b"\x02"

    @staticmethod
    def encode_bytes(payload: bytes) -> bytes:
        payload = EvoEncoder.length(payload) + payload
        return b"\x01" + payload + EvoEncoder.crc(payload) + b"\x02"
