from models.device import DeviceTelemetry

class MeasurementStorage:
    def __init__(self):
        self.__snapshots: dict[str, list[DeviceTelemetry]] = {}

    def add_telemetry(self, device_id: str, snapshot: DeviceTelemetry):
        if not device_id:
            raise ValueError("device_id must not be empty")

        self.__snapshots.setdefault(device_id, []).append(snapshot)

    def get_snapshot(self):
        return self.__snapshots        

    def new_snapshot(self):
        self.__snapshots = {}
