from src.device_client import DeviceClient


class Extractor:
    def __init__(self, device_client: DeviceClient):
        self.device_client = device_client

    def extract_file(self, path: str) -> bytes:
        return self.device_client.read_file(path)

    def extract_all(self) -> dict[str, bytes]:
        files = {}

        for path in self.device_client.list_files():
            files[path] = self.device_client.read_file(path)

        return files
