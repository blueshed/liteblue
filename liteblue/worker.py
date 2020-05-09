"""
    Worker listens to a queue in redis and performs work
"""
import asyncio
import logging
import uuid
from importlib import import_module
from concurrent.futures import ThreadPoolExecutor
import aioredis
import tornado.ioloop
import tornado.log
from . import config
from . import handlers
from .handlers import json_utils

LOGGER = logging.getLogger(__name__)


class RemoteException(Exception):
    """ We cannot serialise Exceptions so this is the message """


class Worker:
    """ A context rpc fed by redis """

    def __init__(self, cfg: config.Config, loop=None):
        """ setup variables before run """
        self.loop = loop if loop else tornado.ioloop.IOLoop.current()
        self.loop.set_default_executor(ThreadPoolExecutor(max_workers=cfg.max_workers))
        self.procedures = import_module(cfg.procedures)
        self.redis_url = cfg.redis_url
        self.redis_topic = cfg.redis_topic
        self.redis = None
        handlers.context.LOOP = self.loop
        handlers.BroadcastMixin._loop_ = self.loop
        handlers.BroadcastMixin._broadcaster_ = self
        self.loop.call_later(0, self.subscribe, cfg.redis_queue)

    async def shutdown(self):
        """ shut down outstatnding tasks """
        handlers.BroadcastMixin._broadcaster_ = None  # pylint: disable=W0212
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()

    async def subscribe(self, work_queue: str):
        """ run forever coroutine that listens to topic and broadcasts """
        subscription = await aioredis.create_redis(self.redis_url)
        try:
            while True:
                document = await subscription.blpop(work_queue, encoding="utf-8")
                LOGGER.info("got document: %s", document)
                self.loop.call_later(0, self.handle_work, document)
        except asyncio.CancelledError:
            pass

    async def unsubscribe(self):
        """ interface """

    async def send(self, data, user_ids):
        """ sends to redis topic """
        if self.redis is None:
            self.redis = await aioredis.create_redis_pool(self.redis_url)
        document = json_utils.dumps([data, user_ids])
        LOGGER.info("published broadcast %s -> %r", self.redis_topic, document)
        await self.redis.publish(self.redis_topic, document)

    async def handle_work(self, val: str = None):
        """ unpack the mesage and call perform """
        if self.redis is None:
            self.redis = await aioredis.create_redis_pool(self.redis_url)
        LOGGER.info("got work %s", val)
        if val is None:
            return
        content = json_utils.loads(val[1])
        try:
            proc = getattr(self.procedures, content["proc"])
            result = await handlers.context.perform(
                content["user"], proc, *content["args"], **content["kwargs"]
            )
            content["result"] = result
        except asyncio.CancelledError:
            LOGGER.info("cancelled")
            return
        except Exception as ex:  # pylint: disable=W0703
            content["error"] = {"code": -32000, "message": str(ex)}
        if content.get("reply"):
            document = json_utils.dumps(content)
            await self.redis.publish(content["reply"], document)
            LOGGER.info("published reply %s -> %r", content["reply"], document)


class Channel:
    """ sends work to redis and handles reply """

    def __init__(self, url, queue, loop=None):
        self.loop = loop if loop else tornado.ioloop.IOLoop.current()
        self._futures_ = {}
        self.redis_url = url
        self.redis_queue = queue
        self.reply_queue = f"channel:{uuid.uuid4()}"
        self.reply_task = self.loop.call_later(0, self.reply_subscribe)
        LOGGER.info("redis reply %s", self.reply_queue)
        self.redis = None

    async def tidy_up(self):
        """ a nasty little method to clean up an io_loop for testing """
        self.reply_task.cancel()
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()

    async def perform(self, user, proc, *args, **kwargs):
        """ send proc to redis """
        if self.redis is None:
            self.redis = await aioredis.create_redis_pool(self.redis_url)
        future_id = str(uuid.uuid4())
        future = asyncio.Future()
        self._futures_[future_id] = future
        document = handlers.json_utils.dumps(
            {
                "user": user,
                "proc": proc,
                "args": args,
                "kwargs": kwargs,
                "future_id": future_id,
                "reply": self.reply_queue,
            }
        )

        await self.redis.rpush(self.redis_queue, document)
        LOGGER.debug("published work %s -> %r", self.redis_queue, document)
        return await future

    async def reply_subscribe(self):
        """ run forever wait work from redis for Application """
        subscription = await aioredis.create_redis(self.redis_url)
        response = await subscription.subscribe(self.reply_queue)
        channel = response[0]
        LOGGER.info("subscribed to: %s", self.reply_queue)
        try:
            while await channel.wait_message():
                document = await channel.get(encoding="utf-8")
                LOGGER.info("got document: %s", document)
                result = handlers.json_utils.loads(document)
                future = self._futures_.get(result.get("future_id"), None)
                if future:
                    if "error" in result:
                        future.set_exception(RemoteException(result.get("error")))
                    else:
                        future.set_result(result.get("result"))
        except asyncio.CancelledError:
            pass


def main(cfg):
    """ Creates Worker and starts tornado """
    tornado.log.enable_pretty_logging()
    loop = tornado.ioloop.IOLoop.current()
    worker = Worker(cfg, loop)
    try:
        LOGGER.info("listening for work")
        loop.start()
    except KeyboardInterrupt:
        LOGGER.info("shutdown")
        loop.run_until_complete(worker.shutdown())
        loop.close()
