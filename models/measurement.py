from dataclasses import dataclass

@dataclass
class Measurement:
    measurement_type: str
    value: float
    unit: str

