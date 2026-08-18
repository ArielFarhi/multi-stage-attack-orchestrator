import json
import socket

from src.device_client import DeviceClient


class TCPDeviceClient(DeviceClient):
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 9000,
        timeout: float = 2.0,
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None

    def connect(self) -> None:
        self.socket = socket.create_connection(
            (self.host, self.port),
            timeout=self.timeout,
        )

    def disconnect(self) -> None:
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def send_request(self, request: dict) -> dict:
        if self.socket is None:
            raise ConnectionError("Not connected to device")

        message = json.dumps(request) + "\n"

        try:
            self.socket.sendall(message.encode())

            response = self._receive_line()

            return json.loads(response)

        except (OSError, json.JSONDecodeError) as error:
            self.disconnect()
            raise ConnectionError("Communication with device failed") from error

    def _receive_line(self) -> str:
        data = b""

        while not data.endswith(b"\n"):
            chunk = self.socket.recv(1024)

            if not chunk:
                raise ConnectionError("Device disconnected")

            data += chunk
        return data.decode().strip()
    
    def get_device_info(self) -> dict:
        return self.send_request({
            "command": "get_info"
        })


    def run_stage(self, stage_name: str) -> bool:
        response = self.send_request({
            "command": "run_stage",
            "stage": stage_name,
        })

        return response.get("result") == "success"


    def list_files(self) -> list[str]:
        response = self.send_request({
            "command": "list_files"
        })

        return response.get("files", [])


    def read_file(self, path: str) -> bytes:
        response = self.send_request({
            "command": "read_file",
            "path": path,
        })

        if response.get("status") != "ok":
            raise FileNotFoundError(path)

        return response["data"].encode()
