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
from enum import IntEnum
from typing import Any


class CommandBase(IntEnum):
    pass


class CommandParserBase(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def parse(cmd_type: int, data: bytes) -> Any:
        pass

    @staticmethod
    @abc.abstractmethod
    def parse_response(cmd_type: int, data: bytes) -> Any:
        pass
