import json

from azure.iot.device.aio import IoTHubDeviceClient

from datetime import datetime, timezone
from gateway.measurement_storage import MeasurementStorage
from models.measurement import Measurement
from models.device import DeviceTelemetry

class GatewayService:
    def __init__(self, storage: MeasurementStorage, azure_client: IoTHubDeviceClient):
        self.storage = storage
        self.azure_client = azure_client

    async def handle_message(self, payload):
        try:
            data = json.loads(payload)

            device_id = data["deviceId"]
            if not isinstance(device_id, str) or not device_id.strip():
                raise ValueError("'deviceId' must be a non-empty string")

            timestamp = datetime.fromtimestamp(
                float(data["timestamp"]),
                tz=timezone.utc,
            )

            raw_measurements = data["measurements"]
            if not isinstance(raw_measurements, list):
                raise ValueError("'measurements' must be a list")

            measurements = [
                Measurement(
                    measurement_type=item["type"],
                    value=float(item["value"]),
                    unit=item["unit"],
                )
                for item in raw_measurements
            ]

            telemetry = DeviceTelemetry(
                timestamp=timestamp,
                measurements=measurements,
            )
            self.storage.add_telemetry(device_id, telemetry)

        except (json.JSONDecodeError, KeyError, TypeError, ValueError, OverflowError):
            print("Invalid MQTT telemetry payload")

    async def send_snapshot(self):
        snapshot = self.storage.get_snapshot()
        if not snapshot:
            return

        body = [
            {
                "deviceId": device_id,
                "snapshot": [
                    {
                        "measurements": [
                            {
                                "type": measurement.measurement_type,
                                "value": measurement.value,
                                "unit": measurement.unit,
                            }
                            for measurement in telemetry.measurements
                        ],
                        "timestamp": telemetry.timestamp.isoformat(),
                    }
                    for telemetry in snapshots
                ],
            }
            for device_id, snapshots in snapshot.items()
        ]

        send_status = False
        try:
            await self.azure_client.send_message(json.dumps(body, ensure_ascii=False))
            print(f"Sent: {json.dumps(body, ensure_ascii=False)}")
            send_status = True
        except Exception as ex:
            print(f"Failed to send message: {ex}")
            send_status = False

        if(send_status):
            self.storage.new_snapshot()
        
