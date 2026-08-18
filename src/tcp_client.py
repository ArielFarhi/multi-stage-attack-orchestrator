import json
import socket

from src.device_client import DeviceClient
from src.device import Device


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
        self.socket: socket.socket | None = None

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

    def get_device(self) -> Device:
        response = self.get_device_info()

        if response.get("status") != "ok":
            raise ConnectionError("Could not read device information")

        try:
            major, minor = response["ios"].split(".", maxsplit=1)
            return Device(
                model=response["model"],
                ios_version=(int(major), int(minor)),
                battery_level=response["battery"],
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ConnectionError("Invalid device information") from error

    def begin_attack(self, stage_count: int) -> None:
        response = self.send_request({
            "command": "begin_attack",
            "stage_count": stage_count,
        })

        if response.get("status") != "ok":
            raise RuntimeError(response.get("message", "Could not begin attack"))
    def run_stage(self, stage_name: str) -> bool:
        response = self.send_request({
            "command": "run_stage",
            "stage": stage_name,
        })

        if response.get("status") != "ok":
            raise RuntimeError(response.get("message", "Stage execution failed"))

        return response.get("result") == "success"

    def list_files(self) -> list[str]:
        response = self.send_request({
            "command": "list_files"
        })

        if response.get("status") != "ok":
            raise PermissionError(response.get("message", "Access denied"))

        return response.get("files", [])

    def read_file(self, path: str) -> bytes:
        response = self.send_request({
            "command": "read_file",
            "path": path,
        })

        if response.get("status") != "ok":
            if response.get("message") == "Access denied":
                raise PermissionError(path)

            raise FileNotFoundError(path)

        return response["data"].encode()
