# -*- coding: utf-8 -*-

from threading import Thread

import functools

from config import CW_OUT_Q, CW_IN_Q, CW_EXCHANGE, CW_URL

import json
import pika
import queue
import logging

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

pika_logger = logging.getLogger('pika')
pika_logger.setLevel(logging.WARN)

class Singleton(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

class Consumer(Thread):
    def __init__(self, handler, dispatcher):
        """ Initialize Queue-Handler. We're passing a custom handler and a telegram-bot dispatcher
        instance to allow easier usage..."""
        Thread.__init__(self)

        self.EXCHANGE = CW_EXCHANGE
        self.EXCHANGE_TYPE = 'topic' 
        self.QUEUE = CW_IN_Q
        self._url = CW_URL

        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None

        self.handler = handler
        self.dispatcher = dispatcher

    def connect(self):
        LOGGER.info('[Consumer] Connecting to %s', self._url)
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        LOGGER.info('[Consumer] Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        LOGGER.info('[Consumer] Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('[Consumer] Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:
            self._connection = self.connect()
            self._connection.ioloop.start()

    def open_channel(self):
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        LOGGER.info('[Consumer] Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        LOGGER.info('[Consumer] Setting up basic consumer')
        on_message_handler = functools.partial(self.handler, dispatcher=self.dispatcher)
        self._channel.basic_consume(on_message_handler, self.QUEUE)

    def add_on_channel_close_callback(self):
        LOGGER.info('[Consumer] Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        LOGGER.warning('[Consumer] Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def add_on_cancel_callback(self):
        LOGGER.info('[Consumer] Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        LOGGER.info('[Consumer] Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        LOGGER.info('[Consumer] Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        if self._channel:
            LOGGER.info('[Consumer] Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):
        LOGGER.info('[Consumer] RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        LOGGER.info('[Consumer] Closing the channel')
        self._channel.close()

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        LOGGER.info('[Consumer] Stopping')
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()
        LOGGER.info('[Consumer] Stopped')

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        LOGGER.info('[Consumer] Closing connection')
        self._connection.close()

class Publisher(Thread, metaclass=Singleton):
        def __init__(self):
            Thread.__init__(self)

            self.EXCHANGE = CW_EXCHANGE
            self.EXCHANGE_TYPE = 'topic'
            self.QUEUE = CW_OUT_Q
            self._url = CW_URL

            self._queue = queue.Queue()
            self._connection = None
            self._channel = None

            self._deliveries = None
            self._acked = None
            self._nacked = None
            self._message_number = None

            self._stopping = False

        def connect(self):
            LOGGER.info('[Publisher] Connecting to %s', self._url)
            return pika.SelectConnection(pika.URLParameters(self._url),
                                         on_open_callback=self.on_connection_open,
                                         on_close_callback=self.on_connection_closed,
                                         stop_ioloop_on_close=False)

        def on_connection_open(self, unused_connection):
            LOGGER.info('[Publisher] Connection opened')
            self.open_channel()

        def on_connection_closed(self, connection, reply_code, reply_text):
            self._channel = None
            if self._stopping:
                self._connection.ioloop.stop()
            else:
                LOGGER.warning('[Publisher] Connection closed, reopening in 5 seconds: (%s) %s',
                               reply_code, reply_text)
                self._connection.add_timeout(5, self._connection.ioloop.stop)

        def open_channel(self):
            LOGGER.info('[Publisher] Creating a new channel')
            self._connection.channel(on_open_callback=self.on_channel_open)

        def on_channel_open(self, channel):
            LOGGER.info('[Publisher] Channel opened')
            self._channel = channel
            self._channel.add_on_close_callback(self.on_channel_closed)
            self.setup_exchange(self.EXCHANGE)

        def on_channel_closed(self, channel, reply_code, reply_text):
            LOGGER.warning('[Publisher] Channel was closed: (%s) %s', reply_code, reply_text)
            self._channel = None
            if not self._stopping:
                self._connection.close()

        def setup_exchange(self, exchange_name):
            LOGGER.info('[Publisher] Declaring exchange %s', exchange_name)
            self._channel.exchange_bind(
                self.on_exchange_declareok,
                exchange_name,
                exchange_name
            )

        def on_exchange_declareok(self, unused_frame):
            LOGGER.info('[Publisher] Exchange declared')
            #self.run_publisher()
            #self.bind_queue(self.QUEUE)

        def publish(self, body):
            LOGGER.info("[Publisher] Got item from queue %s", json.dumps(body))
            self._channel.basic_publish(self.EXCHANGE, self.QUEUE, json.dumps(body))
            #self._channel.basic_publish(self.EXCHANGE, self.QUEUE, json.dumps({'action': 'createAuthCode', 'payload': {'userId': 176862585}}))
            LOGGER.info("[Publisher] ... published")

        def run(self):
            """ Run the example code by connecting and then starting the IOLoop. """
            while not self._stopping:
                self._connection = None
                self._deliveries = []
                self._acked = 0
                self._nacked = 0
                self._message_number = 0

                try:
                    self._connection = self.connect()
                    self._connection.ioloop.start()
                except KeyboardInterrupt:
                    self.stop()
                    if (self._connection is not None and
                            not self._connection.is_closed):
                        # Finish closing
                        self._connection.ioloop.start()

            LOGGER.info('[Publisher] Stopped')

        def stop(self):
            LOGGER.info('Stopping')
            self._stopping = True
            self.close_channel()
            self.close_connection()

        def close_channel(self):
            if self._channel is not None:
                LOGGER.info('[Publisher] Closing the channel')
                self._channel.close()

        def close_connection(self):
            """This method closes the connection to RabbitMQ."""
            if self._connection is not None:
                LOGGER.info('[Publisher] Closing connection')
                self._connection.close()


