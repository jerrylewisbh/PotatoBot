# -*- coding: utf-8 -*-
from core.types import *


def fill_template(msg: str, user: User):
    if user.username:
        msg = msg.replace('%username%', '@' + user.username)
    else:
        msg = msg.replace('%username%', user.first_name + ' ' + user.last_name)
    msg = msg.replace('%first_name%', user.first_name)
    msg = msg.replace('%last_name%', user.last_name)
    msg = msg.replace('%id%', str(user.id))
    return msg
