class Device:
    def __init__(
        self,
        model: str,
        ios_version: tuple[int, int],
        battery_level: int,
    ):
        if not model:
            raise ValueError("model must not be empty")

        if (
            len(ios_version) != 2
            or not all(isinstance(part, int) and part >= 0 for part in ios_version)
        ):
            raise ValueError("ios_version must contain two non-negative integers")

        if not 0 <= battery_level <= 100:
            raise ValueError("battery_level must be between 0 and 100")

        self.model = model
        self.ios_version = ios_version
        self.battery_level = battery_level
