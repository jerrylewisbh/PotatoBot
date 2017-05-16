from telegram import Update, Bot
from core.types import User, AdminType, Admin, admin, session
from core.utils import send_async
from core.functions.inline_keyboard_handling import generate_order_group_markup


@admin()
def order(bot: Bot, update: Update, chat_data):
    markup = generate_order_group_markup()
    chat_data['order'] = update.message.text
    send_async(bot, chat_id=update.message.chat.id, text='Куда слать?', reply_markup=markup)
