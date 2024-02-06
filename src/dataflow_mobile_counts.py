import json
from datetime import timedelta, datetime, timezone

import bytewax.operators as op
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow
from bytewax.operators.window import SystemClockConfig, TumblingWindow

from bytewax_redis_input import RedisPubSubSource


def deserialize(payload):
    try:
        data = json.loads(payload)
    except json.decoder.JSONDecodeError:
        return None
    return data


def initial_count(data):
    if data is None:
        return 'Uknown', 0
    return data['os_timezone'], int(data['device_is_mobile'])


def add(count1, count2):
    return count1 + count2


def jsonify(timezone__mobile_count):
    tz, count = timezone__mobile_count
    return {'timezone': tz, 'num_mobile_users': count}


clock_config = SystemClockConfig()
window_config = TumblingWindow(
    length=timedelta(seconds=5),
    align_to=datetime(2023, 1, 1, tzinfo=timezone.utc),
)

flow = Dataflow("redis-count")

stream = op.input('inp', flow, RedisPubSubSource())

stream = op.map('serde', stream, deserialize)
keyed_stream = op.map('init_count', stream, initial_count)
count_stream = op.window.reduce_window('sum', keyed_stream, clock_config, window_config, add)
count_stream = op.map('format', count_stream, jsonify)

op.output('out', count_stream, StdOutSink())
