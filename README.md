# MQTT to Azure IoT Hub Gateway

The gateway subscribes to configured MQTT topics, buffers valid device telemetry,
and sends the buffered data to Azure IoT Hub at a regular interval.

## Components

- `main.py` loads configuration, creates the MQTT and Azure clients, and runs
  message receiving alongside the periodic send loop.
- `messaging/mqtt_service.py` connects to the MQTT broker, subscribes to the
  configured topics, and passes received payloads to registered handlers.
- `gateway/gateway_service.py` parses incoming telemetry, converts it into
  application models, and formats and sends buffered batches to Azure IoT Hub.
- `gateway/measurement_storage.py` buffers telemetry snapshots by device ID
  until the gateway sends them.
- `models/measurement.py` defines an individual measurement, such as a
  temperature or humidity reading.
- `models/device.py` defines one device telemetry snapshot, containing its
  timestamp and measurements.

## Requirements

- Python 3.11 or newer

## Setup

From the project directory, create and activate a virtual environment, then
install the dependencies:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Create a `.env` file in the project directory:

```dotenv
MQTT_HOST=
MQTT_PORT=
MQTT_TOPICS=
MQTT_USERNAME=
MQTT_PASSWORD=
AZURE_IOT_CONNECTION_STRING=
AZURE_SEND_INTERVAL=
```

`MQTT_TOPICS` accepts multiple topics separated by semicolons as well as wildcards. <br>
Ex. `climate/device001/data;climate/device002/data` <br>
`climate/+/data`

## Run

With the virtual environment active, run:

```powershell
python main.py
```

The gateway connects to the MQTT broker and Azure IoT Hub, then flushes buffered
telemetry every `AZURE_SEND_INTERVAL` seconds (300 seconds by default). Stop it
with `Ctrl+C`.

## MQTT message format

Messages must be JSON with a device ID, a Unix timestamp in seconds, and a list
of measurements:

```json
{
  "deviceId": "E8:F6:0A:C0:4A:24",
  "measurements": [
    { "type": "temperature", "value": 20.2, "unit": "°C" },
    { "type": "humidity", "value": 59, "unit": "%" }
  ],
  "timestamp": "1792855166"
}
```
