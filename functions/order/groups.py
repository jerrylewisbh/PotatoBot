import json

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from core.decorators import command_handler
from core.enums import Icons, Castle
from core.handler.callback.util import create_callback, CallbackAction, get_callback_action
from core.texts import *
from core.types import AdminType, OrderGroup, Session, User, OrderGroupItem, MessageType, Admin, Group, Squad
from core.utils import send_async
from functions.inline_markup import QueryType

Session()


@command_handler(
    min_permission=AdminType.FULL,
)
def list(bot: Bot, update: Update, user: User):
    if update.callback_query:
        action = get_callback_action(update.callback_query.data, update.effective_user.id)
        bot.edit_message_text(
            MSG_ORDER_GROUP_LIST,
            update.callback_query.message.chat.id,
            update.callback_query.message.message_id,
        )
    else:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=MSG_ORDER_GROUP_LIST,
            reply_markup=__get_group_list_keyboard(user)
        )


@command_handler(
    min_permission=AdminType.FULL,
)
def add(bot: Bot, update: Update, user: User, chat_data):
    chat_data['wait_group_name'] = False
    group = OrderGroup()
    group.name = update.message.text
    Session.add(group)
    Session.commit()

    markup = __get_group_manage_memberships(user, group.id)
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name),
        reply_markup=markup
    )


def order_group_delete(bot, update, user, data):
    group = Session.query(OrderGroup).filter_by(id=data['id']).first()
    Session.delete(group)
    Session.commit()
    bot.edit_message_text(
        MSG_ORDER_GROUP_LIST,
        update.callback_query.message.chat.id,
        update.callback_query.message.message_id,
        reply_markup=__get_group_list_keyboard(user)
    )


def order_group_add(bot: Bot, update: Update, user: User, data: dict, chat_data: dict):
    chat_data['wait_group_name'] = True
    send_async(bot, chat_id=update.callback_query.message.chat.id,
               text=MSG_ORDER_GROUP_NEW)


def order_group_tirgger_chat(bot, update, user, data):
    group = Session.query(OrderGroup).filter_by(id=data['id']).first()
    deleted = False
    for item in group.items:
        if item.chat_id == data['c']:
            Session.delete(item)
            Session.commit()
            deleted = True
    if not deleted:
        item = OrderGroupItem()
        item.group_id = group.id
        item.chat_id = data['c']
        Session.add(item)
        Session.commit()
    markup = __get_group_manage_memberships(user, data['id'])
    bot.edit_message_text(MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=markup)


def order_group_manage(bot, update, user, data):
    group = Session.query(OrderGroup).filter_by(id=data['id']).first()
    markup = __get_group_manage_memberships(user, data['id'])
    bot.edit_message_text(MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=markup)


def order_group(bot: Bot, update: Update, user: User, data: dict, chat_data: dict):
    chat_data['order_wait'] = False
    if 'txt' in data and len(data['txt']):
        chat_data['order_type'] = MessageType.TEXT
        if data['txt'] == Icons.LES.value:
            chat_data['order'] = Castle.LES.value
        elif data['txt'] == Icons.GORY.value:
            chat_data['order'] = Castle.GORY.value
        elif data['txt'] == Icons.SEA.value:
            chat_data['order'] = Castle.SEA.value
        else:
            chat_data['order'] = data['txt']
    admin_user = Session.query(Admin).filter(Admin.user_id == update.callback_query.from_user.id).all()
    markup = generate_order_groups_markup(admin_user, chat_data['pin'] if 'pin' in chat_data else True,
                                          chat_data['btn'] if 'btn' in chat_data else True)
    bot.edit_message_text(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=markup)


def group_info(bot, update, user, data):
    msg, inline_markup = generate_group_info(data['id'])
    bot.edit_message_text(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                        reply_markup=inline_markup)


def generate_group_info(group_id):
    group = Session.query(Group).filter(Group.id == group_id).first()
    admins = Session.query(Admin).filter(Admin.admin_group == group_id).all()
    adm_msg = ''
    adm_del_keys = []
    for adm in admins:
        user = Session.query(User).filter_by(id=adm.user_id).first()
        adm_msg += MSG_GROUP_STATUS_ADMIN_FORMAT.\
            format(user.id, user.username or '', user.first_name or '', user.last_name or '')
        adm_del_keys.append([InlineKeyboardButton(MSG_GROUP_STATUS_DEL_ADMIN.
                                                  format(user.first_name or '', user.last_name or ''),
                                                  callback_data=json.dumps(
                                                      {'t': QueryType.DelAdm.value, 'uid': user.id,
                                                       'gid': group_id}))])
    msg = MSG_GROUP_STATUS.format(group.title,
                                  adm_msg,
                                  MSG_ON if group.welcome_enabled else MSG_OFF,
                                  MSG_ON if group.allow_trigger_all else MSG_OFF,
                                  MSG_ON if len(group.squad) and group.squad[0].thorns_enabled else MSG_OFF)

    adm_del_keys.append(
        [InlineKeyboardButton(MSG_ORDER_GROUP_DEL, callback_data=json.dumps(
        {'t': QueryType.GroupDelete.value, 'gid': group_id}))])

    adm_del_keys.append(
        [InlineKeyboardButton(MSG_BACK, callback_data=create_callback("foo"))]
    )
    inline_markup = InlineKeyboardMarkup(adm_del_keys)
    return msg, inline_markup


def generate_order_groups_markup(admin_user: list=None, pin: bool=True, btn=True):
    if admin_user:
        group_adm = True
        for adm in admin_user:
            if adm.admin_type < AdminType.GROUP.value:
                group_adm = False
                break
        if group_adm:
            inline_keys = []
            for adm in admin_user:
                group = Session.query(Group).filter_by(id=adm.admin_group, bot_in_group=True).first()
                if group:
                    inline_keys.append([InlineKeyboardButton(group.title, callback_data=json.dumps(
                        {'t': QueryType.Order.value, 'g': False, 'id': group.id}))])
            inline_keys.append(
                [InlineKeyboardButton(MSG_ORDER_PIN if pin else MSG_ORDER_NO_PIN, callback_data=json.dumps(
                    {'t': QueryType.TriggerOrderPin.value, 'g': True}))])
            inline_keys.append(
                [InlineKeyboardButton(MSG_ORDER_BUTTON if btn else MSG_ORDER_NO_BUTTON, callback_data=json.dumps(
                    {'t': QueryType.TriggerOrderButton.value, 'g': True}))])
            inline_markup = InlineKeyboardMarkup(inline_keys)
            return inline_markup
        else:
            groups = Session.query(OrderGroup).all()
            inline_keys = []
            for group in groups:
                inline_keys.append([InlineKeyboardButton(group.name, callback_data=json.dumps(
                    {'t': QueryType.Order.value, 'g': True, 'id': group.id}))])
            inline_keys.append([InlineKeyboardButton(MSG_ORDER_TO_SQUADS, callback_data=json.dumps(
                {'t': QueryType.Orders.value}))])
            inline_keys.append([InlineKeyboardButton(MSG_ORDER_PIN if pin else MSG_ORDER_NO_PIN,
                                                     callback_data=json.dumps(
                                                         {'t': QueryType.TriggerOrderPin.value, 'g': True}))])
            inline_keys.append([InlineKeyboardButton(MSG_ORDER_BUTTON if btn else MSG_ORDER_NO_BUTTON,
                                                     callback_data=json.dumps(
                                                         {'t': QueryType.TriggerOrderButton.value, 'g': True}))])
            inline_markup = InlineKeyboardMarkup(inline_keys)
            return inline_markup


def __get_group_manage_memberships(user: User, group_id):
    squads = Session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        in_group = False
        for item in squad.chat.group_items:
            if item.group_id == group_id:
                in_group = True
                break
        inline_keys.append([
            InlineKeyboardButton(
                (MSG_SYMBOL_ON if in_group else MSG_SYMBOL_OFF) + squad.squad_name,
                callback_data=create_callback(
                    CallbackAction.ORDER_GROUP_MANAGE,
                    user.id,
                    action="toggle",
                    squad_id=squad.chat_id
                )
            )
        ])

    inline_keys.append([
        InlineKeyboardButton(
            MSG_ORDER_GROUP_DEL,
            callback_data=create_callback(
                CallbackAction.ORDER_GROUP_MANAGE,
                user.id,
                action="delete"
            )
        )
    ])
    inline_keys.append([
        InlineKeyboardButton(
            MSG_BACK,
            callback_data=create_callback(
                CallbackAction.ORDER_GROUP,
                user.id
            )
        )
    ])
    return InlineKeyboardMarkup(inline_keys)


def __get_group_list_keyboard(user: User):
    groups = Session.query(OrderGroup).all()
    inline_keys = []
    for group in groups:
        inline_keys.append([
            InlineKeyboardButton(group.name, callback_data=create_callback(
                CallbackAction.ORDER_GROUP,
                user.id,
                order_group_id=group.id)
            )
        ])
    inline_keys.append([
        InlineKeyboardButton(MSG_ORDER_GROUP_ADD, callback_data=create_callback(
            CallbackAction.ORDER_GROUP_ADD,
            user.id)
        )
    ])
    return InlineKeyboardMarkup(inline_keys)
