# -*- coding: utf-8 -*-
from core.types import *
from datetime import datetime


def fill_template(msg: str, user: User):
    if user.username:
        msg = msg.replace('%username%', '@' + user.username)
    else:
        msg = msg.replace('%username%', user.first_name + ' ' + user.last_name)
    msg = msg.replace('%first_name%', user.first_name)
    msg = msg.replace('%last_name%', user.last_name)
    msg = msg.replace('%id%', str(user.id))
    return msg


def fill_char_template(msg: str, user: User):
    msg = fill_template(msg, user)
    char = sorted(user.character, key=lambda x: x.date)[0]
    msg = msg.replace('%date%', str(char.date))
    msg = msg.replace('%name%', str(char.name))
    msg = msg.replace('%prof%', str(char.prof))
    msg = msg.replace('%pet%', str(char.pet))
    msg = msg.replace('%petLevel%', str(char.petLevel))
    msg = msg.replace('%maxStamina%', str(char.maxStamina))
    msg = msg.replace('%level%', str(char.level))
    msg = msg.replace('%attack%', str(char.attack))
    msg = msg.replace('%defence%', str(char.defence))
    msg = msg.replace('%exp%', str(char.exp))
    msg = msg.replace('%needExp%', str(char.needExp))
    msg = msg.replace('%castle%', str(char.castle))
    msg = msg.replace('%gold%', str(char.gold))
    return msg
