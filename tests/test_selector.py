import pytest

from src.attack import Attack
from src.device import Device
from src.selector import AttackSelector
from src.stage import Stage

def test_selector_picks_attack_with_highest_success_probability():
    device = Device(
        model="iPhone14",
        ios_version=(17, 2),
        battery_level=80,
    )

    attack_a = Attack(
        name="attack_a",
        stages=[
            Stage("a_stage_1", 0.9),
            Stage("a_stage_2", 0.8),
        ],
        supported_models=["iPhone14"],
        min_ios=(17, 0),
        max_ios=(17, 5),
        min_battery=30,
    )

    attack_b = Attack(
        name="attack_b",
        stages=[
            Stage("b_stage_1", 0.9),
            Stage("b_stage_2", 0.9),
        ],
        supported_models=["iPhone14"],
        min_ios=(17, 0),
        max_ios=(17, 5),
        min_battery=30,
    )

    selector = AttackSelector([attack_a, attack_b])

    selected_attack = selector.select(device)

    assert selected_attack == attack_b


def test_selector_ignores_incompatible_attacks():
    device = Device(
        model="iPhone14",
        ios_version=(17, 2),
        battery_level=80,
    )

    compatible_attack = Attack(
        name="compatible_attack",
        stages=[
            Stage("stage_1", 0.8),
        ],
        supported_models=["iPhone14"],
        min_ios=(17, 0),
        max_ios=(17, 5),
        min_battery=30,
    )

    incompatible_attack = Attack(
        name="incompatible_attack",
        stages=[
            Stage("stage_1", 1.0),
        ],
        supported_models=["iPhone15"],
        min_ios=(17, 0),
        max_ios=(18, 0),
        min_battery=30,
    )

    selector = AttackSelector(
        [compatible_attack, incompatible_attack]
    )

    selected_attack = selector.select(device)

    assert selected_attack == compatible_attack


def test_selector_returns_none_when_no_attack_is_compatible():
    device = Device(
        model="iPhone14",
        ios_version=(17, 2),
        battery_level=80,
    )

    attack = Attack(
        name="attack_a",
        stages=[
            Stage("stage_1", 0.9),
        ],
        supported_models=["iPhone15"],
        min_ios=(18, 0),
        max_ios=(18, 5),
        min_battery=30,
    )

    selector = AttackSelector([attack])

    selected_attack = selector.select(device)

    assert selected_attack is None


def test_rank_attacks_orders_by_success_probability():
    device = Device(
        model="iPhone14",
        ios_version=(17, 2),
        battery_level=80,
    )

    attack_low = Attack(
        name="attack_low",
        stages=[
            Stage("stage_1", 0.5),
        ],
        supported_models=["iPhone14"],
        min_ios=(17, 0),
        max_ios=(17, 5),
        min_battery=30,
    )

    attack_high = Attack(
        name="attack_high",
        stages=[
            Stage("stage_1", 0.9),
        ],
        supported_models=["iPhone14"],
        min_ios=(17, 0),
        max_ios=(17, 5),
        min_battery=30,
    )

    selector = AttackSelector([attack_low, attack_high])

    ranked_attacks = selector.rank_attacks(device)

    assert ranked_attacks == [attack_high, attack_low]