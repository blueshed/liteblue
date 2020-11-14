# pylint: disable=W0201
"""
    Broadcast function  without Websockets
"""
import asyncio
import logging
import time
import inspect
import tornado.iostream
from tornado import ioloop
from tornado.queues import Queue
from tornado import gen
from .broadcaster import Broadcaster
from . import json_utils

LOGGER = logging.getLogger(__name__)


class RedisBroadcaster(Broadcaster):
    """ simple re-broadcaster """

    def broadcast(self, document):
        """ sends to _clients_ """
        data, user_ids = json_utils.loads(document)
        BroadcastMixin.send(data, user_ids)

    async def send(self, data, user_ids):
        """ sends to redis """
        document = json_utils.dumps([data, user_ids])
        await self.publish(document)


class BroadcastMixin:
    """
    Queue of messages to send to client
    """

    _clients_ = []
    _broadcaster_ = None
    _cron_ = None
    _loop_ = None

    def init_broadcast(self):
        """
        Set up response headers and prepare
        local queue and add self to clients
        """
        self.broadcasting = True
        self.queue = Queue()
        self._clients_.append(self)
        self._task_ = self._loop_.call_later(0, self.do_broadcast)

    async def do_broadcast(self):
        """ this waits on the queue and write_message each data """
        try:
            while self.broadcasting:
                try:
                    delta = time.time() + 0.1
                    data = await self.queue.get(timeout=delta)
                    if inspect.iscoroutinefunction(self.write_message):
                        await self.write_message(data)
                    else:
                        self.write_message(data)
                except gen.TimeoutError:
                    continue
        except asyncio.CancelledError:
            pass
        except tornado.iostream.StreamClosedError:
            pass
        self._task_ = None
        self.end_broadcast()

    def end_broadcast(self):
        """ remove self from clients """
        self.broadcasting = False
        if self in self._clients_:
            self._clients_.remove(self)

    @classmethod
    def broadcast(cls, data, user_ids=None):
        """ thread safe """
        if cls._loop_:
            if cls._broadcaster_:
                cls._loop_.call_later(0, cls._broadcaster_.send, data, user_ids)
            else:
                cls._loop_.call_later(0, cls.send, data, user_ids)

    @classmethod
    def keep_alive(cls):
        """ pings all connected clients """
        logging.debug("keep alive")
        msg = str(time.time())
        for client in cls._clients_:
            client.ping(msg)

    @classmethod
    def send(cls, data, user_ids):
        """ does the actual sending to all _clients_ """
        message = json_utils.dumps(data)
        LOGGER.debug("sending: %s", message)
        for client in cls._clients_:
            if user_ids is None or client.current_user["id"] in user_ids:
                client.queue.put_nowait(message)

    @classmethod
    def init_broadcasts(cls, io_loop, topic_name, redis_url):
        """ set up keep alive and re-broadcaster """
        cls._loop_ = io_loop
        cls._cron_ = ioloop.PeriodicCallback(cls.keep_alive, 30000)
        cls._cron_.start()

        if redis_url:
            cls._broadcaster_ = RedisBroadcaster(topic_name, redis_url)
            cls._loop_.call_later(0, cls._broadcaster_.subscribe)
            LOGGER.info("redis broadcast")
        else:
            cls._broadcaster_ = None
            LOGGER.info("local broadcast")

    @classmethod
    async def tidy_up(cls):
        """ clean up keep alive, broadcaster and client tasks """
        if cls._cron_:
            cls._cron_.stop()
        if cls._broadcaster_:
            await cls._broadcaster_.unsubscribe()
        tasks = [b._task_ for b in cls._clients_ if b._task_]  # pylint: disable=W0212
        for task in tasks:
            task.cancel()
        await asyncio.sleep(0.11)
