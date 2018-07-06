import logging
from telegram import Bot, ReplyMarkup, TelegramError
from telegram.ext import run_async

from core.types import MessageType


@run_async
def __send_order(bot: Bot, text: str, message_type: MessageType, chat_id: int, markup: ReplyMarkup, pin: bool = False):
    logging.info(
        "send_order(bot='%s', text='%s', message_type='%s', chat_id='%s', markup='%s', pin=%s)",
        bot,
        text,
        message_type,
        chat_id,
        markup,
        pin
    )
    try:
        msg_sent = None
        if message_type == MessageType.AUDIO.value:
            msg_sent = bot.send_audio(chat_id, text, reply_markup=markup)
        elif message_type == MessageType.DOCUMENT.value:
            msg_sent = bot.send_document(chat_id, text, reply_markup=markup)
        elif message_type == MessageType.VOICE.value:
            msg_sent = bot.send_voice(chat_id, text, reply_markup=markup)
        elif message_type == MessageType.STICKER.value:
            msg_sent = bot.send_sticker(chat_id, text, reply_markup=markup)
        elif message_type == MessageType.CONTACT.value:
            msg = text.replace('\'', '"')
            contact = loads(msg)
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
        elif message_type == MessageType.VIDEO.value:
            msg_sent = bot.send_video(chat_id, text, reply_markup=markup)
        elif message_type == MessageType.VIDEO_NOTE.value:
            msg_sent = bot.send_video_note(chat_id, text, reply_markup=markup)
        elif message_type == MessageType.LOCATION.value:
            msg = text.replace('\'', '"')
            location = loads(msg)
            msg_sent = bot.send_location(chat_id, location['latitude'], location['longitude'], reply_markup=markup)
        elif message_type == MessageType.PHOTO.value:
            msg_sent = bot.send_photo(chat_id, text, reply_markup=markup)
        else:
            logging.info("SEND ORDER")
            msg_sent = bot.send_message(
                chat_id=chat_id,
                text=text,
                disable_web_page_preview=True,
                reply_markup=markup
            )

        if pin:
            msg_result = msg_sent.result()
            logging.info("Pinning for message_id='%s'", msg_result.message_id)
            bot.pin_chat_message(
                chat_id=chat_id,
                message_id=msg_result.message_id,
                disable_notification=False,
            )

        logging.info(
            "END send_order(bot='%s', text='%s', message_type='%s', chat_id='%s', markup='%s', pin=%s)",
            bot,
            text,
            message_type,
            chat_id,
            markup,
            pin
        )
        return msg_sent
    except TelegramError as err:
        bot.logger.error(err.message)
        return None
