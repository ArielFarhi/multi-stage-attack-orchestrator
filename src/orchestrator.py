from src.device import Device
from src.device_client import DeviceClient
from src.extractor import Extractor


class AttackOrchestrator:
    def __init__(self, selector):
        self.selector = selector

    def run(
        self,
        device: Device,
        device_client: DeviceClient | None = None,
    ):
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

    def run_and_extract(
        self,
        device: Device,
        device_client: DeviceClient,
    ) -> dict[str, bytes] | None:
        successful_attack = self.run(device, device_client)

        if successful_attack is None:
            return None

        return Extractor(device_client).extract_all()
