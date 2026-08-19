class Device:
    def __init__(
        self,
        model: str,
        ios_version: tuple[int, int],
        battery_level: int,
    ):
        if not model:
            raise ValueError("model must not be empty")

        if len(ios_version) != 2:
            raise ValueError("ios_version must contain two non-negative integers")

        major, minor = ios_version

        if major < 0 or minor < 0:
            raise ValueError("ios_version must contain two non-negative integers")

        if not 0 <= battery_level <= 100:
            raise ValueError("battery_level must be between 0 and 100")

        self.model = model
        self.ios_version = ios_version
        self.battery_level = battery_level
