""" Tool to make queues empty after bot was down for a longer time.... """

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../botato')))

# noinspection PyPep8
from cwmq import Consumer


def clear_handler(channel, method, properties, body, dispatcher):
    print("Cleared {}".format(method.delivery_tag))
    #time.sleep(0.01)
    channel.basic_ack(method.delivery_tag)


if __name__ == "__main__":
    q_in = Consumer(
        clear_handler,
        clear_handler,
        clear_handler,
        clear_handler,
        dispatcher=None
    )
    q_in.setName("T1_IN")
    q_in.start()

    q_in.join()
