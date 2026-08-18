import socket
import subprocess

import pytest

from src.tcp_client import TCPDeviceClient
from src.attack import Attack
from src.device import Device
from src.orchestrator import AttackOrchestrator
from src.selector import AttackSelector
from src.stage import Stage


SIMULATOR_SOURCE = "simulator/device_simulator.c"
SIMULATOR_BINARY = "simulator/device_simulator"


@pytest.fixture(scope="module")
def simulator():
    with socket.socket() as port_socket:
        port_socket.bind(("127.0.0.1", 0))
        port = port_socket.getsockname()[1]

    subprocess.run(
        [
            "gcc",
            SIMULATOR_SOURCE,
            "-o",
            SIMULATOR_BINARY,
        ],
        check=True,
    )

    process = subprocess.Popen(
        [SIMULATOR_BINARY, str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    startup_message = process.stdout.readline()

    if f"listening on port {port}" not in startup_message:
        stderr = process.stderr.read()
        process.wait()
        pytest.fail(
            f"Simulator failed to start: {stderr.strip()}"
        )

    yield port

    process.terminate()
    process.wait()


@pytest.fixture
def client(simulator):
    device_client = TCPDeviceClient(port=simulator)
    device_client.connect()

    yield device_client

    device_client.disconnect()


def test_get_device_info(client):
    response = client.get_device_info()

    assert response["status"] == "ok"
    assert response["model"] == "iPhone14"
    assert response["ios"] == "17.2"
    assert response["battery"] == 80


def test_run_stage(client):
    result = client.run_stage("stage_1")

    assert result is True


def test_list_files(client):
    files = client.list_files()

    assert "/data/contacts.txt" in files
    assert "/data/notes.txt" in files


def test_read_file(client):
    data = client.read_file("/data/contacts.txt")

    assert data == b"Alice,123456"


def test_read_missing_file(client):
    with pytest.raises(FileNotFoundError):
        client.read_file("/data/missing.txt")


def test_orchestrator_runs_attack_and_extracts_all_files(client):
    device = Device("iPhone14", (17, 2), 80)
    attack = Attack(
        name="tcp_attack",
        stages=[Stage("stage_1", 0.9), Stage("stage_2", 0.8)],
        supported_models=["iPhone14"],
        min_ios=(17, 0),
        max_ios=(17, 5),
    )
    orchestrator = AttackOrchestrator(AttackSelector([attack]))

    files = orchestrator.run_and_extract(device, client)

    assert files == {
        "/data/contacts.txt": b"Alice,123456",
        "/data/notes.txt": b"Example note",
    }


def test_orchestrator_tries_next_attack_after_stage_failure(client):
    device = Device("iPhone14", (17, 2), 80)
    failing_attack = Attack(
        "failing",
        [Stage("fail_stage", 1.0)],
        ["iPhone14"],
        (17, 0),
        (17, 5),
    )
    successful_attack = Attack(
        "successful",
        [Stage("stage_1", 0.5)],
        ["iPhone14"],
        (17, 0),
        (17, 5),
    )
    orchestrator = AttackOrchestrator(
        AttackSelector([failing_attack, successful_attack])
    )

    selected_attack = orchestrator.run(device, client)

    assert selected_attack is successful_attack


def test_connection_drops_during_stage(client):
    with pytest.raises(ConnectionError):
        client.run_stage("drop_connection")


def test_connection_drop(client):
    client.send_request({
        "command": "disconnect"
    })

    with pytest.raises(ConnectionError):
        client.send_request({
            "command": "get_info"
        })
