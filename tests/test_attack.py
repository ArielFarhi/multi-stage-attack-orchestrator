from src.attack import Attack
from src.device import Device
from src.stage import Stage
import pytest

def test_attack_is_compatible():
    device = Device("iPhone17", (17, 2), 80)

    attack = Attack(
        name="attack_a",
        stages=[Stage("s1", 0.9)],
        supported_models=["iPhone17"],
        min_ios=(17, 0),
        max_ios=(17, 5),
        min_battery=30,
    )

    assert attack.is_compatible(device)
    
def test_success_probability():
    attack = Attack(
        name="attack_a",
        stages=[
            Stage("s1", 0.9),
            Stage("s2", 0.8),
        ],
        supported_models=["iPhone17"],
        min_ios=(17, 0),
        max_ios=(17, 5),
    )

    assert attack.success_probability() == pytest.approx(0.72)


@pytest.mark.parametrize(
    "device",
    [
        Device("unsupported", (17, 2), 80),
        Device("iPhone17", (16, 9), 80),
        Device("iPhone17", (17, 6), 80),
        Device("iPhone17", (17, 2), 10),
    ],
)
def test_attack_rejects_incompatible_device_state(device):
    attack = Attack(
        "attack_a",
        [Stage("s1", 1.0)],
        ["iPhone17"],
        (17, 0),
        (17, 5),
        min_battery=30,
    )

    assert attack.is_compatible(device) is False


def test_attack_stops_after_first_failed_stage():
    first_stage = Stage("first", 0.0)
    second_stage = Stage("second", 1.0)
    second_stage.run = pytest.fail
    attack = Attack("attack", [first_stage, second_stage], ["model"], (0, 0), (0, 0))

    assert attack.run() is False


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": ""},
        {"stages": []},
        {"supported_models": []},
        {"min_ios": (18, 0), "max_ios": (17, 0)},
        {"min_battery": 101},
    ],
)
def test_attack_rejects_invalid_configuration(kwargs):
    configuration = {
        "name": "attack",
        "stages": [Stage("stage", 1.0)],
        "supported_models": ["model"],
        "min_ios": (17, 0),
        "max_ios": (18, 0),
    }
    configuration.update(kwargs)

    with pytest.raises(ValueError):
        Attack(**configuration)
