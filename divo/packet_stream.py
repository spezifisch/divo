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

from loguru import logger

from .helpers import chunks
from .image import Color, ImageBuffer, Palette


class PacketStreamDecoder:
    _debug = False

    def __init__(self, palette: bytes, payload: bytes):
        # parse palette
        self.palette = self.parse_palette(palette)

        # decode image
        self.image = self.parse_image(payload, self.palette)

    @staticmethod
    def parse_palette(data: bytes) -> Palette:
        ret = Palette()
        ret.palette += [Color(*data[x : x + 3]) for x in range(0, len(data), 3)]
        return ret

    @classmethod
    def parse_image(cls, data: bytes, palette: Palette) -> ImageBuffer:
        # parse byte data to binary string
        binary_string = ""
        for bx in data:
            by = f"{bx:08b}"
            by = by[::-1]
            binary_string += by

        bits_per_pixel = palette.bits_per_pixel()

        if cls._debug:
            # print payload as binary
            pixels_per_row = 16
            bits_per_row = pixels_per_row * bits_per_pixel
            for row in range(16):
                payload_start = row * bits_per_row
                payload_end = payload_start + bits_per_row
                row_payload = binary_string[payload_start:payload_end]
                print(chunks(row_payload, bits_per_pixel))

        # build image
        buf = ImageBuffer()
        for pos in range(0, len(binary_string) - 2, bits_per_pixel):
            pixel_no = int(pos / bits_per_pixel)
            x = pixel_no % buf.width
            y = int(pixel_no / buf.width)

            if y >= buf.height:
                extra_crap = binary_string[pos:]
                logger.info(f"got extra crap after image: {extra_crap}")
                break

            bidx = binary_string[pos : pos + bits_per_pixel][::-1]
            idx = int(bidx, 2)
            try:
                color = palette[idx]
                buf.set(x, y, color)
            except IndexError:
                logger.warning(f"tried to set color index {idx}")

        return buf
