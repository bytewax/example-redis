import json
import logging
import os
import pathlib

import redis


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
CHANNEL_NAME = os.getenv('REDIS_CHANNEL_NAME', 'device_events')
JSONL_FILE = os.getenv('EVENTS_JSONL_FILE', 'data/events.jsonl')

# Connect to Redis
if not REDIS_PASSWORD:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
else:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)



# Read the .jsonl file and publish to the Redis channel
with pathlib.Path(JSONL_FILE).open() as file:
    for line in file:
        try:
            # Here we're just checking that each line is valid JSON,
            # you can skip this if you're sure of the .jsonl format.
            json.loads(line)
            # Publish to the Redis channel
            r.publish(CHANNEL_NAME, line)

        except json.JSONDecodeError:
            logger.exception(f'Invalid JSON: {line}')

logger.info('Data published to Redis channel!')

