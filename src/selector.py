from src.attack import Attack
from src.device import Device


class AttackSelector:
    def __init__(self, attacks: list[Attack]):
        self.attacks = attacks

    def get_compatible_attacks(self, device: Device) -> list[Attack]:
        compatible_attacks = []

        for attack in self.attacks:
            if attack.is_compatible(device):
                compatible_attacks.append(attack)

        return compatible_attacks

    def rank_attacks(self, device: Device) -> list[Attack]:
        attacks = self.get_compatible_attacks(device)

        return sorted(
            attacks,
            key=lambda attack: attack.success_probability(),
            reverse=True,
        )

    def select(self, device: Device) -> Attack | None:
        ranked = self.rank_attacks(device)

        if not ranked:
            return None

        return ranked[0]
