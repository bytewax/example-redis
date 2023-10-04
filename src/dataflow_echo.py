import os

import redis
from bytewax.connectors.stdio import StdOutput
from bytewax.dataflow import Dataflow
from bytewax.inputs import PartitionedInput, StatefulSource


class RedisPubSubSource(StatefulSource):
    def __init__(self, redis_host, redis_port, channel):
        r = redis.Redis(host=redis_host, port=redis_port)
        # self.pubsub = r.pubsub()
        # ignore subscribe messages to get rid of spammy 1
        self.pubsub = r.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe(channel)
        self.channel = channel

    def next_batch(self):
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


class RedisPubSubInput(PartitionedInput):
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = os.getenv('REDIS_PORT', '6379')
        self.channel_name = os.getenv('REDIS_CHANNEL_NAME', 'device_events')

    def list_parts(self):
        return ['single-part']

    def build_part(self, for_key, resume_state):
        assert for_key == 'single-part'
        assert resume_state is None
        return RedisPubSubSource(
            self.redis_host,
            self.redis_port,
            self.channel_name,
        )


flow = Dataflow()

flow.input('inp', RedisPubSubInput())
flow.output('out', StdOutput())
