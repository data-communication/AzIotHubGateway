from dataclasses import dataclass
from datetime import datetime
from models.measurement import Measurement

@dataclass
class DeviceTelemetry:
    timestamp: datetime
    measurements: list[Measurement]
