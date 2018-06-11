from core.texts import *
from core.types import AdminType, check_admin, Session
from core.decorators import admin_allowed, user_allowed
from core.utils import send_async, update_group
from telegram import Bot, Update

Session()


def pin_decorator(func):
    @user_allowed
    def wrapper(bot, update, *args, **kwargs):
        group = update_group(update.message.chat)
        if group is None and \
                check_admin(update, AdminType.FULL) or \
                group is not None and \
                (group.allow_pin_all or
                 check_admin(update, AdminType.GROUP)):
            func(bot, update, *args, **kwargs)

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


@admin_allowed(AdminType.GROUP)
def pin_all(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    if not group.allow_pin_all:
        group.allow_pin_all = True
        Session.add(group)
        Session.commit()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_PIN_ALL_ENABLED)


@admin_allowed(AdminType.GROUP)
def not_pin_all(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    if group.allow_pin_all:
        group.allow_pin_all = False
        Session.add(group)
        Session.commit()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_PIN_ALL_DISABLED)
