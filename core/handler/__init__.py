# -*- coding: utf-8 -*-
import re

from telegram import Bot, Update
from telegram.ext import BaseFilter

from core.utils import create_or_update_user


class FilterUser(BaseFilter):
    def filter(self, message):
        user = create_or_update_user(message.from_user)
        return True if user else False

class FilterSquad(BaseFilter):
    def filter(self, message):
        user = create_or_update_user(message.from_user)
        return user.is_squadmember


class MessageHandler(object):
    def __init__(self, condition, action):
        self.condition = condition
        self.action = action

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.action)

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.action)


class RegexHandler(MessageHandler):
    def __init__(self, regex, action):
        self.condition = lambda update: re.search(regex, update.message.text)
        self.action = action


def handle_message(handlers, msg, bot: Bot, update: Update, *args, **kwargs):
    for handler in handlers:
        if handler.condition(update):
            handler.action(bot, update, *args, **kwargs)
            return True
    return False
