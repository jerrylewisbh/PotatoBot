from telegram import Update, Bot
from core.types import Group, Trigger, AdminType, admin, session
from core.utils import send_async, update_group
from core.texts import *


def trigger_decorator(func):
    def wrapper(bot, update, *args, **kwargs):
        group = update_group(update.message.chat)
        if group is None:
            ((admin(adm_type=AdminType.FULL))(func))(bot, update, *args, **kwargs)
        elif group.allow_trigger_all:
            func(bot, update, *args, **kwargs)
        else:
            ((admin(adm_type=AdminType.GROUP))(func))(bot, update, *args, **kwargs)
    return wrapper


@admin()
def set_trigger(bot: Bot, update: Update):
    msg = update.message.text.split(' ', 1)
    if len(msg) == 2:
        msg = msg[1]
        new_trigger = msg.split('::', 1)
        if len(new_trigger) == 2 and len(new_trigger[0]):
            trigger = session.query(Trigger).filter_by(trigger=new_trigger[0]).first()
            if trigger is None:
                trigger = Trigger(trigger=new_trigger[0], message=new_trigger[1])
            else:
                trigger.message = new_trigger[1]
            session.add(trigger)
            session.commit()
            send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_NEW.format(new_trigger[0]))
        else:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_NEW_ERROR)


@admin(adm_type=AdminType.GROUP)
def add_trigger(bot: Bot, update: Update):
    msg = update.message.text.split(' ', 1)
    if len(msg) == 2:
        msg = msg[1]
        new_trigger = msg.split('::', 1)
        if len(new_trigger) == 2:
            new_trigger[0] = new_trigger[0].strip()
            if len(new_trigger[0]) > 0:
                trigger = session.query(Trigger).filter_by(trigger=new_trigger[0]).first()
                if trigger is None:
                    trigger = Trigger(trigger=new_trigger[0], message=new_trigger[1])
                    session.add(trigger)
                    session.commit()
                    send_async(bot, chat_id=update.message.chat.id,
                               text=MSG_TRIGGER_NEW.format(new_trigger[0]))
                else:
                    send_async(bot, chat_id=update.message.chat.id,
                               text=MSG_TRIGGER_EXISTS.format(new_trigger[0]))
            else:
                send_async(bot, chat_id=update.message.chat.id,
                           text=MSG_TRIGGER_NEW_ERROR)
        else:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_NEW_ERROR)


@trigger_decorator
def trigger_show(bot: Bot, update: Update):
    trigger = session.query(Trigger).filter_by(trigger=update.message.text).first()
    if trigger is not None:
        send_async(bot, chat_id=update.message.chat.id, text=trigger.message, disable_web_page_preview=True)


@admin(adm_type=AdminType.GROUP)
def enable_trigger_all(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    group.allow_trigger_all = True
    session.add(group)
    session.commit()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_ALL_ENABLED)


@admin(adm_type=AdminType.GROUP)
def disable_trigger_all(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    group.allow_trigger_all = False
    session.add(group)
    session.commit()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_ALL_DISABLED)


@admin()
def del_trigger(bot: Bot, update: Update):
    msg = update.message.text.split(' ', 1)[1]
    trigger = session.query(Trigger).filter_by(trigger=msg).first()
    if trigger is not None:
        session.delete(trigger)
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_DEL.format(msg))
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_DEL_ERROR)


@trigger_decorator
def list_triggers(bot: Bot, update: Update):
    triggers = session.query(Trigger).all()
    msg = MSG_TRIGGER_LIST_HEADER + ('\n'.join([trigger.trigger for trigger in triggers]) or MSG_EMPTY)
    send_async(bot, chat_id=update.message.chat.id, text=msg)
