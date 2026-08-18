import pytest

from src.device import Device


@pytest.mark.parametrize(
    "model, ios_version, battery_level",
    [
        ("", (17, 0), 50),
        ("model", (-1, 0), 50),
        ("model", (17,), 50),
        ("model", (17, 0), -1),
        ("model", (17, 0), 101),
    ],
)
def test_device_rejects_invalid_state(model, ios_version, battery_level):
    with pytest.raises(ValueError):
        Device(model, ios_version, battery_level)
