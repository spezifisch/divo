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

from datetime import datetime
from typing import Any, Optional, Union

from loguru import logger

from .bluetooth_base import BluetoothBase
from .command import (
    COMMANDS_WITHOUT_RESPONSE,
    ActivatedModes,
    BoxMode,
    Command,
    CommandParser,
    GetBoxMode,
    LightMode,
    TimeType,
)
from .command_base import CommandBase
from .exceptions import CommandNoReplyException, PacketWriteException
from .packet import Packet, ResponsePacket


class Pixoo:
    def __init__(self, bt_device: BluetoothBase) -> None:
        self.comm = bt_device
        self.comm.connect()
        self.comm.flush()

        self.command_parser = CommandParser()

    def write(self, data: bytes) -> Optional[Any]:
        """
        send raw data to Pixoo and receive and parse response packet

        :param data: raw packet to send
        :return: ResponsePacket if this command has a response and we successfully received it
        """

        if not Packet.is_valid(self.command_parser, data):
            raise PacketWriteException("tried to send invalid packet")

        self.comm.write(data)
        logger.debug(f"sending {list(data)}")

        cmd = data[3]
        if cmd in COMMANDS_WITHOUT_RESPONSE:
            return None

        # read packet start marker and packet size
        response = self.comm.read(3)
        if len(response) == 3:
            if response[0] == Packet.START_OF_PACKET:
                size_lo = response[1]
                size_hi = response[2]
                size = ((size_hi & 0xFF) << 8) | (size_lo & 0xFF)
                logger.debug(f"receiving payload with length {size}")

                # read rest of packet
                rest = self.comm.read(size + 1)
                if len(rest):
                    if rest[-1] == Packet.END_OF_PACKET:
                        # we received a complete packet
                        packet = response + rest
                        logger.debug(f"received {list(packet)}")
                        return ResponsePacket.parse(self.command_parser, packet)
                    else:
                        logger.error(f"end marker not present: rest={rest!r}")
                else:
                    logger.error("rest empty")
            else:
                logger.error(f"received garbage: {response!r}")
        else:
            logger.error(f"didn't receive enough data for response, only: {response!r}")

        return None

    def write_command(
        self, cmd: CommandBase, cmd_data: Optional[Union[bytes, int]] = None, need_response: bool = False
    ) -> Optional[Any]:
        """
        send command with payload and receive response if there is any

        :param cmd: Command id
        :param cmd_data: raw data, command-specific
        :return: parsed ResponsePacket if we received it successfully
        """
        resp = self.write(Packet.build(cmd, cmd_data))
        if need_response and resp is None:
            raise CommandNoReplyException(f"expected a reply to command {cmd.value}")

        return resp

    def write_command_with_response(
        self, cmd: CommandBase, cmd_data: Optional[Union[bytes, int]] = None
    ) -> ResponsePacket:
        resp = self.write_command(cmd, cmd_data, need_response=True)
        assert isinstance(resp, ResponsePacket)
        return resp

    def set_brightness(self, percent: int) -> ResponsePacket:
        if not (0 <= percent <= 100):
            raise ValueError("out of range")

        return self.write_command_with_response(Command.SET_SYSTEM_BRIGHTNESS, percent)

    def set_score(self, blue_score: int, red_score: int) -> ResponsePacket:
        rs_lo = red_score & 0xFF
        rs_hi = (red_score >> 8) & 0xFF
        bs_lo = blue_score & 0xFF
        bs_hi = (blue_score >> 8) & 0xFF
        val = bytes([BoxMode.WATCH, 0, rs_lo, rs_hi, bs_lo, bs_hi, 0, 0, 0, 0])
        return self.write_command_with_response(Command.SET_BOX_MODE, val)

    def set_music_visualizer(self, visualizer: int) -> ResponsePacket:
        if not (0 <= visualizer <= 11):
            raise ValueError("visualizer id out of range")

        val = bytes([BoxMode.MUSIC, visualizer & 0xFF] + [0] * 8)
        return self.write_command_with_response(Command.SET_BOX_MODE, val)

    def set_time(self, ts: Optional[datetime] = None) -> ResponsePacket:
        if ts is None:
            ts = datetime.now()

        year = ts.year
        month = ts.month
        day_of_month = ts.day
        hours = ts.hour
        minutes = ts.minute
        seconds = ts.second
        day_of_week = ts.isoweekday() % 7

        val = bytes(
            [
                int(year % 100),
                int(year / 100),
                month,  # 1 to 12
                day_of_month,  # 1 to 31
                hours,
                minutes,
                seconds,
                day_of_week,  # 0=sun, 1=mon, ..6=sat
            ]
        )
        return self.write_command_with_response(Command.SET_TIME, val)

    def set_game(self, enable: bool, game: int) -> ResponsePacket:
        if not (0 <= game <= 8):
            raise ValueError("game id out of range")

        val = bytes([int(enable), game])
        return self.write_command_with_response(Command.SET_GAME, val)

    def set_system_color(self, r: int, g: int, b: int) -> ResponsePacket:
        val = bytes([r & 0xFF, g & 0xFF, b & 0xFF])
        return self.write_command_with_response(Command.SET_SYSTEM_COLOR, val)

    def set_sleep_color(self, r: int, g: int, b: int) -> None:
        val = bytes([r & 0xFF, g & 0xFF, b & 0xFF])
        self.write_command(Command.SET_SLEEP_COLOR, val)

    def get_box_mode(self) -> GetBoxMode:
        data = self.write_command(Command.GET_BOX_MODE)
        assert isinstance(data, bytes)
        return GetBoxMode.from_data(data)

    def set_light_mode_clock(
        self,
        time_type: TimeType,
        red: int,
        green: int,
        blue: int,
        modes: Optional[ActivatedModes] = None,
    ) -> ResponsePacket:
        if modes is None:
            modes = ActivatedModes.get_default()

        val = bytes(
            [
                BoxMode.ENV.value,
                1,
                time_type.value,
                int(modes.clock),
                int(modes.weather),
                int(modes.temperature),
                int(modes.date),
                red,
                green,
                blue,
            ]
        )
        return self.write_command_with_response(Command.SET_BOX_MODE, val)

    def set_light_mode_temperature(self, box_mode: GetBoxMode) -> ResponsePacket:
        val = bytes(
            [
                LightMode.TEMPERATURE.value,
                box_mode.temp_type,
                box_mode.temp_r,
                box_mode.temp_g,
                box_mode.temp_b,
                0,
            ]
        )
        return self.write_command_with_response(Command.SET_BOX_MODE, val)

    def send_app_newest_time(self, value: Optional[bool]) -> None:
        if value is None:
            data = -1 & 0xFF
        else:
            data = int(value)
        self.write_command(Command.SEND_APP_NEWEST_TIME, data)

    def set_light_mode_light(
        self,
        red: int,
        green: int,
        blue: int,
        modes: Optional[ActivatedModes] = None,
    ) -> ResponsePacket:
        if modes is None:
            modes = ActivatedModes.get_default()

        val = bytes(
            [
                BoxMode.LIGHT.value,
                red,
                green,
                blue,
                0x14,
                0,
                int(modes.clock),
                int(modes.weather),
                int(modes.temperature),
                int(modes.date),
            ]
        )
        return self.write_command_with_response(Command.SET_BOX_MODE, val)

    def set_light_mode_vj(self, pattern: int) -> ResponsePacket:
        if pattern < 0 or pattern > 15:
            raise ValueError("pattern id out of range")

        val = bytes([BoxMode.SPECIAL.value, pattern])
        return self.write_command_with_response(Command.SET_BOX_MODE, val)
