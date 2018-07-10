""" Tool to make queues empty after bot was down for a longer time.... """

import os
import sys
import time
import redis

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# noinspection PyPep8
from config import *


def clear_handler(channel, method, properties, body, dispatcher):
    print("Cleared {}".format(method.delivery_tag))
    time.sleep(0.01)
    channel.basic_ack(method.delivery_tag)


if __name__ == "__main__":
    r = redis.StrictRedis(REDIS_SERVER)
    for key in r.keys("????????????????????????????????????"):
        r.delete(key)
