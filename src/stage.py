import random

class Stage:
    def __init__(self, name: str, success_probability: float):
        if not 0 <= success_probability <= 1:
            raise ValueError("success probability must be between 0 and 1")

        self.name = name
        self.success_probability = success_probability

    def run(self, device_client=None) -> bool:
        if device_client is not None:
            return device_client.run_stage(self.name)

        return random.random() < self.success_probability
