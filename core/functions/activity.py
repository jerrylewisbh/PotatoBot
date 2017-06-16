from telegram import Update, Bot
from core.types import User, AdminType, Admin, admin, session, OrderGroup, Group, Squad, Order, OrderCleared
from core.utils import send_async
from core.functions.inline_keyboard_handling import generate_groups_manage, generate_group_manage
from datetime import datetime, timedelta


@admin(adm_type=AdminType.GROUP)
def day_activity(bot: Bot, update: Update):
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        orders = sorted(squad.chat.orders, key=lambda x: x.date, reverse=True)
        status = dict()
        total_count = 0
        for order in orders:
            if datetime.now() - order.date > timedelta(days=1):
                break
            total_count += 1
            for cleared in order.cleared:
                if str(cleared.user) in status:
                    status[str(cleared.user)] += 1
                else:
                    status[str(cleared.user)] = 1
        msg = 'Статистика выполнения приказов за день:\n'
        for name, count in status.items():
            msg += '{}: {}/{}\n'.format(name, count, total_count)
        send_async(bot, chat_id=update.message.chat.id, text=msg)


@admin(adm_type=AdminType.GROUP)
def week_activity(bot: Bot, update: Update):
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        orders = sorted(squad.chat.orders, key=lambda x: x.date, reverse=True)
        status = dict()
        total_count = 0
        for order in orders:
            if datetime.now() - order.date > timedelta(days=7):
                break
            total_count += 1
            for cleared in order.cleared:
                if str(cleared.user) in status:
                    status[str(cleared.user)] += 1
                else:
                    status[str(cleared.user)] = 1
        msg = 'Статистика выполнения приказов за неделю:\n'
        for name, count in status.items():
            msg += '{}: {}/{}\n'.format(name, count, total_count)
        send_async(bot, chat_id=update.message.chat.id, text=msg)
