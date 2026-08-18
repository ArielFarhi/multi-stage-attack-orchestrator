class AttackOrchestrator:
    def __init__(self, selector):
        self.selector = selector

    def run(self, device):
        attacks = self.selector.rank_attacks(device)

        for attack in attacks:
            if attack.run():
                return attack

        return None