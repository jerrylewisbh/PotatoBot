import logging
from telegram.error import Unauthorized, BadRequest, TimedOut
from telegram import ReplyMarkup, TelegramError
from telegram.ext import run_async

from core.bot import MQBot
from core.db import Session
from core.enums import MessageType
from core.model import Group
from core.utils import disable_group


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

            try:
                msg_sent = bot.send_message(
                    chat_id=chat_id,
                    text=order.order,
                    disable_web_page_preview=True,
                    reply_markup=markup
                )
            except TimedOut as ex:
                logging.warning("Giving order timed out. Retry!")
                msg_sent = bot.send_message(
                    chat_id=chat_id,
                    text=order.order,
                    disable_web_page_preview=True,
                    reply_markup=markup
                )
            except BadRequest as ex:
                if ex.message == "Chat not found":
                    logging.warning(
                        "Chat for group_id='%s' not found: %s",
                        chat_id,
                        ex.message
                    )
                    group = Session.query(Group).filter(Group.id == chat_id).first()
                    if group:
                        disable_group(group)
                else:
                    logging.warning(
                        "Can't send order into group_id='%s'. Message: %s",
                        chat_id,
                        ex.message
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
                except BadRequest as ex:
                    if ex.message == "Chat not found":
                        logging.warning(
                            "Chat for group_id='%s' not found: %s",
                            chat_id,
                            ex.message
                        )
                        group = Session.query(Group).filter(Group.id == chat_id).first()
                        if group:
                            disable_group(group)
                    else:
                        logging.warning(
                            "Can't send order into group_id='%s'. Message: %s",
                            chat_id,
                            ex.message
                        )

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
