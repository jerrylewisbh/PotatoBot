import logging

from config import SUPER_ADMIN_ID, LOGFILE

# from core.texts import *
from core.texts import (MSG_DEL_GLOBAL_ADMIN, MSG_DEL_GLOBAL_ADMIN_NOT_EXIST,
                        MSG_DEL_GROUP_ADMIN, MSG_DEL_GROUP_ADMIN_NOT_EXIST,
                        MSG_EMPTY, MSG_LIST_ADMINS_FORMAT,
                        MSG_LIST_ADMINS_HEADER, MSG_LIST_ADMINS_USER_FORMAT,
                        MSG_NEW_GLOBAL_ADMIN, MSG_NEW_GLOBAL_ADMIN_EXISTS,
                        MSG_NEW_GROUP_ADMIN, MSG_NEW_GROUP_ADMIN_EXISTS,
                        MSG_NEW_SUPER_ADMIN, MSG_NEW_SUPER_ADMIN_EXISTS,
                        MSG_USER_UNKNOWN)
from core.types import Admin, AdminType, User, Session
from core.decorators import admin_allowed, user_allowed
from core.utils import send_async
from telegram import Bot, Update

Session()

@admin_allowed()
def set_admin(bot: Bot, update: Update):
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


@admin_allowed()
def del_admin(bot: Bot, update: Update):
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


@admin_allowed()
def list_admins(bot: Bot, update: Update):
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


@user_allowed
def admins_for_users(bot: Bot, update: Update):
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


@admin_allowed(adm_type=AdminType.SUPER)
def set_global_admin(bot: Bot, update: Update):
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


@user_allowed(False)
def set_super_admin(bot: Bot, update: Update):
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


@admin_allowed(adm_type=AdminType.SUPER)
def del_global_admin(bot: Bot, update: Update):
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


@user_allowed(False)
def get_log(bot: Bot, update: Update):
    # Fixme: Decorator "@admin_allowed(adm_type=AdminType.SUPER)" instead of other check... But this is NYI
    if update.message.from_user.id != SUPER_ADMIN_ID:
        logging.info("User %s tried to request logs and is not allowed to!", update.message.from_user.id)
        return

    logging.info("User %s requrested logs", update.message.from_user.id)
    if update.message.chat.type == 'private':
        with open(LOGFILE, 'rb') as file:
            bot.send_document(
                chat_id = update.message.chat.id,
                document = file
            )
