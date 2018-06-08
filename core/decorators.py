import logging
from functools import wraps

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


def command_handler(permissions_required: AdminType = AdminType.NOT_ADMIN, allow_private: bool = True,
                    allow_group: bool = False, allow_channel: bool = False,
                    allow_banned: bool = False, forward_from: int = None,
                    *args: object,
                    **kwargs : object) -> object:
    """
    Use this decorator to mark CommandHandlers and other exposed chat commands. This decorator allows you to check
    for user permissions.

    By default this decorator does not allow banned users to use the bot. Messages from these users will be dropped.
    Also by default only messages from private chats are allowed. You can influence this behaviour by changing
    allow_[group|channel|private].

    Functions with this decorator get also the "User" object passed into or the decorator will fail. It should be safe
    to depend on the existence of a valid User object. permission_required:



    :type permissions_required: AdminType
    :type allow_private: bool
    :type allow_banned: bool
    :type allow_private: bool
    :type allow_group: bool
    :type allow_channel: bool
    :type forward_from: int
    :type args: object
    :type kwargs: object

    :param permissions_required: AdminType
    :param allow_banned:
    :param allow_private:
    :param allow_group:
    :param allow_channel:
    :param forward_from:
    :param args:
    :param kwargs:
    :return:
    """

    def real_decorator(func, *args, **kwargs):
        @wraps(func)
        def wrapper(*args, **kwargs):
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

            #user = create_or_update_user(update.message.from_user)
            user = create_or_update_user(update.effective_user)
            if not user:
                logging.error("create_or_update_user() did not return a User!")
                raise ValueError("create_or_update_user() did not return a User!")
            if user.is_banned and not allow_banned:
                logging.info(
                    "Message received from banned user '%s' but this is not an allowed function for a banned account.",
                    user.id
                )
                return

            if forward_from and forward_from != update.message.forward_from.id:
                logging.debug("Message is not a valid forward %s!=%s", update.message.forward_from.id, forward_from)
                return

            if permissions_required:
                if permissions_required not in AdminType:
                    raise ValueError("Given permission does not match an existing AdminType")
                #print(user.permission)

                # The lower the number, the higher the permission is...
                #if permissions_required in [AdminType.SUPER, AdminType.FULL]:
                #    # Highest permission levels. Just pass
                #    logging.debug("%s is admin-type %s!", user.id, user.permission)



            logging.info("User '%s' has called: '%s'", user.id, func.__name__)

            return func(bot, update, user, **kwargs)
        return wrapper
    return real_decorator

