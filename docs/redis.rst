Redis
=====

In order to scale we need to send brodcasts to each host so
that they can rebroadcast to each of their clients. This
is done with redis.


.. autoclass:: liteblue.handlers.broadcaster.Broadcaster
    :members:


.. autoclass:: liteblue.handlers.broadcast_mixin.RedisBroadcaster
    :members:
