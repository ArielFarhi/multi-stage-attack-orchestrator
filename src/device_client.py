from abc import ABC, abstractmethod

class DeviceClient(ABC):

    @abstractmethod
    def run_stage(self, stage_name: str) -> bool:
        pass

    @abstractmethod
    def read_file(self, path: str) -> bytes:
        pass

    @abstractmethod
    def list_files(self) -> list[str]:
        pass
