import logging
from config import LOGFILE, SUPER_ADMIN_ID, LOG_ALLOWED_RECIPIENTS

from telegram import Bot, Update

from core.decorators import command_handler
from core.texts import *
from core.types import Admin, AdminType, Session, User
from core.utils import send_async
from functions.inline_markup import generate_group_info

Session()


@command_handler(
    min_permission=AdminType.FULL,
)
def set_admin(bot: Bot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)[1]
    msg = msg.replace('@', '')
    if msg != '':
        user = Session.query(User).filter_by(username=msg).first()
        if user is None:
            send_async(bot,
                       chat_id=update.message.chat.id,
                       text=MSG_USER_UNKNOWN)

        else:
            adm = Session.query(Admin).filter_by(user_id=user.id,
                                                 admin_group=update.message.chat.id).first()

            if adm is None:
                new_group_admin = Admin(user_id=user.id,
                                        admin_type=AdminType.GROUP.value,
                                        admin_group=update.message.chat.id)

                Session.add(new_group_admin)
                Session.commit()
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_NEW_GROUP_ADMIN.format(user.username))

            else:
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_NEW_GROUP_ADMIN_EXISTS.format(user.username))


def del_adm(bot, chat_id, user):
    adm = Session.query(Admin).filter_by(user_id=user.id,
                                         admin_group=chat_id).first()

    if adm is None:
        send_async(bot,
                   chat_id=chat_id,
                   text=MSG_DEL_GROUP_ADMIN_NOT_EXIST.format(user.username))

    else:
        Session.delete(adm)
        Session.commit()
        send_async(bot,
                   chat_id=chat_id,
                   text=MSG_DEL_GROUP_ADMIN.format(user.username))


@command_handler(
    min_permission=AdminType.FULL,
)
def del_admin(bot: Bot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)[1]
    if msg.find('@') != -1:
        msg = msg.replace('@', '')
        if msg != '':
            user = Session.query(User).filter_by(username=msg).first()
            if user is None:
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_USER_UNKNOWN)

            else:
                del_adm(bot, update.message.chat.id, user)
    else:
        user = Session.query(User).filter_by(id=msg).first()
        if user is None:
            send_async(bot,
                       chat_id=update.message.chat.id,
                       text=MSG_USER_UNKNOWN)

        else:
            del_adm(bot, update.message.chat.id, user)


@command_handler(
    min_permission=AdminType.FULL,
)
def list_admins(bot: Bot, update: Update, user: User):
    admins = Session.query(Admin).filter(Admin.admin_group == update.message.chat.id).all()
    users = []
    for admin_user in admins:
        users.append(Session.query(User).filter_by(id=admin_user.user_id).first())
    msg = MSG_LIST_ADMINS_HEADER
    for user in users:
        msg += MSG_LIST_ADMINS_FORMAT.format(user.id,
                                             user.username,
                                             user.first_name,
                                             user.last_name)

    send_async(bot, chat_id=update.message.chat.id, text=msg)


@command_handler(
    allow_group=True
)
def admins_for_users(bot: Bot, update: Update, user: User):
    admins = Session.query(Admin).filter(Admin.admin_group == update.message.chat.id).all()
    users = []
    for admin_user in admins:
        users.append(Session.query(User).filter_by(id=admin_user.user_id).first())
    msg = MSG_LIST_ADMINS_HEADER
    if users is None:
        msg += MSG_EMPTY
    else:
        for user in users:
            msg += MSG_LIST_ADMINS_USER_FORMAT.format(user.username or '',
                                                      user.first_name or '',
                                                      user.last_name or '')

    send_async(bot, chat_id=update.message.chat.id, text=msg)


@command_handler(
    min_permission=AdminType.SUPER,
)
def set_global_admin(bot: Bot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)[1]
    msg = msg.replace('@', '')
    if msg != '':
        user = Session.query(User).filter_by(username=msg).first()
        if user is None:
            send_async(bot,
                       chat_id=update.message.chat.id,
                       text=MSG_USER_UNKNOWN)

        else:
            adm = Session.query(Admin).filter_by(user_id=user.id,
                                                 admin_type=AdminType.FULL.value).first()

            if adm is None:
                new_group_admin = Admin(user_id=user.id,
                                        admin_type=AdminType.FULL.value,
                                        admin_group=0)
                Session.add(new_group_admin)
                Session.commit()
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_NEW_GLOBAL_ADMIN.format(user.username))

            else:
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_NEW_GLOBAL_ADMIN_EXISTS.format(user.username))


@command_handler(
    min_permission=AdminType.SUPER,
)
def set_super_admin(bot: Bot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)[1]
    msg = msg.replace('@', '')
    if msg != '':
        user = Session.query(User).filter_by(username=msg).first()
        if user is None:
            send_async(bot,
                       chat_id=update.message.chat.id,
                       text=MSG_USER_UNKNOWN)

        else:
            if user.id == SUPER_ADMIN_ID and update.message.from_user.id == SUPER_ADMIN_ID:
                adm = Session.query(Admin).filter_by(user_id=user.id, admin_group=0).first()
                if adm is not None:
                    if adm.admin_type == AdminType.SUPER.value:
                        send_async(bot,
                                   chat_id=update.message.chat.id,
                                   text=MSG_NEW_SUPER_ADMIN_EXISTS.format(user.username))

                    else:
                        adm.admin_type = AdminType.SUPER.value
                        Session.add(adm)
                        Session.commit()
                        send_async(bot,
                                   chat_id=update.message.chat.id,
                                   text=MSG_NEW_SUPER_ADMIN.format(user.username))

                else:
                    new_super_admin = Admin(user_id=user.id,
                                            admin_type=AdminType.SUPER.value,
                                            admin_group=0)

                    Session.add(new_super_admin)
                    Session.commit()
                    send_async(bot,
                               chat_id=update.message.chat.id,
                               text=MSG_NEW_SUPER_ADMIN.format(user.username))


@command_handler(
    min_permission=AdminType.SUPER,
)
def del_global_admin(bot: Bot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)[1]
    if msg.find('@') != -1:
        msg = msg.replace('@', '')
        if msg != '':
            user = Session.query(User).filter_by(username=msg).first()
            if user is None:
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_USER_UNKNOWN)

            else:
                adm = Session.query(Admin).filter_by(user_id=user.id,
                                                     admin_type=AdminType.FULL.value).first()

                if adm is None:
                    send_async(bot,
                               chat_id=update.message.chat.id,
                               text=MSG_DEL_GLOBAL_ADMIN_NOT_EXIST.format(user.username))

                else:
                    Session.delete(adm)
                    Session.commit()
                    send_async(bot,
                               chat_id=update.message.chat.id,
                               text=MSG_DEL_GLOBAL_ADMIN.format(user.username))
    else:
        user = Session.query(User).filter_by(id=msg).first()
        if user is None:
            send_async(bot,
                       chat_id=update.message.chat.id,
                       text=MSG_USER_UNKNOWN)

        else:
            adm = Session.query(Admin).filter_by(user_id=user.id,
                                                 admin_type=AdminType.FULL.value).first()
            if adm is None:
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_DEL_GLOBAL_ADMIN_NOT_EXIST.format(user.username))
            else:
                Session.delete(adm)
                Session.commit()
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_DEL_GLOBAL_ADMIN.format(user.username))


@command_handler()
def get_log(bot: Bot, update: Update, user: User):
    if update.message.from_user.id not in LOG_ALLOWED_RECIPIENTS:
        logging.warning("User %s tried to request logs and is not allowed to!", update.message.from_user.id)
        return

    logging.info("User %s requrested logs", update.message.from_user.id)
    if update.message.chat.type == 'private':
        with open(LOGFILE, 'rb') as file:
            bot.send_document(
                chat_id=update.message.chat.id,
                document=file,
                timeout=120 # Logs can be big, so use a bigger timeout...
            )


def delete_admin(bot, update, user, data):
    admin_user = Session.query(User).filter_by(id=data['uid']).first()
    if admin_user:
        del_adm(bot, data['gid'], admin_user)
    msg, inline_markup = generate_group_info(data['gid'])
    bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                        reply_markup=inline_markup)
