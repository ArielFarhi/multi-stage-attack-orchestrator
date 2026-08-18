class Device:
    def __init__(self, model: str, ios_version: tuple[int, int], battery_level: int):
        self.model = model
        self.ios_version = ios_version
        self.battery_level = battery_level