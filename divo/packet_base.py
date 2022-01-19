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

import abc
from typing import Any, Optional, Union

from .command_base import CommandBase, CommandParserBase
from .exceptions import PacketException


class PacketBase(abc.ABC):
    START_OF_PACKET = 1
    END_OF_PACKET = 2

    @classmethod
    @abc.abstractmethod
    def build(cls, cmd: CommandBase, payload: Optional[Union[bytes, int]] = None) -> bytes:
        pass

    @classmethod
    @abc.abstractmethod
    def parse(cls, parser: CommandParserBase, packet: bytes) -> Any:
        pass

    @classmethod
    def is_valid(cls, parser: CommandParserBase, packet: bytes) -> bool:
        try:
            cls.parse(parser, packet)
        except PacketException:
            return False
        return True
