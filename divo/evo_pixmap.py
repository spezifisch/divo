"""
This file is part of divo (https://github.com/spezifisch/divo).
Copyright (c) 2021 carolosf (https://github.com/carolosf), spezifisch ((https://github.com/spezifisch).
Copyright (c) 2019 johsam (https://github.com/johsam).

Original file:
https://github.com/johsam/timebox-evo-rest/blob/80820d010a242a45d26e6ff3f9b2b53546beb66b/pixmap/rawpixmap.py
Modifications by carolosf, spezifisch.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

import logging
from typing import List, Tuple

from PIL import Image, ImageEnhance

RGBColor = Tuple[int, int, int]
RGBAColor = Tuple[int, int, int, int]


class RawPixmap:

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    GRAY = (120, 120, 120)
    DARK_GRAY = (50, 50, 50)
    DEG_PLUS = (255, 128, 128)
    DEG_MINUS = (128, 128, 255)

    def __init__(self, width: int, height: int):

        self._width = width
        self._height = height
        self._pixels: List[RGBColor] = [(0, 0, 0)] * width * height
        self.clear()

    def clear(self) -> None:
        for i, _ in enumerate(self._pixels):
            self._pixels[i] = self.BLACK

    def setPixel(self, x: int, y: int, color: RGBColor) -> None:
        self._pixels[(x % self._width) + (y % self._height) * self._width] = color

    def getPixel(self, x: int, y: int) -> RGBColor:
        return self._pixels[(x % self._width) + (y % self._height) * self._width]

    def line(self, x: int, y: int, x2: int, y2: int, color: RGBColor) -> None:
        """Brensenham line algorithm"""
        steep = 0
        dx = abs(x2 - x)
        dy = abs(y2 - y)

        if (x2 - x) > 0:
            sx = 1
        else:
            sx = -1

        if (y2 - y) > 0:
            sy = 1
        else:
            sy = -1

        if dy > dx:
            steep = 1
            x, y = y, x
            dx, dy = dy, dx
            sx, sy = sy, sx
        d = (2 * dy) - dx

        for _ in range(0, dx):
            if steep:
                self.setPixel(y, x, color)
            else:
                self.setPixel(x, y, color)

            while d >= 0:
                y = y + sy
                d = d - (2 * dx)

            x = x + sx
            d = d + (2 * dy)
        self.setPixel(x2, y2, color)

    def set_rgb_pixels(self, data: List[RGBColor]) -> None:
        self._pixels = list(data)

    def get_rgb_pixels(self) -> List[RGBColor]:
        return self._pixels

    def get_pixel_data(self) -> List[int]:
        return [(t[0] << 16) + (t[1] << 8) + t[2] for t in self._pixels]

    def load_image(self, path: str) -> Image:
        try:
            result = Image.open(path)
            logging.info("Loaded image size=%s type=%s", result.size, result.mode)
            return result
        except Exception:  # pylint: disable=broad-except
            logging.warning("Failed to load image")
            return Image.new("RGBA", (self._width, self._height), color="black")

    @classmethod
    def blend_value(cls, under: int, over: int, a: int) -> int:
        return int((over * a + under * (255 - a)) / 255)

    @classmethod
    def blend_rgba(cls, under: RGBAColor, over: RGBAColor) -> Tuple[int, ...]:
        return tuple([cls.blend_value(under[i], over[i], over[3]) for i in (0, 1, 2)] + [255])

    def decode_image(self, image: Image, dim: bool = False) -> List[RGBColor]:
        w = self._width
        h = self._height

        image_mode = image.mode
        target = Image.new("RGBA", (w, h), color="black")

        source = image.convert("RGBA")
        if dim:
            enhancer = ImageEnhance.Brightness(source)
            source = enhancer.enhance(0.5)

        if source.size[0] != w or source.size[1] != h:
            source.thumbnail((w, h), Image.BICUBIC)

        if image_mode == "RGBA":
            # Alpha to black
            for y in range(source.size[1]):
                for x in range(source.size[0]):
                    source.putpixel((x, y), self.blend_rgba((0, 0, 0, 255), source.getpixel((x, y))))

        offset = ((w - source.size[0]) // 2, (h - source.size[1]) // 2)
        target.paste(source, offset)

        target = target.convert("RGB")

        return list(target.getdata())

    def view(self) -> None:
        def rgb_fg(r: int, g: int, b: int) -> str:
            return "\x1b[38;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"

        print("\x1b[0;0H", end="")

        for y in range(self._height):
            res = []
            for x in range(self._width):
                (r, g, b) = self.getPixel(x, y)
                if r == 0 and g == 0 and b == 0:
                    res.append(rgb_fg(20, 20, 20) + u"\u25A0")
                else:
                    res.append(rgb_fg(r, g, b) + u"\u25A0")
            print("".join(res))

    def pixel_list(self) -> List[RGBColor]:
        result = []
        for y in range(self._height):
            for x in range(self._width):
                result.append(self.getPixel(x, y))
        return result
