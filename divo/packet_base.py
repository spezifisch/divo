import abc
from typing import Optional, Union, Any

from command_base import CommandBase, CommandParserBase
from exceptions import PacketException


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
