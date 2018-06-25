# -*- coding: utf-8 -*-
import json
import logging

import redis
import uuid
from telegram import InlineKeyboardButton

from config import REDIS_SERVER, REDIS_PORT
from core.types import User


class InlineButton(object):
    def __init__(self, title, **kwargs):
        self.title = title
        self.payload = kwargs


def get_action(uuid):
    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
    action = json.loads(r.get(uuid))
    return action


def create_button(title: InlineButton, user: User, back: bool = False, **kwargs: object) -> InlineKeyboardButton:
    """ Convenience wrapper for creating a button... """

    logging.info(title.name)
    cb = create_callback(
        title.name,
        user=user,
        back=back
    )
    return InlineKeyboardButton(str(title.value), callback_data=cb)


def create_callback(action: str, user: User, back: bool = False) -> str:
    """ Callback data for Telegram is limited to a few bytes. To be more flexible we create a UUID and store the
    actual callback-data in Redis. Keys are stored for up to one day and then get removed."""

    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)

    data = json.dumps({
        'action': action,
        'user_id': user.id,
        'back': back
    })

    callback_id = str(uuid.uuid1())
    r.set(callback_id, data, ex=3600*180) # Age out data after 180 days...
    return callback_id
