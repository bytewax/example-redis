import os

import redis
import bytewax.operators as op
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow
from bytewax.inputs import FixedPartitionedSource, StatefulSourcePartition


class RedisPubSubPartition(StatefulSourcePartition):
    def __init__(self, redis_host, redis_port, redis_pass, channel):
        if not redis_pass:
            r = redis.Redis(host=redis_host, port=redis_port)
        else: 
            r = redis.Redis(host=redis_host, port=redis_port, password=redis_pass)
        self.pubsub = r.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe(channel)

    def next_batch(self, _sched):
        message = self.pubsub.get_message()
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


class RedisPubSubSource(FixedPartitionedSource):
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', '6379'))
        self.redis_pass = os.getenv('REDIS_PASS', None)
        self.channel_name = os.getenv('REDIS_CHANNEL_NAME', 'device_events')

    def list_parts(self):
        return ['single-part']

    def build_part(self, now, for_key, resume_state):
        return RedisPubSubPartition(
            self.redis_host,
            self.redis_port,
            self.redis_pass,
            self.channel_name,
        )


flow = Dataflow("redis-echo")

input = op.input('inp', flow, RedisPubSubSource())
op.output('out', input, StdOutSink())
