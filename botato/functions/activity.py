from datetime import datetime, timedelta
from telegram import Update

from core.bot import MQBot
from core.decorators import command_handler
from core.texts import MSG_ORDER_STATISTIC, MSG_ORDER_STATISTIC_OUT_FORMAT
from core.db import Session
from core.enums import AdminType
from core.model import User, Squad
from core.utils import send_async

Session()


def activity(squad, days=0, hours=0):
    orders = sorted(squad.chat.orders, key=lambda x: x.date, reverse=True)
    status = dict()
    total_count = 0
    for order in orders:
        if datetime.now() - order.date > timedelta(days=days, hours=hours):
            break
        total_count += 1
        for cleared in order.cleared:
            if str(cleared.user) in status:
                status[str(cleared.user)] += 1
            else:
                status[str(cleared.user)] = 1
    msg = MSG_ORDER_STATISTIC.format(days)
    users = sorted(status.items(), key=lambda x: x[1], reverse=True)
    for name, count in users:
        msg += MSG_ORDER_STATISTIC_OUT_FORMAT.format(name, count, total_count)
    return msg


@command_handler(
    min_permission=AdminType.GROUP,
    allow_group=True,
    allow_private=False
)
def day_activity(bot: MQBot, update: Update, user: User):
    squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        msg = activity(squad, days=1)
        send_async(bot, chat_id=update.message.chat.id, text=msg)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_group=True,
    allow_private=False
)
def week_activity(bot: MQBot, update: Update, user: User):
    squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        msg = activity(squad, days=7)
        send_async(bot, chat_id=update.message.chat.id, text=msg)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_group=True,
    allow_private=False
)
def battle_activity(bot: MQBot, update: Update, user: User):
    squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        msg = activity(squad, hours=4)
        send_async(bot, chat_id=update.message.chat.id, text=msg)
