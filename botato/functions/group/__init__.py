import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, TelegramError

from core.bot import MQBot
from core.decorators import command_handler
from core.handler.callback import get_callback_action, CallbackAction
from core.handler.callback.util import create_callback
from core.texts import *
from core.db import Session
from core.enums import AdminType
from core.model import Group, User, Admin, Squad
from core.utils import send_async
from functions.user import __delete_group_admin


@command_handler(
    min_permission=AdminType.FULL
)
def info(bot: MQBot, update: Update, user: User):
    if not update.callback_query:
        logging.warning("group.manage was called without callback!")
        return

    action = get_callback_action(update.callback_query.data, update.effective_user.id)

    group = Session.query(Group).filter(Group.id == action.data['group_id']).first()
    admins = Session.query(Admin).filter(Admin.group_id == action.data['group_id']).all()

    adm_msg = ''
    adm_del_keys = []
    for adm in admins:
        user = Session.query(User).filter_by(id=adm.user_id).first()
        adm_msg += MSG_GROUP_STATUS_ADMIN_FORMAT.format(
            user.id,
            user.username or '',
            user.first_name or '',
            user.last_name or ''
        )

        adm_del_keys.append([
            InlineKeyboardButton(
                MSG_GROUP_STATUS_DEL_ADMIN.format(user.first_name or '', user.last_name or ''),
                callback_data=create_callback(
                    CallbackAction.GROUP_MANAGE,
                    user.id,
                    sub_action='demote',
                    group_id=group.id,
                    admin_user_id=user.id,
                )
            )
        ])

    msg = MSG_GROUP_STATUS.format(
        group.title,
        adm_msg,
        MSG_ON if group.welcome_enabled else MSG_OFF,
        MSG_ON if group.allow_trigger_all else MSG_OFF,
        MSG_ON if group.fwd_minireport else MSG_OFF,
        MSG_ON if group.thorns_enabled else MSG_OFF,
        MSG_ON if group.silence_enabled else MSG_OFF,
        MSG_ON if group.reminders_enabled else MSG_OFF,

    )
    if len(group.squad):
        msg += MSG_GROUP_STATUS_SQUAD.format(
            MSG_ON if group.squad[0].hiring else MSG_OFF,
            MSG_ON if group.squad[0].testing_squad else MSG_OFF,
        )

    adm_del_keys.append([
        InlineKeyboardButton(
            MSG_ORDER_GROUP_DEL,
            callback_data=create_callback(
                CallbackAction.GROUP_MANAGE,
                user.id,
                sub_action='delete',
                group_id=group.id,
            )
        )
    ])

    adm_del_keys.append([
        InlineKeyboardButton(
            MSG_BACK,
            callback_data=create_callback(
                CallbackAction.GROUP,
                user.id
            )
        )
    ])
    inline_markup = InlineKeyboardMarkup(adm_del_keys)

    bot.edit_message_text(
        msg,
        update.callback_query.message.chat.id,
        update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=inline_markup
    )


@command_handler(
    min_permission=AdminType.FULL,
)
def list(bot: MQBot, update: Update, user: User):
    msg = MSG_GROUP_STATUS_CHOOSE_CHAT
    groups = Session.query(Group).all()
    inline_keys = []
    for group in groups:
        inline_keys.append(
            InlineKeyboardButton(
                "{}{}".format(
                    '⚜' if group.squad else '🏘️',
                    group.title if not group.squad else '{} (Squad: {})'.format(
                        group.title, group.squad[0].squad_name
                    )
                ),
                callback_data=create_callback(
                    CallbackAction.GROUP_INFO,
                    user.id,
                    group_id=group.id
                )
            )
        )
    inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])

    if not update.callback_query:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=msg,
            reply_markup=inline_markup,
            parse_mode=ParseMode.HTML,
        )
    else:
        bot.edit_message_text(
            chat_id=update.callback_query.message.chat.id,
            message_id=update.callback_query.message.message_id,
            text=msg,
            reply_markup=inline_markup,
            parse_mode=ParseMode.HTML,
        )


@command_handler(
    min_permission=AdminType.FULL,
)
def manage(bot: MQBot, update: Update, user: User):
    if not update.callback_query:
        logging.warning("method was called without callback_query!")
        return

    action = get_callback_action(update.callback_query.data, update.effective_user.id)

    if action.data['sub_action'] == "delete":
        # Delete the group, if a squad is associated delete this as well
        squad = Session.query(Squad).filter_by(chat_id=action.data['group_id']).first()
        if squad is not None:
            logging.warning("Deleting squad %s", squad.squad_name)
            bot.send_message(chat_id=action.data['group_id'], text=MSG_SQUAD_DELETE)
            for member in squad.members:
                Session.delete(member)
            Session.delete(squad)
            Session.commit()

        # Now delete the group
        group = Session.query(Group).filter(Group.id == action.data['group_id']).first()
        logging.warning("Deleting group %s", group.title)

        try:
            bot.leave_chat(chat_id=action.data['group_id'])
        except TelegramError:
            pass

        if group:
            Session.delete(group)
            Session.commit()
    elif action.data['sub_action'] == "demote":
        admin_user = Session.query(User).filter(User.id == action.data['admin_user_id']).first()
        if admin_user:
            __delete_group_admin(bot, admin_user, action.data['group_id'])

    list(bot, update, user)
