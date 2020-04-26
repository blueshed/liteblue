""" Redis publish and subscribe in one class """
import logging
import aioredis

LOGGER = logging.getLogger(__name__)


class Broadcaster:
    """ both publish and subscribe to same topic """

    def __init__(self, topic_name: str, redis_url: str):
        self.topic_name = topic_name
        self.redis_url = redis_url
        self.subscription = None

    def broadcast(self, document):
        """ sub class responsibility """

    async def publish(self, document):
        """ publishes a document to topic """
        redis = await aioredis.create_redis_pool(self.redis_url)
        await redis.execute("publish", self.topic_name, document)
        LOGGER.debug("published %s -> %r", self.topic_name, document)
        redis.close()
        await redis.wait_closed()

    async def subscribe(self):
        """ run forever coroutine that listens to topic and broadcasts """
        self.subscription = await aioredis.create_redis(self.redis_url)
        response = await self.subscription.subscribe(self.topic_name)
        channel = response[0]
        LOGGER.info("subscribed to: %s", self.topic_name)
        try:
            while await channel.wait_message():
                document = await channel.get(encoding="utf-8")
                LOGGER.debug("got document: %s", document)
                self.broadcast(document)
        finally:
            self.subscription.close()

    async def unsubscribe(self):
        """ close subscription client """
        if self.subscription:
            self.subscription.close()
            await self.subscription.wait_closed()
