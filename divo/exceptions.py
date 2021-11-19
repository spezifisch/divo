class PacketException(Exception):
    pass


class PacketParsingError(PacketException):
    pass


class PacketChecksumError(PacketException):
    pass


class PacketWriteException(Exception):
    pass


class NotConnectedException(Exception):
    pass
