import abc


class BluetoothBase(abc.ABC):
    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def flush(self):
        pass

    @abc.abstractmethod
    def get_in_waiting(self) -> int:
        pass

    @abc.abstractmethod
    def write(self, data: bytes) -> int:
        pass

    @abc.abstractmethod
    def read(self, count: int) -> bytes:
        pass
