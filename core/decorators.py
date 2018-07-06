import logging
from functools import wraps

import telegram
from telegram import Bot, Update

from core.types import AdminType, Session, check_admin, User

Session()


# TODO: A lot of this can be moved out here in favor of python-telegram-command handlers and filters!

# noinspection PyNestedDecorators
def command_handler(min_permission: AdminType = AdminType.NOT_ADMIN, allow_private: bool = True,
                    allow_group: bool = False, allow_channel: bool = False,
                    allow_banned: bool = False, squad_only: bool = False, testing_only: bool = False,
                    forward_from: int = None,
                    *args: object,
                    **kwargs: object) -> object:
    """
    Use this decorator to mark CommandHandlers and other exposed chat commands.py. This decorator allows you to check
    for user permissions.

    By default this decorator does not allow banned users to use the bot. Messages from these users will be dropped.
    Also by default only messages from private chats are allowed. You can influence this behaviour by changing
    allow_[group|channel|private].

    Functions with this decorator get also the "User" object passed into or the decorator will fail. It should be safe
    to depend on the existence of a valid User object. permission_required:



    :type min_permission: AdminType
    :type allow_private: bool
    :type allow_banned: bool
    :type allow_private: bool
    :type allow_group: bool
    :type allow_channel: bool
    :type squad_only: bool
    :type testing_only: bool
    :type forward_from: int
    :type args: object
    :type kwargs: object

    :param min_permission: AdminType
    :param allow_banned:
    :param allow_private:
    :param allow_group:
    :param allow_channel:
    :param squad_only:
    :param testing_only:
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
                    Bot.__class__, type(args[0]))
                logging.error(error_msg)
                raise TypeError(error_msg)
            if not isinstance(args[1], Update):
                error_msg = "Function is decorated as @command_handler. Expecting object of type {} as second argument. Got {}".format(
                    Update.__class__, type(args[1]))
                logging.error(error_msg)
                raise TypeError(error_msg)

            bot = args[0]
            update = args[1]
            # args = kwargs['args'] if kwargs and 'args' in kwargs else None

            if update.message and not update.callback_query:
                if update.message.chat.type == 'channel' and not allow_channel:
                    logging.debug("Message received in channel but allow_channel=False. Ignoring message.")
                    return
                elif update.message.chat.type in ['group', 'supergroup'] and not allow_group:
                    logging.debug("Message received in group/supergroup but allow_group=False. Ignoring message.")
                    return
                elif update.message.chat.type == 'private' and not allow_private:
                    logging.debug("Message received in private but allow_private=False. Ignoring message.")
                    return

            if forward_from and update.message.forward_from and forward_from != update.message.forward_from.id:
                logging.debug("Message is not a valid forward %s!=%s", update.message.forward_from.id, forward_from)
                return

            if update.channel_post:
                # Channel posts are not allowed. Block functions
                logging.debug("Channel post... (be careful, user is None!)")
                return func(bot, update, None, **kwargs)
            else:
                user = create_or_update_user(update.effective_user)
                if not user:
                    logging.error("create_or_update_user() did not return a User!")
                    raise ValueError("create_or_update_user() did not return a User!")
                if user.is_banned and not allow_banned:
                    logging.info(
                        "Message received from banned user '%s' but this is not an allowed function for a banned account.",
                        user.id)
                    return

                if squad_only and not user.is_squadmember:
                    logging.debug("This is a squad only feature and user '%s' is no squad member", user.id)
                    return

                if testing_only and not user.is_tester:
                    logging.debug(
                        "This is a testing-squad only feature and user '%s' is no testing-squad member",
                        user.id
                    )
                    return

                if not min_permission:
                    raise ValueError("None is no valid AdminType!")
                elif min_permission not in AdminType:
                    raise ValueError("Given permission does not match an existing AdminType")
                elif min_permission != AdminType.NOT_ADMIN:
                    # We need actual admin-permissions. Check.
                    if not check_admin(update, min_permission):
                        logging.warning(
                            "'%s' is not allowed to call function '%s'!",
                            "@{}".format(user.username) if user.username else user.id,
                            func.__name__ if hasattr(func, "__name__") else "unknown,"
                        )
                        return
                # Else: Normal user permissions rqd...

                logging.info("User '%s' has called: '%s'", user.id, func.__name__)

            return func(bot, update, user, **kwargs)

        return wrapper

    return real_decorator


def create_or_update_user(telegram_user: telegram.User) -> User:
    """

    :type telegram_user: object
    :rtype: User
    """
    if not telegram_user:
        return None
    user = Session.query(User).filter_by(id=telegram_user.id).first()
    if not user:
        user = User(
            id=telegram_user.id,
            username=telegram_user.username or '',
            first_name=telegram_user.first_name or '',
            last_name=telegram_user.last_name or ''
        )
        Session.add(user)
    else:
        updated = False
        if user.username != telegram_user.username:
            user.username = telegram_user.username
            updated = True
        if user.first_name != telegram_user.first_name:
            user.first_name = telegram_user.first_name
            updated = True
        if user.last_name != telegram_user.last_name:
            user.last_name = telegram_user.last_name
            updated = True
        if updated:
            Session.add(user)
    Session.commit()
    return user
