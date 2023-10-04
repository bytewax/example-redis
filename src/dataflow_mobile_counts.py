import json
from datetime import timedelta, datetime, timezone

from bytewax.connectors.stdio import StdOutput
from bytewax.dataflow import Dataflow
from bytewax.window import SystemClockConfig, TumblingWindow

from bytewax_redis_input import RedisPubSubInput


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

flow = Dataflow()

flow.input('inp', RedisPubSubInput())

flow.map(deserialize)
flow.map(initial_count)
flow.reduce_window('sum', clock_config, window_config, add)
flow.map(jsonify)

flow.output('out', StdOutput())
