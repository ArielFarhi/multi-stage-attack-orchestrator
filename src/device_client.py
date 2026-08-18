from abc import ABC, abstractmethod

from src.device import Device


class DeviceClient(ABC):

    @abstractmethod
    def get_device(self) -> Device:
        pass

    @abstractmethod
    def begin_attack(self, stage_count: int) -> None:
        pass

    @abstractmethod
    def run_stage(self, stage_name: str) -> bool:
        pass

    @abstractmethod
    def read_file(self, path: str) -> bytes:
        pass

    @abstractmethod
    def list_files(self) -> list[str]:
        pass
