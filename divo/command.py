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

from enum import IntEnum
from typing import Any, Optional

from loguru import logger

from .command_base import CommandBase, CommandParserBase


class Command(CommandBase):
    SET_TIME = 24
    SET_SYSTEM_COLOR = 36
    SEND_APP_NEWEST_TIME = 38
    SET_24_HOUR = 45
    LIGHT_CURRENT_LEVEL = 49
    SET_BOX_COLOR = 68
    SET_BOX_MODE = 69
    GET_BOX_MODE = 70
    SET_MUL_BOX_COLOR = 73
    SET_CLIMATE = 95
    SET_SYSTEM_BRIGHTNESS = 116
    SET_GAME = 160
    SET_SLEEP_COLOR = 173
    SET_USER_GIF = 177

    @classmethod
    def get_name(cls, value: int) -> str:
        try:
            return cls(value).name
        except ValueError:
            return "UNKNOWN"


# when one of the following commands is sent the device doesn't send back a response
COMMANDS_WITHOUT_RESPONSE = [
    Command.SEND_APP_NEWEST_TIME,
    Command.SET_SLEEP_COLOR,
]


class CommandParser(CommandParserBase):
    @staticmethod
    def parse(cmd_type: int, data: bytes) -> Any:
        if cmd_type == Command.SET_BOX_COLOR.value:
            return SetBoxColor.from_data(data)
        elif cmd_type == Command.SET_MUL_BOX_COLOR.value:
            return SetMulBoxColor.from_data(data)
        else:
            name = Command.get_name(cmd_type)
            logger.warning(f"parser for cmd_type {cmd_type} ({name}) not implemented")

        return None

    @staticmethod
    def parse_response(cmd_type: int, data: bytes) -> Any:
        if cmd_type == Command.GET_BOX_MODE.value:
            return GetBoxMode.from_data(data)
        else:
            name = Command.get_name(cmd_type)
            logger.warning(f"response parser for cmd_type {cmd_type} ({name}) not implemented")

        return None


class BoxMode(IntEnum):
    ENV = 0
    LIGHT = 1
    HOT = 2
    SPECIAL = 3
    MUSIC = 4
    USER_DEFINE = 5
    WATCH = 6  # is actually score blue/red board
    SCORE = 7  # doesn't work?


#  	const modes = {
#   			clock: "00",
#   			lighting: "01",
#   			cloud: "02",
#   			effects: "03",
#   			visualization: "04",
#   			custom: "05",
#   			score: "06"
#   		};


class LightMode(IntEnum):
    CLOCK = 0
    TEMPERATURE = 1
    COLOR = 2
    SPECIAL = 3
    SOUND = 4
    USER = 5


class TimeType(IntEnum):
    """Different clock layouts that can be chosen"""

    BIG = 0  # fullscreen
    RAINBOW = 1  # rainbow
    BORDER = 2  # boxed
    ANALOG = 3  # analog square
    BIG_INV = 4  # fullscreen negative
    ANALOG_ROUND = 5  # analog round
    SMALL = 6  # widescreen


class WeatherType(IntEnum):
    CLEAR = 1
    CLOUDY = 3
    THUNDERSTORM = 5
    RAIN = 6
    SNOW = 8
    FOG = 9


class ActivatedModes:
    @staticmethod
    def get_default() -> "ActivatedModes":
        return ActivatedModes(clock=True)

    def __init__(self, clock: bool = False, weather: bool = False, temperature: bool = False, date: bool = False):
        self.clock = clock
        self.weather = weather
        self.temperature = temperature
        self.date = date


class GetBoxMode:
    @staticmethod
    def from_data(data: bytes) -> "GetBoxMode":
        return GetBoxMode(
            mode=data[0],
            temp_type=data[1],
            light_mode=data[2],
            light_r=data[3],
            light_g=data[4],
            light_b=data[5],
            level=data[6],
            music_type=data[7],
            sys_light=data[8],
            time_type=data[9],
            time_r=data[10],
            time_g=data[11],
            time_b=data[12],
            temp_r=data[13],
            temp_g=data[14],
            temp_b=data[15],
            raw=data,
        )

    def __init__(
        self,
        mode: int = 0,
        temp_type: int = 0,
        light_mode: int = 0,
        light_r: int = 0,
        light_g: int = 0,
        light_b: int = 0,
        light_level: int = 0,
        level: int = 0,
        music_type: int = 0,
        sys_light: int = 0,
        time_type: int = 0,
        time_r: int = 0,
        time_g: int = 0,
        time_b: int = 0,
        temp_r: int = 0,
        temp_g: int = 0,
        temp_b: int = 0,
        raw: Optional[bytes] = None,
    ):
        self._raw: Optional[bytes] = raw

        self.mode = mode
        self.temp_type = temp_type
        self.light_mode = light_mode
        self.light_r = light_r
        self.light_g = light_g
        self.light_b = light_b
        self.light_level = light_level
        self.level = level
        self.music_type = music_type
        self.sys_light = sys_light
        self.time_type = time_type
        self.time_r = time_r
        self.time_g = time_g
        self.time_b = time_b
        self.temp_r = temp_r
        self.temp_g = temp_g
        self.temp_b = temp_b

    def __str__(self) -> str:
        return (
            f"GetBoxMode<mode={self.mode} temp_type={self.temp_type} light_mode={self.light_mode} "
            + f"light_r={self.light_r} light_g={self.light_g} light_b={self.light_b} time_type={self.time_type} "
            + f"time_r={self.time_r} time_g={self.time_g} time_b={self.time_b} "
            + f"temp_r={self.temp_r} temp_g={self.temp_g} temp_b={self.temp_b}>"
        )


class SetBoxColor:
    @staticmethod
    def from_data(data: bytes) -> "SetBoxColor":
        # crap = 00 0a 0a 04 aa 7f 00 f4 01 00
        _ = data[:10]

        palette_len = data[10]
        palette = data[11 : 11 + 3 * palette_len]
        image = data[11 + 3 * palette_len :]

        return SetBoxColor(
            palette=palette,
            image=image,
            raw=data,
        )

    def __init__(self, raw: bytes, palette: bytes, image: bytes):
        self.raw = raw

        self.palette = palette
        self.image = image

    def __str__(self) -> str:
        return f"SetBoxColor<palette={self.palette!r} image={self.image!r}>"


class SetMulBoxColor(SetBoxColor):
    @staticmethod
    def from_data(data: bytes) -> "SetBoxColor":
        # crap = 2c 01 00 aa a2 00 1b 01 00
        _ = data[:9]
        palette_len = data[9]
        palette = data[10 : 10 + 3 * palette_len]
        image = data[10 + 3 * palette_len :]

        return SetBoxColor(
            palette=palette,
            image=image,
            raw=data,
        )
