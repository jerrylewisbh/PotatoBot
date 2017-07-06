from telegram import Update, Bot
from core.types import User, AdminType, Admin, admin, session
from core.utils import send_async
from core.functions.inline_keyboard_handling import generate_order_groups_markup, generate_flag_orders
from core.texts import *


@admin(adm_type=AdminType.GROUP)
def order(bot: Bot, update: Update, chat_data):
    admin_user = session.query(Admin).filter(Admin.user_id == update.message.from_user.id).all()
    markup = generate_order_groups_markup(bot, admin_user)
    chat_data['order'] = update.message.text
    send_async(bot, chat_id=update.message.chat.id, text=MSG_ORDER_SEND_HEADER.format(chat_data['order']),
               reply_markup=markup)


@admin(adm_type=AdminType.GROUP)
def orders(bot: Bot, update: Update, chat_data):
    markup = generate_flag_orders()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_FLAG_CHOOSE_HEADER, reply_markup=markup)
