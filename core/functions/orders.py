from telegram import Update, Bot
from core.types import AdminType, Admin, admin_allowed, MessageType
from core.utils import send_async
from core.functions.inline_keyboard_handling import generate_order_groups_markup, generate_flag_orders
from core.texts import *


@admin_allowed(adm_type=AdminType.GROUP)
def order(bot: Bot, update: Update, session, chat_data):
    chat_data['order_wait'] = False
    admin_user = session.query(Admin).filter(Admin.user_id == update.message.from_user.id).all()
    markup = generate_order_groups_markup(session, admin_user, chat_data['pin'] if 'pin' in chat_data else True)
    msg = update.message
    if msg.audio:
        chat_data['order'] = msg.audio.file_id
        chat_data['order_type'] = MessageType.AUDIO.value
    elif msg.document:
        chat_data['order'] = msg.document.file_id
        chat_data['order_type'] = MessageType.DOCUMENT.value
    elif msg.voice:
        chat_data['order'] = msg.voice.file_id
        chat_data['order_type'] = MessageType.VOICE.value
    elif msg.sticker:
        chat_data['order'] = msg.sticker.file_id
        chat_data['order_type'] = MessageType.STICKER.value
    elif msg.contact:
        chat_data['order'] = str(msg.contact)
        chat_data['order_type'] = MessageType.CONTACT.value
    elif msg.video:
        chat_data['order'] = msg.video.file_id
        chat_data['order_type'] = MessageType.VIDEO.value
    elif msg.video_note:
        chat_data['order'] = msg.video_note.file_id
        chat_data['order_type'] = MessageType.VIDEO_NOTE.value
    elif msg.location:
        chat_data['order'] = str(msg.location)
        chat_data['order_type'] = MessageType.LOCATION.value
    elif msg.photo:
        chat_data['order'] = msg.photo[-1].file_id
        chat_data['order_type'] = MessageType.PHOTO.value
    else:
        chat_data['order'] = msg.text
        chat_data['order_type'] = MessageType.TEXT.value
    send_async(bot, chat_id=update.message.chat.id, text=MSG_ORDER_SEND_HEADER,
               reply_markup=markup)


@admin_allowed(adm_type=AdminType.GROUP)
def orders(bot: Bot, update: Update, session, chat_data):
    markup = generate_flag_orders()
    chat_data['order_wait'] = True
    send_async(bot, chat_id=update.message.chat.id, text=MSG_FLAG_CHOOSE_HEADER, reply_markup=markup)
