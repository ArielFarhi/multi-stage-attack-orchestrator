from src.device import Device
from src.device_client import DeviceClient
from src.extractor import Extractor
from src.attack import Attack
from src.selector import AttackSelector


class AttackOrchestrator:
    def __init__(self, selector: AttackSelector):
        self.selector = selector

    def run(
        self,
        device: Device,
        device_client: DeviceClient | None = None,
    ) -> Attack | None:
        attacks = self.selector.rank_attacks(device)

        for attack in attacks:
            succeeded = (
                attack.run()
                if device_client is None
                else attack.run(device_client)
            )

            if succeeded:
                return attack

        return None

    def run_connected(self, device_client: DeviceClient) -> Attack | None:
        device = device_client.get_device()
        return self.run(device, device_client)

    def run_and_extract(
        self,
        device_client: DeviceClient,
    ) -> dict[str, bytes] | None:
        successful_attack = self.run_connected(device_client)

        if successful_attack is None:
            return None

        return Extractor(device_client).extract_all()
