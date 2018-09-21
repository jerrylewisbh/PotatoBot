# -*- coding: utf-8 -*-
import functools
import json
import logging
import uuid
from threading import Thread

import pika

from config import CW_OUT_Q, CW_IN_Q, CW_EXCHANGE, CW_URL, CW_DEALS_Q, CW_OFFERS_Q, CW_DIGEST_Q, LOG_LEVEL_MQ, \
    MQ_TESTING, CW_DIGEST_A

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL_MQ)

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
    def __init__(self, handler, deals_handler, offers_handler, digest_handler, auction_digest_handler, dispatcher):
        """ Initialize Queue-Handler. We're passing a custom handler and a telegram-bot dispatcher
        instance to allow easier usage..."""
        Thread.__init__(self)

        self.EXCHANGE = CW_EXCHANGE
        self.EXCHANGE_TYPE = 'topic'
        self.QUEUE = CW_IN_Q
        self.QUEUE_DEALS = CW_DEALS_Q
        self.QUEUE_OFFERS = CW_OFFERS_Q
        self.QUEUE_DIGEST = CW_DIGEST_Q
        self.QUEUE_AUCTION = CW_DIGEST_A
        self._url = CW_URL

        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None

        self.handler = handler
        self.deals_handler = deals_handler
        self.offers_handler = offers_handler
        self.digest_handler = digest_handler
        self.auction_digest_handler = auction_digest_handler
        self.dispatcher = dispatcher

    def connect(self):
        logger.info('[Consumer] Connecting to Queue')
        logger.debug('[Consumer] Connecting to Queue %s', self._url)

        return pika.SelectConnection(
            pika.URLParameters(self._url),
            self.on_connection_open,
            stop_ioloop_on_close=False,
        )

    def on_connection_open(self, unused_connection):
        logger.info('[Consumer] Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        logger.info('[Consumer] Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logger.warning('[Consumer] Connection closed, reopening in 5 seconds: (%s) %s',
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
        logger.info('[Consumer] Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        logger.info('[Consumer] Setting up basic consumer')
        on_message_handler = functools.partial(self.handler, dispatcher=self.dispatcher)
        self._channel.basic_consume(on_message_handler, self.QUEUE)

        logger.info('[Consumer] Setting up basic consumer for DEALS')
        on_message_handler_deals = functools.partial(self.deals_handler, dispatcher=self.dispatcher)
        self._channel.basic_consume(on_message_handler_deals, self.QUEUE_DEALS)

        logger.info('[Consumer] Setting up basic consumer for OFFERS')
        on_message_handler_offers = functools.partial(self.offers_handler, dispatcher=self.dispatcher)
        self._channel.basic_consume(on_message_handler_offers, self.QUEUE_OFFERS)

        logger.info('[Consumer] Setting up basic consumer for DIGEST')
        on_message_handler_digest = functools.partial(self.digest_handler, dispatcher=self.dispatcher)
        self._channel.basic_consume(on_message_handler_digest, self.QUEUE_DIGEST)

        logger.info('[Consumer] Setting up basic consumer for AUCTION DIGEST')
        on_message_handler_digest = functools.partial(self.auction_digest_handler, dispatcher=self.dispatcher)
        self._channel.basic_consume(on_message_handler_digest, self.QUEUE_AUCTION)

    def add_on_channel_close_callback(self):
        logger.info('[Consumer] Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        logger.warning('[Consumer] Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def add_on_cancel_callback(self):
        logger.info('[Consumer] Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        logger.info('[Consumer] Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        logger.info('[Consumer] Acknowledging message %s', delivery_tag)
        if not MQ_TESTING:
            self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        if self._channel:
            logger.info('[Consumer] Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):
        logger.info('[Consumer] RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        logger.info('[Consumer] Closing the channel')
        self._channel.close()

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        logger.info('[Consumer] Stopping')
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()
        logger.info('[Consumer] Stopped')

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        logger.info('[Consumer] Closing connection')
        self._connection.close()


class Publisher(Thread, metaclass=Singleton):
    def __init__(self):
        Thread.__init__(self)

        self.EXCHANGE = CW_EXCHANGE
        self.EXCHANGE_TYPE = 'topic'
        self.QUEUE = CW_OUT_Q
        self._url = CW_URL

        # self._queue = queue.PriorityQueue()
        self._connection = None
        self._channel = None

        self._deliveries = None
        self._acked = None
        self._nacked = None
        self._message_number = None

        self._stopping = False

    def connect(self):
        logger.info('[Consumer] Connecting to Queue')
        logger.debug('[Consumer] Connecting to Queue %s', self._url)
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     on_open_callback=self.on_connection_open,
                                     on_close_callback=self.on_connection_closed,
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        logger.info('[Publisher] Connection opened')
        self.open_channel()

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._stopping:
            self._connection.ioloop.stop()
        else:
            logger.warning('[Publisher] Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self._connection.ioloop.stop)

    def open_channel(self):
        logger.info('[Publisher] Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        logger.info('[Publisher] Channel opened')
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        self.setup_exchange(self.EXCHANGE)

    def on_channel_closed(self, channel, reply_code, reply_text):
        logger.warning('[Publisher] Channel was closed: (%s) %s', reply_code, reply_text)
        self._channel = None
        if not self._stopping:
            self._connection.close()

    def setup_exchange(self, exchange_name):
        logger.info('[Publisher] Declaring exchange %s', exchange_name)
        self._channel.exchange_bind(
            self.on_exchange_declareok,
            exchange_name,
            exchange_name
        )

    def on_exchange_declareok(self, unused_frame):
        logger.info('[Publisher] Exchange declared')
        # self.run_publisher()
        # self.bind_queue(self.QUEUE)

    def publish(self, body):
        # Dear future me: Currently correlation_ids are not sent back by the CW API making some things hard...
        # Check for it again in the future...
        logger.info("[Publisher] Publishing item: %s", json.dumps(body))

        self._channel.basic_publish(
            exchange=self.EXCHANGE,
            routing_key=self.QUEUE,
            body=json.dumps(body),
            properties=pika.BasicProperties(
                correlation_id=str(uuid.uuid4())
            ),
        )
        logger.debug("[Publisher] ... published")

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
                if self._connection is not None and not self._connection.is_closed:
                    # Finish closing
                    self._connection.ioloop.start()

        logger.info('[Publisher] Stopped')

    def stop(self):
        logger.info('Stopping')
        self._stopping = True
        self.close_channel()
        self.close_connection()

    def close_channel(self):
        if self._channel is not None:
            logger.info('[Publisher] Closing the channel')
            self._channel.close()

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        if self._connection is not None:
            logger.info('[Publisher] Closing connection')
            self._connection.close()
