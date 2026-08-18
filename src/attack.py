from src.stage import Stage
from src.device import Device

class Attack:
    def __init__(self, name: str, 
                 stages: list[Stage], 
                 supported_models: list[str], 
                 min_ios: tuple[int, int], 
                 max_ios: tuple[int, int], 
                 min_battery: int = 20):
        self.name = name
        self.stages = stages
        self.supported_models = supported_models
        self.min_ios = min_ios
        self.max_ios = max_ios
        self.min_battery = min_battery
    
    def is_compatible(self, device: Device) -> bool:
        if device.model not in self.supported_models:
            return False

        if device.ios_version < self.min_ios or device.ios_version > self.max_ios:
            return False

        if device.battery_level < self.min_battery:
            return False

        return True
    
    def success_probability(self) -> float:
        probability = 1.0

        for stage in self.stages:
            probability *= stage.success_probability

        return probability
    
    def run(self) -> bool:
        for stage in self.stages:
            if not stage.run():
                return False

        return True