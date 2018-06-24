from telegram import Bot, Update

from core.decorators import command_handler
from core.texts import *
from core.types import AdminType, OrderGroup, Session, User
from core.utils import send_async
from functions.inline_keyboard_handling import (generate_group_manage,
                                                generate_groups_manage)

Session()


@command_handler(
    min_permission=AdminType.FULL,
)
def group_list(bot: Bot, update: Update, user: User):
    markup = generate_groups_manage()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_ORDER_GROUP_LIST, reply_markup=markup)


@command_handler(
    min_permission=AdminType.FULL,
)
def add_group(bot: Bot, update: Update, user: User, chat_data):
    chat_data['wait_group_name'] = False
    group = OrderGroup()
    group.name = update.message.text
    Session.add(group)
    Session.commit()
    markup = generate_group_manage(group.id)
    send_async(bot, chat_id=update.message.chat.id,
               text=MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name), reply_markup=markup)
