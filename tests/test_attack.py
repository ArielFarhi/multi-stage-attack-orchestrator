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