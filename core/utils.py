import telegram
from telegram import Bot
from telegram.error import TelegramError
from telegram.ext.dispatcher import run_async

from core.types import Group, Session, User

Session()


@run_async
def send_async(bot: Bot, *args, **kwargs):
    try:
        return bot.sendMessage(*args, **kwargs)

    except TelegramError as err:
        bot.logger.error(err.message)
        group = Session.query(Group).filter_by(id=kwargs['chat_id']).first()
        if group is not None:
            group.bot_in_group = False
            Session.add(group)
            Session.commit()
        return None


def create_or_update_user(telegram_user: telegram.User) -> User:
    """

    :type telegram_user: object
    :rtype: User
    """
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


def update_group(grp):
    if grp.type in ['group', 'supergroup', 'channel']:
        group = Session.query(Group).filter_by(id=grp.id).first()
        if group is None:
            group = Group(id=grp.id, title=grp.title,
                          username=grp.username)
            Session.add(group)

        else:
            updated = False
            if group.username != grp.username:
                group.username = grp.username
                updated = True
            if group.title != grp.title:
                group.title = grp.title
                updated = True
            if not group.bot_in_group:
                group.bot_in_group = True
                updated = True
            if updated:
                Session.add(group)

        Session.commit()
        return group
    return None


# Not used?
# def chunks(l, n):
#    n = max(1, n)
#    return (l[i:i + n] for i in range(0, len(l), n))


def pad_string(text, padding):
    """ Add whitespaces to a string to make different texts the same length for pre-formatted texts """
    if not text:
        text = ""

    while len(text) <= padding:
        text += " "

    return text
