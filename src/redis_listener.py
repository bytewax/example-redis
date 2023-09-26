import logging
import os


import redis

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
CHANNEL_NAME = os.getenv('REDIS_CHANNEL_NAME', 'device_events')

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

# Function to handle the messages from the channel
def message_handler(message):
    data = message['data'].decode('utf-8')
    logger.info(f'Received data: {data}')

# Subscribe to the channel
pubsub = r.pubsub()
pubsub.subscribe(**{CHANNEL_NAME: message_handler})

# Listen for incoming messages
logger.info(f'Listening to channel: {CHANNEL_NAME}')
pubsub.run_in_thread(sleep_time=0.001)

