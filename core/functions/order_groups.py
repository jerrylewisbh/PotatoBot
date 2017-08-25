from telegram import Update, Bot
from core.types import Session, OrderGroup
from core.utils import send_async
from core.functions.inline_keyboard_handling import generate_groups_manage, generate_group_manage
from core.texts import *


def group_list(bot: Bot, update: Update):
    markup = generate_groups_manage()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_ORDER_GROUP_LIST, reply_markup=markup)


def add_group(bot: Bot, update: Update, chat_data):
    session = Session()
    chat_data['wait_group_name'] = False
    group = OrderGroup()
    group.name = update.message.text
    session.add(group)
    session.commit()
    markup = generate_group_manage(group.id)
    send_async(bot, chat_id=update.message.chat.id,
               text=MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name), reply_markup=markup)
