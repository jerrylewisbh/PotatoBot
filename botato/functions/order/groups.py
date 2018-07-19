import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from core.bot import MQBot
from core.utils import send_async
from core.decorators import command_handler
from core.handler.callback.util import create_callback, CallbackAction, get_callback_action
from core.texts import *
from core.db import Session
from core.enums import AdminType
from core.model import User, OrderGroup, OrderGroupItem, Squad

Session()


@command_handler(
    min_permission=AdminType.FULL,
)
def list(bot: MQBot, update: Update, user: User):
    if update.callback_query:
        action = get_callback_action(update.callback_query.data, update.effective_user.id)
        bot.edit_message_text(
            MSG_ORDER_GROUP_LIST,
            update.callback_query.message.chat.id,
            update.callback_query.message.message_id,
            reply_markup=__get_group_list_keyboard(user)
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
def add(bot: MQBot, update: Update, user: User, chat_data):
    if "wait_group_name" in chat_data and not chat_data["wait_group_name"] or "wait_group_name" not in chat_data:
        chat_data["wait_group_name"] = True
        send_async(
            bot,
            chat_id=user.id,
            text=MSG_ORDER_GROUP_NEW,
        )
    elif "wait_group_name" in chat_data:
        chat_data['wait_group_name'] = False

        group = OrderGroup()
        group.name = update.message.text
        Session.add(group)
        Session.commit()

        markup = __get_group_manage_keyboard(user, group.id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name),
            reply_markup=markup
        )


def __delete(order_group_id):
    group = Session.query(OrderGroup).filter_by(id=order_group_id).first()
    Session.delete(group)
    Session.commit()


def __toggle_chat(chat_id, order_group_id):
    group_item = Session.query(OrderGroupItem).filter(
        OrderGroupItem.group_id == order_group_id,
        OrderGroupItem.chat_id == chat_id
    ).first()

    if not group_item:
        item = OrderGroupItem()
        item.group_id = order_group_id
        item.chat_id = chat_id
        Session.add(item)
        Session.commit()
    else:
        Session.delete(group_item)
        Session.commit()


@command_handler(
    min_permission=AdminType.FULL,
)
def manage(bot, update, user):
    if not update.callback_query:
        logging.warning("group.manage was called without callback!")
        return
    action = get_callback_action(update.callback_query.data, update.effective_user.id)
    group = Session.query(OrderGroup).filter_by(id=action.data['order_group_id']).first()

    if "sub_action" in action.data:
        if action.data['sub_action'] == "toggle":
            __toggle_chat(action.data['squad_chat_id'], action.data['order_group_id'])
        elif action.data['sub_action'] == "delete":
            __delete(action.data['order_group_id'])
            list(bot, update, user)
            return

    markup = __get_group_manage_keyboard(user, action.data['order_group_id'])
    bot.edit_message_text(
        MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name),
        update.callback_query.message.chat.id,
        update.callback_query.message.message_id,
        reply_markup=markup
    )


def __get_group_manage_keyboard(user: User, order_group_id):
    squads = Session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        in_group = False
        for item in squad.chat.group_items:
            if item.group_id == order_group_id:
                in_group = True
                break
        inline_keys.append([
            InlineKeyboardButton(
                (MSG_SYMBOL_ON if in_group else MSG_SYMBOL_OFF) + squad.squad_name,
                callback_data=create_callback(
                    CallbackAction.ORDER_GROUP_MANAGE,
                    user.id,
                    sub_action="toggle",
                    squad_chat_id=squad.chat_id,
                    order_group_id=order_group_id
                )
            )
        ])

    inline_keys.append([
        InlineKeyboardButton(
            MSG_ORDER_GROUP_DEL,
            callback_data=create_callback(
                CallbackAction.ORDER_GROUP_MANAGE,
                user.id,
                sub_action="delete",
                order_group_id=order_group_id
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
                CallbackAction.ORDER_GROUP_MANAGE,
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
