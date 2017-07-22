from telegram import Bot, Update, Message

from core.texts import MSG_PIN_ALL_ENABLED, MSG_PIN_ALL_DISABLED
from core.types import AdminType, admin, session
from core.utils import update_group, send_async


def pin_decorator(func):
    def wrapper(bot, update, *args, **kwargs):
        group = update_group(update.message.chat)
        if group is None:
            ((admin(adm_type=AdminType.FULL))(func))(bot, update, *args, **kwargs)
        elif group.allow_pin_all:
            func(bot, update, *args, **kwargs)
        else:
            ((admin(adm_type=AdminType.GROUP))(func))(bot, update, *args, **kwargs)
    return wrapper


@pin_decorator
def pin(bot: Bot, update: Update):
    bot.request.post(bot.base_url + '/pinChatMessage',
                     {'chat_id': update.message.reply_to_message.chat.id,
                      'message_id': update.message.reply_to_message.message_id,
                      'disable_notification': False})


@pin_decorator
def silent_pin(bot: Bot, update: Update):
    bot.request.post(bot.base_url + '/pinChatMessage',
                     {'chat_id': update.message.reply_to_message.chat.id,
                      'message_id': update.message.reply_to_message.message_id,
                      'disable_notification': True})


@admin(AdminType.GROUP)
def pin_all(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    if not group.allow_pin_all:
        group.allow_pin_all = True
        session.add(group)
        session.commit()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_PIN_ALL_ENABLED)


@admin(AdminType.GROUP)
def not_pin_all(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    if group.allow_pin_all:
        group.allow_pin_all = False
        session.add(group)
        session.commit()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_PIN_ALL_DISABLED)
