import logging
from telegram import Update

from config import SUPER_ADMIN_ID
from core.bot import MQBot
from core.decorators import command_handler
from core.handler.callback import get_callback_action
from core.texts import MSG_USER_UNKNOWN, MSG_NEW_GROUP_ADMIN, \
    MSG_NEW_GROUP_ADMIN_EXISTS, MSG_LIST_ADMINS_HEADER, \
    MSG_LIST_ADMINS_FORMAT, MSG_EMPTY, MSG_LIST_ADMINS_USER_FORMAT, MSG_NEW_GLOBAL_ADMIN, MSG_NEW_GLOBAL_ADMIN_EXISTS, \
    MSG_NEW_SUPER_ADMIN_EXISTS, MSG_NEW_SUPER_ADMIN, MSG_DEL_GLOBAL_ADMIN_NOT_EXIST, MSG_DEL_GLOBAL_ADMIN, \
    MSG_DEL_GROUP_ADMIN, MSG_DEL_GROUP_ADMIN_NOT_EXIST
from core.types import Session, User, AdminType, Admin
from core.utils import send_async
from functions.user.util import send_settings, __toggle_gold_hiding, __toggle_sniping, __toggle_deal_report, \
    __toggle_report, \
    __disable_api


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True
)
def set_admin(bot: MQBot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)[1]
    msg = msg.replace('@', '')
    if msg != '':
        user = Session.query(User).filter_by(username=msg).first()
        if user is None:
            send_async(
                bot,
                chat_id=update.message.chat.id,
                text=MSG_USER_UNKNOWN
            )

        else:
            adm = Session.query(Admin).filter_by(user_id=user.id,
                                                 group_id=update.message.chat.id).first()

            if adm is None:
                new_group_admin = Admin(user_id=user.id,
                                        admin_type=AdminType.GROUP.value,
                                        group_id=update.message.chat.id)

                Session.add(new_group_admin)
                Session.commit()
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_NEW_GROUP_ADMIN.format(user.username))

            else:
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_NEW_GROUP_ADMIN_EXISTS.format(user.username))


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True
)
def del_admin(bot: MQBot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)[1]
    if msg.find('@') != -1:
        msg = msg.replace('@', '')
        if msg != '':
            user = Session.query(User).filter_by(username=msg).first()
            if user is None:
                send_async(
                    bot,
                    chat_id=update.message.chat.id,
                    text=MSG_USER_UNKNOWN
                )

            else:
                adm = Session.query(Admin).filter_by(
                    user_id=user.id,
                    group_id=update.message.chat.id
                ).first()

                if adm is None:
                    send_async(
                        bot,
                        chat_id=update.message.chat.id,
                        text=MSG_DEL_GROUP_ADMIN_NOT_EXIST.format(user.username)
                    )

                else:
                    Session.delete(adm)
                    Session.commit()
                    send_async(
                        bot,
                        chat_id=update.message.chat.id,
                        text=MSG_DEL_GROUP_ADMIN.format(user.username)
                    )
    else:
        user = Session.query(User).filter_by(id=msg).first()
        if user is None:
            send_async(
                bot,
                chat_id=update.message.chat.id,
                text=MSG_USER_UNKNOWN
            )

        else:
            adm = Session.query(Admin).filter_by(
                user_id=user.id,
                group_id=update.message.chat.id
            ).first()

            if adm is None:
                send_async(
                    bot,
                    chat_id=update.message.chat.id,
                    text=MSG_DEL_GROUP_ADMIN_NOT_EXIST.format(user.username)
                )

            else:
                Session.delete(adm)
                Session.commit()
                send_async(
                    bot,
                    chat_id=update.message.chat.id,
                    text=MSG_DEL_GROUP_ADMIN.format(user.username)
                )


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=True,
    allow_group=True
)
def list_admins(bot: MQBot, update: Update, user: User):
    admins = Session.query(Admin).filter(Admin.group_id == update.message.chat.id).all()
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
    allow_group=True,
    allow_private=False,
    allow_group=True
)
def admins_for_users(bot: MQBot, update: Update, user: User):
    admins = Session.query(Admin).filter(Admin.group_id == update.message.chat.id).all()
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
def set_global_admin(bot: MQBot, update: Update, user: User):
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
                                        group_id=None)
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
def set_super_admin(bot: MQBot, update: Update, user: User):
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
                adm = Session.query(Admin).filter_by(user_id=user.id, group_id=None).first()
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
                                            group_id=None)

                    Session.add(new_super_admin)
                    Session.commit()
                    send_async(bot,
                               chat_id=update.message.chat.id,
                               text=MSG_NEW_SUPER_ADMIN.format(user.username))


@command_handler(
    min_permission=AdminType.SUPER,
)
def del_global_admin(bot: MQBot, update: Update, user: User):
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
            send_async(
                bot,
                chat_id=update.message.chat.id,
                text=MSG_USER_UNKNOWN
            )

        else:
            adm = Session.query(Admin).filter_by(user_id=user.id,
                                                 admin_type=AdminType.FULL.value).first()
            if adm is None:
                send_async(
                    bot,
                    chat_id=update.message.chat.id,
                    text=MSG_DEL_GLOBAL_ADMIN_NOT_EXIST.format(user.username)
                )
            else:
                Session.delete(adm)
                Session.commit()
                send_async(
                    bot,
                    chat_id=update.message.chat.id,
                    text=MSG_DEL_GLOBAL_ADMIN.format(user.username)
                )


@command_handler()
def settings(bot: MQBot, update: Update, user: User):
    if not update.callback_query:
        send_settings(bot, update, user)
    else:
        action = get_callback_action(update.callback_query.data, user.id)
        if action.data["setting_action"] == "disable_api":
            __disable_api(bot, update, user)
        elif action.data["setting_action"] == "report":
            __toggle_report(bot, update, user)
        elif action.data["setting_action"] == "deal_report":
            __toggle_deal_report(bot, update, user)
        elif action.data["setting_action"] == "sniping":
            __toggle_sniping(bot, update, user)
        elif action.data["setting_action"] == "hiding":
            __toggle_gold_hiding(bot, update, user)
        else:
            logging.warning("Unknown setting_action for settings")


def __delete_group_admin(bot: MQBot, user: User, chat_id):
    adm = Session.query(Admin).filter(User.id == user.id, Admin.group_id == chat_id).first()

    if adm is None:
        send_async(
            bot,
            chat_id=chat_id,
            text=MSG_DEL_GROUP_ADMIN_NOT_EXIST.format(user.username)
        )

    else:
        Session.delete(adm)
        Session.commit()
        send_async(
            bot,
            chat_id=chat_id,
            text=MSG_DEL_GROUP_ADMIN.format(user.username)
        )
