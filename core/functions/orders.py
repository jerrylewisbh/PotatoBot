from telegram import Update, Bot
from core.types import User, AdminType, Admin, admin, session
from core.utils import send_async
from core.functions.inline_keyboard_handling import generate_order_groups_markup, generate_flag_orders


@admin()
def order(bot: Bot, update: Update, chat_data):
    markup = generate_order_groups_markup(bot, update.message.text)
    chat_data['order'] = update.message.text
    send_async(bot, chat_id=update.message.chat.id, text='Приказ: {}\nКуда слать?'.format(chat_data['order']),
               reply_markup=markup)


@admin()
def orders(bot: Bot, update: Update, chat_data):
    markup = generate_flag_orders()
    send_async(bot, chat_id=update.message.chat.id, text='Выбирай', reply_markup=markup)
