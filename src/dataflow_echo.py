import os

import redis
from bytewax import operators as op
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow
from bytewax.inputs import FixedPartitionedSource, StatefulSourcePartition


class RedisPubSubPartition(StatefulSourcePartition[str, None]):
    def __init__(self, redis_host, redis_port, channel):
        r = redis.Redis(host=redis_host, port=redis_port)
        # self.pubsub = r.pubsub()
        # ignore subscribe messages to get rid of spammy 1
        self.pubsub = r.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe(channel)
        self.channel = channel

    def next_batch(self, _sched):
        message = self.pubsub.get_message()
        # would not need this if ignoring subscribe, but just in case
        if message is None:
            return []
        data = message['data']
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        return [data]

    def snapshot(self):
        return None

    def close(self):
        self.pubsub.close()


class RedisPubSubSource(FixedPartitionedSource[str, None]):
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = os.getenv('REDIS_PORT', '6379')
        self.channel_name = os.getenv('REDIS_CHANNEL_NAME', 'device_events')

    def list_parts(self):
        return ['single-part']

    def build_part(self, now, for_key, resume_state):
        assert for_key == 'single-part'
        assert resume_state is None
        return RedisPubSubPartition(
            self.redis_host,
            self.redis_port,
            self.channel_name,
        )


flow = Dataflow('redis_echo')

stream = op.input('inp', flow, RedisPubSubSource())
op.output('out', stream, StdOutSink())
