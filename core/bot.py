#!/usr/bin/env python3
# encoding=utf-8

'''
MessageQueue usage example with @queuedmessage decorator.
'''
import logging

import telegram.bot
from telegram.error import Unauthorized
from telegram.ext import messagequeue as mq


class MQBot(telegram.bot.Bot):
    '''A subclass of Bot which delegates send method handling to MQ'''

    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except BaseException:
            pass
        super(MQBot, self).__del__()

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
        #if "text" in kwargs:
        #    print("---------------")
        #    print(kwargs['text'])
        #    print("---------------")

        try:
            return super(MQBot, self).send_message(*args, **kwargs)
        except Unauthorized as ex:
            if "chat_id" in kwargs:
                logging.warning(
                    "Unauthorized occurred: %s. We should probably remove user user_id='%s' from bot.",
                    ex.message,
                    kwargs['chat_id'],
                    exc_info=True
                )
