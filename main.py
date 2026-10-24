import asyncio
import os
import sys

from azure.iot.device.aio import IoTHubDeviceClient

from dotenv import load_dotenv

from gateway.gateway_service import GatewayService
from gateway.measurement_storage import MeasurementStorage
from messaging.mqtt_service import MqttService


async def main() -> None:
    load_dotenv()

    mqtt_service = MqttService(
        host=os.getenv("MQTT_HOST", "localhost"),
        port=int(os.getenv("MQTT_PORT", "1883")),
        username=os.getenv("MQTT_USERNAME"),
        password=os.getenv("MQTT_PASSWORD"),
        identifier="Azure-IoT-Hub-Gateway",
    )

    storage = MeasurementStorage()
    
    azure_client = IoTHubDeviceClient.create_from_connection_string(
        os.getenv("AZURE_IOT_CONNECTION_STRING")
    )

    gateway = GatewayService(storage=storage, azure_client=azure_client)

    topics = [
        topic.strip()
        for topic in os.getenv("MQTT_TOPICS").split(";")
        if topic.strip()
    ]

    for topic in topics:
        mqtt_service.register(topic, gateway.handle_message)

    interval = float(os.getenv("AZURE_SEND_INTERVAL", "300"))
   
    await azure_client.connect()

    async def flush_periodically() -> None:
        while True:
            await asyncio.sleep(interval)
            await gateway.send_snapshot()

    try:
        async with asyncio.TaskGroup() as tasks:
            tasks.create_task(mqtt_service.run())
            tasks.create_task(flush_periodically())
    except asyncio.CancelledError:
        print("Shutting down.")
    finally:
        await azure_client.disconnect()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.run(main(), loop_factory=asyncio.SelectorEventLoop)
    else:
        asyncio.run(main())