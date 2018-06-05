import logging
from functools import partial

from sqlalchemy.exc import SQLAlchemyError
from telegram import Bot, Update

from core.types import AdminType, check_admin, check_ban, log, Session
from core.utils import create_or_update_user

Session()

def admin_allowed(adm_type=AdminType.FULL, ban_enable=True, allowed_types=()):
    def decorate(func):
        def wrapper(bot: Bot, update, *args, **kwargs):
            try:
                allowed = check_admin(update, adm_type, allowed_types)
                if ban_enable:
                    allowed &= check_ban(update)
                if allowed:
                    if func.__name__ not in ['manage_all', 'trigger_show', 'user_panel', 'wrapper', 'welcome']:
                        log(
                            update.effective_user.id,
                            update.effective_chat.id,
                            func.__name__,
                            update.message.text if update.message else None or update.callback_query.data if update.callback_query else None
                        )
                    # Fixme: Issues a message-update even if message did not change. This
                    # raises a telegram.error.BadRequest exception!
                    func(bot, update, *args, **kwargs)
            except SQLAlchemyError as err:
                bot.logger.error(str(err))
                Session.rollback()
        return wrapper
    return decorate


def user_allowed(ban_enable=True):
    if callable(ban_enable):
        return admin_allowed(AdminType.NOT_ADMIN)(ban_enable)
    else:
        def wrap(func):
            return admin_allowed(AdminType.NOT_ADMIN, ban_enable)(func)
    return wrap


def command_handler(function=None, permissions_required=None, allow_banned=False, allow_private=True, allow_group=False, allow_channel=False, *args, **kwargs):
    """
    Use this decorator to mark CommandHandlers and other exposed chat commands. This decorator allows you to check
    for user permissions.

    By default this decorator does not allow banned users to use the bot. Messages from these users will be dropped.
    Also by default only messages from private chats are allowed. You can influence this behaviour by changing
    allow_[group|channel|private].

    Functions with this decorator get also the "User" object passed into or the decorator will fail. It should be safe
    to depend on the existence of a valid User object.

    :param function:
    :param permissions_required:
    :param allow_banned:
    :param allow_private:
    :param allow_group:
    :param allow_channel:
    :param args:
    :param kwargs:
    :return:
    """

    print(function)
    print(permissions_required)
    print(allow_banned)
    print(allow_channel)
    print(allow_group)
    print(allow_private)
    print(args)
    print(kwargs)

    def wrapper(*args, **kwargs):
        print("-- inside --")
        print(function)
        print(permissions_required)
        print(allow_banned)
        print(allow_channel)
        print(allow_group)
        print(allow_private)
        print("-- own --")
        print('args - ', args)
        print('kwargs - ', kwargs)

        # Check if we have the required parameters in the right order...
        if not isinstance(args[0], Bot):
            error_msg = "Function is decorated as @command_handler. Expecting object of type {} as first argument. Got {}".format(
                Bot.__class__,
                type(args[0])
            )
            logging.error(error_msg)
            raise TypeError(error_msg)
        if not isinstance(args[1], Update):
            error_msg = "Function is decorated as @command_handler. Expecting object of type {} as second argument. Got {}".format(
                Update.__class__,
                type(args[1])
            )
            logging.error(error_msg)
            raise TypeError(error_msg)

        bot = args[0]
        update = args[1]

        if update.message.chat.type == 'channel' and not allow_channel:
            logging.debug("Message received in channel but allow_channel=False. Ignoring message.")
            return
        elif update.message.chat.type in ['group', 'supergroup'] and not allow_group:
            logging.debug("Message received in group/supergroup but allow_group=False. Ignoring message.")
            return
        elif update.message.chat.type == 'private' and not allow_private:
            logging.debug("Message received in private but allow_private=False. Ignoring message.")
            return

        user = create_or_update_user(args[0])
        if not user:
            logging.error("create_or_update_user() did not return a User!")
            raise ValueError("create_or_update_user() did not return a User!")
        if user.is_banned and not allow_banned:
            logging.debug("Message received from banned user allow_banned=False. Ignoring message.")
            return

        return function(*args, user, **kwargs)

    return wrapper

