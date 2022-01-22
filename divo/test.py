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

import math
from time import sleep
from typing import Any, Tuple

from loguru import logger

from .command import ActivatedModes, Command, CommandParser, TimeType, WeatherType
from .evo_encoder import EvoEncoder
from .evo_pixmap import RawPixmap
from .packet import Packet, ResponsePacket
from .pixoo import Pixoo


def parse_packet(data: bytes) -> Any:
    return Packet.parse(CommandParser(), data)


def parse_response_packet(data: bytes) -> Any:
    return ResponsePacket.parse(CommandParser(), data)


def hsv_to_rgb(h: int, s: int, v: int) -> Tuple[float, float, float]:
    """Convert HSV color space to RGB color space
    source: https://code.activestate.com/recipes/576554-covert-color-space-from-hsv-to-rgb-and-rgb-to-hsv/
    by Victor Lin, MIT license

    @param h: Hue
    @param s: Saturation
    @param v: Value
    return (r, g, b)
    """

    hi = math.floor(h / 60.0) % 6
    f = (h / 60.0) - math.floor(h / 60.0)
    p = v * (1.0 - s)
    q = v * (1.0 - (f * s))
    t = v * (1.0 - ((1.0 - f) * s))
    return {
        0: (v, t, p),
        1: (q, v, p),
        2: (p, v, t),
        3: (p, q, v),
        4: (t, p, v),
        5: (v, p, q),
    }[hi]


def test_pattern(test: int, d: Pixoo) -> None:
    if test == 1:
        logger.info("sleep color test")
        d.set_sleep_color(100, 0, 0)
    elif test == 2:
        logger.info("score board test")
        d.set_score(23, 42)
        d.set_brightness(50)
        sleep(0.5)

        d.set_brightness(99)
        sleep(0.5)
    elif test == 3:
        logger.info("rgb+ test")
        d.set_brightness(99)
        d.set_system_color(255, 100, 100)
        sleep(0.5)
        d.set_sleep_color(255, 0, 0)
        sleep(0.5)
        d.set_sleep_color(0, 255, 0)
        sleep(0.5)
        d.set_sleep_color(0, 0, 255)
        sleep(0.5)
        d.set_sleep_color(255, 0, 255)
        sleep(0.5)
    elif test == 4:
        logger.info("music viz test")
        d.set_music_visualizer(6)
        sleep(1)

        logger.info("game mode test -> slot")
        # 0=tetris
        # 1=slots
        # 2=dice
        # 3=eight-ball
        # 4=breakout
        # 5=tetris again?
        # 6=half a pong
        # 7=rock paper scissors
        # 8=idk some man
        d.set_game(True, 1)
        sleep(1)
    elif test == 5:
        logger.info("digital clock mode rainbow test")
        # somehow this keeps Pixoo from switching away from clock mode
        d.send_app_newest_time(False)

        for color in ((255, 0, 0), (0, 255, 0), (0, 0, 255)):
            r, g, b = color
            resp = d.set_light_mode_clock(TimeType.RAINBOW, r, g, b)
            logger.info(f"set clock to rainbow({r}, {g}, {b}), response: {resp}")
            sleep(0.4)

        resp = d.set_light_mode_clock(TimeType.SMALL, 255, 220, 220)
        logger.info("set clock to small, response:", resp)

        d.set_brightness(100)
    elif test == 6:
        logger.info("weird temperature mode test")
        # note: this is not the temperature mode the app uses
        box_mode = d.get_box_mode()
        d.set_light_mode_temperature(box_mode)
        sleep(1)
        d.set_brightness(50)
    elif test == 7:
        logger.info("green analog clock test")
        # SPP_LIGHT_CURRENT_LEVEL
        p1 = b"\x01\x03\x00\x31\x34\x00\x02"
        # SPP_SEND_APP_NEWEST_TIME
        p2 = b"\x01\x04\x00\x26\x00\x2a\x00\x02"
        parse_packet(p1)
        parse_packet(p2)
        d.write(p1)
        # d.write(p2)
        # clock green
        # SPP_SET_BOX_MODE
        p3 = bytes([1, 13, 0, 69, 0, 1, 100, 1, 0, 0, 0, 0, 255, 5, 188, 1, 2])
        parse_packet(p3)
        d.write(p3)
    elif test == 8:
        logger.info("light mode rainbow test")
        d.set_brightness(100)

        d.set_light_mode_light(0xF8, 0x01, 0x79)

        for h in range(0, 255, 5):
            rgb = hsv_to_rgb(h, 1, 1)
            r, g, b = [int(round(x * 255)) for x in rgb]
            d.set_light_mode_light(r, g, b)
            sleep(0.1)
    elif test == 9:
        logger.info("VJ test")
        d.send_app_newest_time(False)
        for i in range(16):
            logger.info(f"VJ mode {i}")
            d.set_light_mode_vj(i)
            sleep(1)

        logger.info("VJ mode 2 again")
        d.set_light_mode_vj(2)
    elif test == 10:
        logger.info("clock mode border test")
        d.set_time()
        d.send_app_newest_time(False)
        d.set_light_mode_clock(TimeType.BORDER, 0x9D, 0xFC, 0x05)
        d.set_brightness(100)
    elif test == 11:
        logger.info("image mode mudkip test")
        from binascii import unhexlify

        p = unhexlify(
            "01860044000a0a04aa7f00f40100080000004dbbef2989c8c1c3c5ff9f00ffffff1f1f30bf5c1500002001000000002402"
            + "000000002402000000004402000000904409000000922449b00140922449b20d64d22469420e64e22471420e27e32471c8"
            + "0ff89b2449ff0d00d6b6adb60d00a06d92b40d00a06d89a40100106d89a401001049893400512802"
        )
        parse_packet(p)
        d.write(p)
    elif test == 12:
        d.set_time()
        d.set_light_mode_clock(
            TimeType.BIG,
            0,
            0,
            255,
            ActivatedModes(clock=True, weather=True, temperature=True, date=False),
        )
        d.set_brightness(10)

        rp = RawPixmap(16, 16)
        img = rp.load_image("test.png")
        pixels = rp.decode_image(img)
        rp.set_rgb_pixels(pixels)

        ee = EvoEncoder()
        x = ee.image_bytes(rp.get_pixel_data())
        parse_packet(x)
        d.write(x)
    elif test == 13:
        d.set_music_visualizer(4)
    elif test == 14:
        d.set_game(True, 0)
        sleep(1)
        d.set_score(50, 999)
        sleep(1)
        d.set_time()
        d.set_light_mode_clock(
            TimeType.BIG,
            0,
            0,
            255,
            ActivatedModes(clock=True, weather=True, temperature=True, date=False),
        )
        sleep(1)
        d.set_light_mode_vj(1)
        sleep(1)
        d.set_brightness(10)
        sleep(1)

        # val = bytes([BoxMode.USER_DEFINE])
        # d.write_command(Command.SET_BOX_MODE, val)
        # https://github.com/jfroehlich/node-p1x3lramen/blob/main/source/devices/pixoo.js
        # https://github.com/DavidVentura/divoom/blob/master/divoom/protocol.py

        val = bytes([12, WeatherType.CLEAR])
        d.write_command(Command.SET_CLIMATE, val)

        val = bytes([0])
        d.write_command(Command.SET_24_HOUR, val)
        sleep(1)
    else:
        raise ValueError("invalid test id")
