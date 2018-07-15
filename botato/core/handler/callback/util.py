# -*- coding: utf-8 -*-
import logging
import pickle
from enum import IntFlag, auto

import redis
import uuid

from config import REDIS_SERVER, REDIS_PORT


class CallbackAction(IntFlag):
    """ CAREFUL! Do NOT add someting in between lightly as this will invalidate existing IDs in REDIS!"""

    # TOP related stuff...
    TOP = auto()  # General Toplist
    TOP_ATK = auto()  # Attack
    TOP_DEF = auto()  # Defense
    TOP_EXP = auto()  # Experience
    TOP_ATT = auto()  # Battle attendance
    TOP_FILTER_CLASS = auto()  # Filter by class
    TOP_FILTER_SQUAD = auto()  # Filter by squad
    TOP_FILTER_WEEK = auto()  # Filter by week
    TOP_FILTER_MONTH = auto()  # Filter by month
    TOP_FILTER_ALL = auto()  # Filter by all dates

    # Quest related stuff
    QUEST_LOCATION = auto()
    FORAY_PLEDGE = auto()

    # Squad related
    SQUAD_LEAVE = auto()
    SQUAD_JOIN = auto()
    SQUAD_INVITE = auto()
    SQUAD_LIST = auto()
    SQUAD_LIST_MEMBERS = auto()
    SQUAD_MANAGE = auto()

    # Report
    REPORT = auto()
    PAGINATION_SKIP_FORWARD = auto()
    PAGINATION_SKIP_BACKWARD = auto()
    PAGINATION_SKIP_NEXT = auto()
    PAGINATION_SKIP_PREV = auto()
    PAGINATION_SKIP_BATTLE_1 = auto()
    PAGINATION_SKIP_BATTLE_2 = auto()
    PAGINATION_SKIP_BATTLE_3 = auto()

    # Hero related
    HERO = auto()
    HERO_EQUIP = auto()
    HERO_SKILL = auto()
    HERO_STOCK = auto()

    # Settings
    SETTING = auto()

    # Orders
    ORDER = auto()
    ORDER_GROUP = auto()
    ORDER_GROUP_MANAGE = auto()
    ORDER_GROUP_ADD = auto()

    # Groups
    GROUP = auto()
    GROUP_INFO = auto()
    GROUP_MANAGE = auto()
    ORDER_GIVE = auto()
    ORDER_CONFIRM = auto()


class Action(object):
    def __init__(self, action, user_id, **kwargs):
        self.action = action
        self.user_id = user_id
        self.data = kwargs

    def __str__(self):
        return "Action: '{}', User-ID: '{}', Data: {}".format(self.action, self.user_id, str(self.data) if self.data else "Empty")


def get_callback_action(uuid_key, user_id, allow_all=False):
    """ Save a simple callback to redis. This checks if the user using the keyboard is also the one we initially
    registered. This can be disabled with allow_all=True"""
    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
    action = r.get(uuid_key)
    if action:
        action = pickle.loads(action)
        logging.debug(action)
        if user_id == action.user_id or allow_all:
            return action
        else:
            logging.error("user_id in action != user_id used for loading!")
            return None
    return None


def create_callback(action, user_id, **kwargs):
    """ Callback data for Telegram is limited to a few bytes. To be more flexible we create a UUID and store the
    actual callback-data in Redis. Keys are stored for up to one day and then get removed."""

    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)

    a = Action(action, user_id, **kwargs)
    callback_id = str(uuid.uuid1())
    r.set(callback_id, pickle.dumps(a), ex=3600 * 30)  # Age out data after 180 days...
    return callback_id
