from src.device import Device
from src.device_client import DeviceClient
from src.stage import Stage


class Attack:
    def __init__(
        self,
        name: str,
        stages: list[Stage],
        supported_models: list[str],
        min_ios: tuple[int, int],
        max_ios: tuple[int, int],
        min_battery: int = 20,
    ):
        if not name:
            raise ValueError("attack name must not be empty")
        if not stages:
            raise ValueError("attack must contain at least one stage")
        if not supported_models:
            raise ValueError("supported_models must not be empty")
        if min_ios > max_ios:
            raise ValueError("min_ios must not be greater than max_ios")
        if not 0 <= min_battery <= 100:
            raise ValueError("min_battery must be between 0 and 100")

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

    def run(self, device_client: DeviceClient | None = None) -> bool:
        if device_client is not None:
            device_client.begin_attack(len(self.stages))

        for stage in self.stages:
            succeeded = (
                stage.run()
                if device_client is None
                else device_client.run_stage(stage.name)
            )

            if not succeeded:
                return False

        return True
