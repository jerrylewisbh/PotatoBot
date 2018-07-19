import logging
from telegram.error import Unauthorized
from telegram import ReplyMarkup, TelegramError
from telegram.ext import run_async

from core.bot import MQBot
from core.enums import MessageType



class OrderDraft(object):
    def __init__(self):
        self.type = MessageType.TEXT
        self.order = None
        self.pin = True
        self.button = False


@run_async
def __send_order(bot: MQBot, order: OrderDraft, chat_id: int, markup: ReplyMarkup):
    logging.info(
        "send_order(bot='%s', text='%s', message_type='%s', chat_id='%s', markup='%s', pin=%s)",
        bot,
        order.order,
        order.type,
        chat_id,
        markup,
        order.pin
    )
    try:
        msg_sent = None
        if order.type == MessageType.AUDIO.value:
            msg_sent = bot.send_audio(chat_id, order.order, reply_markup=markup)
        elif order.type == MessageType.DOCUMENT.value:
            msg_sent = bot.send_document(chat_id, order.order, reply_markup=markup)
        elif order.type == MessageType.VOICE.value:
            msg_sent = bot.send_voice(chat_id, order.order, reply_markup=markup)
        elif order.type == MessageType.STICKER.value:
            msg_sent = bot.send_sticker(chat_id, order.order, reply_markup=markup)
        elif order.type == MessageType.CONTACT.value:
            msg = order.order.replace('\'', '"')
            logging.warning("TODO: SEND CONTACT")
            return
            if 'phone_number' not in contact.keys():
                contact['phone_number'] = None
            if 'first_name' not in contact.keys():
                contact['first_name'] = None
            if 'last_name' not in contact.keys():
                contact['last_name'] = None
                msg_sent = bot.send_contact(
                    chat_id, contact['phone_number'],
                    contact['first_name'],
                    contact['last_name'],
                    reply_markup=markup
                )
        elif order.type == MessageType.VIDEO.value:
            msg_sent = bot.send_video(chat_id, order.order, reply_markup=markup)
        elif order.type == MessageType.VIDEO_NOTE.value:
            msg_sent = bot.send_video_note(chat_id, order.order, reply_markup=markup)
        elif order.type == MessageType.LOCATION.value:
            msg = order.order.replace('\'', '"')
            #location = loads(msg)
            logging.warning("TODO: SEND LOCATION")
            return
            #msg_sent = bot.send_location(chat_id, location['latitude'], location['longitude'], reply_markup=markup)
        elif order.type == MessageType.PHOTO.value:
            msg_sent = bot.send_photo(chat_id, order.order, reply_markup=markup)
        else:
            logging.info("Sending Order")
            msg_sent = bot.send_message(
                chat_id=chat_id,
                text=order.order,
                disable_web_page_preview=True,
                reply_markup=markup
            )

        if order.pin:
            msg_result = msg_sent.result()
            # If it got send... Pin it
            if msg_result:
                try:
                    logging.info("Pinning for message_id='%s'", msg_result.message_id)
                    bot.pin_chat_message(
                        chat_id=chat_id,
                        message_id=msg_result.message_id,
                        disable_notification=False,
                    )
                except Unauthorized:
                    logging.warning("I'm not allowed to pin message in chat_id='%s'", chat_id)

        logging.info(
            "END send_order(bot='%s', text='%s', message_type='%s', chat_id='%s', markup='%s', pin=%s)",
            bot,
            order.order,
            order.type,
            chat_id,
            markup,
            order.pin
        )
        return msg_sent
    except TelegramError as err:
        logging.error(err.message)
        return None
