import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from core.bot import MQBot
from core.decorators import command_handler
from core.handler.callback import get_callback_action, CallbackAction
from core.handler.callback.util import create_callback
from core.texts import MSG_GROUP_STATUS_ADMIN_FORMAT, MSG_GROUP_STATUS_DEL_ADMIN, MSG_GROUP_STATUS, MSG_ON, MSG_OFF, \
    MSG_ORDER_GROUP_DEL, MSG_BACK, MSG_GROUP_STATUS_SQUAD, MSG_GROUP_STATUS_CHOOSE_CHAT
from core.types import AdminType, User, Session, Group, Admin, Squad
from core.utils import send_async


@command_handler(
    min_permission=AdminType.FULL
)
def info(bot: MQBot, update: Update, user: User):
    if not update.callback_query:
        logging.warning("group.manage was called without callback!")
        return

    action = get_callback_action(update.callback_query.data, update.effective_user.id)

    group = Session.query(Group).filter(Group.id == action.data['group_id']).first()
    admins = Session.query(Admin).filter(Admin.admin_group == action.data['group_id']).all()

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
                    CallbackAction.ORDER_GROUP_MANAGE,
                    user.id
                    # TODO
                )
            )
        ])

    msg = MSG_GROUP_STATUS.format(
        group.title,
        adm_msg,
        MSG_ON if group.welcome_enabled else MSG_OFF,
        MSG_ON if group.allow_trigger_all else MSG_OFF,
        MSG_ON if group.fwd_minireport else MSG_OFF,
    )
    if len(group.squad):
        msg += MSG_GROUP_STATUS_SQUAD.format(
            MSG_ON if group.squad[0].thorns_enabled else MSG_OFF,
            MSG_ON if group.squad[0].silence_enabled else MSG_OFF,
            MSG_ON if group.squad[0].reminders_enabled else MSG_OFF,
            MSG_ON if group.squad[0].hiring else MSG_OFF,
            MSG_ON if group.squad[0].testing_squad else MSG_OFF,
        )

    adm_del_keys.append([
        InlineKeyboardButton(
            MSG_ORDER_GROUP_DEL,
            callback_data=create_callback(
                CallbackAction.SQUAD_MANAGE,
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
                CallbackAction.ORDER_GROUP_MANAGE,
                user.id
                # TODO
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
def send_status(bot: MQBot, update: Update, user: User):
    msg = MSG_GROUP_STATUS_CHOOSE_CHAT
    groups = Session.query(Group).all()
    inline_keys = []
    for group in groups:
        inline_keys.append(
            InlineKeyboardButton(
                "{}{}".format(
                    '⚜' if group.squad else '🏘️',
                    group.title
                ),
                callback_data=create_callback(
                    CallbackAction.GROUP_INFO,
                    user.id,
                    group_id=group.id
                )
            )
        )
    inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=msg,
        reply_markup=inline_markup,
        parse_mode=ParseMode.HTML,
    )
