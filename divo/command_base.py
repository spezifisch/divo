import abc
from enum import IntEnum
from typing import Optional, Any


class CommandBase(IntEnum):
    pass


class CommandParserBase(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def parse(cmd_type: int, data: Optional[bytes]) -> Any:
        pass

    @staticmethod
    @abc.abstractmethod
    def parse_response(cmd_type: int, data: Optional[bytes]) -> Any:
        pass
