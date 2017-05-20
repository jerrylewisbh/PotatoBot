import json
from telegram import Bot, Update, ReplyKeyboardMarkup, KeyboardButton
from core.types import User, Group, Admin, session, admin
from core.utils import send_async
from core.functions.admins import del_adm
from enum import Enum
from core.enums import Castle, Icons
import logging


def generate_standard_markup():
    buttons = []
    buttons.append(KeyboardButton('Приказы'))
    buttons.append(KeyboardButton('Статус'))
    buttons.append(KeyboardButton('Группы'))
    return ReplyKeyboardMarkup([buttons], True)
