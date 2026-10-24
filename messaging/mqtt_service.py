import asyncio
from collections.abc import Awaitable, Callable

from asyncio_mqtt import Client, MqttError

def mqtt_topic_matches(filter: str, topic: str) -> bool:
    filter_levels = filter.split("/")
    topic_levels = topic.split("/")

    for f, t in zip(filter_levels, topic_levels):
        if f == "#":
            return True
        if f == "+":
            continue
        if f != t:
            return False

    return len(filter_levels) == len(topic_levels)


class MqttService:
    def __init__(self, host="localhost", port=1883, username=None, password=None, identifier=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.identifier = identifier

        self._handlers: dict[str, list[Callable[[str], Awaitable[None]]]] = {}
        self._topics: asyncio.Queue[str] = asyncio.Queue()

    def register(self, topic: str, handler: Callable[[str], Awaitable[None]]):
        if topic not in self._handlers:
            self._handlers[topic] = []
            self._topics.put_nowait(topic)

        self._handlers[topic].append(handler)

    async def _subscribe(self, client: Client):
        while True:
            topic = await self._topics.get()
            print("Subscribing to:", topic)
            await client.subscribe(topic)

    async def _receive(self, client):
        async with client.messages() as messages:
            # Subscribe to all registered topics
            for topic in self._handlers.keys():
                await client.subscribe(topic)

            async for message in messages:
                topic = str(message.topic)
                payload = message.payload.decode("utf-8")

                for registered_topic, handlers in self._handlers.items():
                    if mqtt_topic_matches(registered_topic, topic):
                        for handler in handlers:
                            await handler(payload)

    async def run(self):
        try:
            async with Client(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                client_id=self.identifier,
            ) as client:

                async with asyncio.TaskGroup() as tasks:
                    tasks.create_task(self._subscribe(client))
                    tasks.create_task(self._receive(client))

        except MqttError as e:
            print(f"MQTT error: {e}")
