import json
from datetime import timedelta, datetime, timezone

from bytewax import operators as op
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow
from bytewax.operators.window import SystemClockConfig, TumblingWindow
from bytewax.operators import window as window_op

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

flow = Dataflow('dataflow_mobile_counts')

inp = op.input('redis_inp', flow, RedisPubSubSource())
des = op.map('deserialize', inp, deserialize)

init_count = op.map('initial_count', des, initial_count)
reduce = window_op.reduce_window(
    'sum',
    init_count,
    clock_config,
    window_config,
    add,
)

serialize = op.map('jsonify', reduce, jsonify)

op.output('out', serialize, StdOutSink())
