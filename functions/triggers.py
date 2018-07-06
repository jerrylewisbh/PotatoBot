from html import escape
from json import loads
from telegram import Message, ParseMode, Update

from core.bot import MQBot
from core.decorators import command_handler
from core.texts import *
from core.types import (AdminType, LocalTrigger, MessageType, Session, Trigger,
                        check_admin, User)
from core.utils import send_async, update_group

Session()


def trigger_decorator(func):
    @command_handler(
        allow_group=True
    )
    def wrapper(bot, update, *args, **kwargs):
        group = update_group(update.message.chat)
        if group is None and \
                check_admin(update, AdminType.FULL) or \
                group is not None and \
                (group.allow_trigger_all or
                 check_admin(update, AdminType.GROUP)):
            func(bot, update, *args, **kwargs)
    return wrapper


def add_global_trigger_db(msg: Message, trigger_text: str):
    trigger = Session.query(Trigger).filter_by(trigger=trigger_text).first()
    if trigger is None:
        trigger = Trigger()
        trigger.trigger = trigger_text
    if msg.audio:
        trigger.message = msg.audio.file_id
        trigger.message_type = MessageType.AUDIO.value
    elif msg.document:
        trigger.message = msg.document.file_id
        trigger.message_type = MessageType.DOCUMENT.value
    elif msg.voice:
        trigger.message = msg.voice.file_id
        trigger.message_type = MessageType.VOICE.value
    elif msg.sticker:
        trigger.message = msg.sticker.file_id
        trigger.message_type = MessageType.STICKER.value
    elif msg.contact:
        trigger.message = str(msg.contact)
        trigger.message_type = MessageType.CONTACT.value
    elif msg.video:
        trigger.message = msg.video.file_id
        trigger.message_type = MessageType.VIDEO.value
    elif msg.video_note:
        trigger.message = msg.video_note.file_id
        trigger.message_type = MessageType.VIDEO_NOTE.value
    elif msg.location:
        trigger.message = str(msg.location)
        trigger.message_type = MessageType.LOCATION.value
    elif msg.photo:
        trigger.message = msg.photo[-1].file_id
        trigger.message_type = MessageType.PHOTO.value
    else:
        trigger.message = msg.text
        trigger.message_type = MessageType.TEXT.value
    Session.add(trigger)
    Session.commit()


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True,
)
def set_global_trigger(bot: MQBot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)
    if len(msg) == 2 and len(msg[1]) > 0 and update.message.reply_to_message:
        trigger = msg[1].strip()
        data = update.message.reply_to_message
        add_global_trigger_db(data, trigger)
        send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_NEW.format(trigger))
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_NEW_ERROR)


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True,
)
def add_global_trigger(bot: MQBot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)
    if len(msg) == 2 and len(msg[1]) > 0 and update.message.reply_to_message:
        trigger_text = msg[1].strip()
        trigger = Session.query(Trigger).filter_by(trigger=trigger_text).first()
        if trigger is None:
            data = update.message.reply_to_message
            add_global_trigger_db(data, trigger_text)
            send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_NEW.format(trigger_text))
        else:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_EXISTS.format(trigger_text))
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_NEW_ERROR)


@trigger_decorator
def trigger_show(bot: MQBot, update: Update, user: User):
    trigger = Session.query(LocalTrigger).filter_by(chat_id=update.message.chat.id, trigger=update.message.text).first()
    if trigger is None:
        trigger = Session.query(Trigger).filter_by(trigger=update.message.text).first()
    if trigger is not None:
        if trigger.message_type == MessageType.AUDIO.value:
            bot.send_audio(update.message.chat.id, trigger.message)
        elif trigger.message_type == MessageType.DOCUMENT.value:
            bot.send_document(update.message.chat.id, trigger.message)
        elif trigger.message_type == MessageType.VOICE.value:
            bot.send_voice(update.message.chat.id, trigger.message)
        elif trigger.message_type == MessageType.STICKER.value:
            bot.send_sticker(update.message.chat.id, trigger.message)
        elif trigger.message_type == MessageType.CONTACT.value:
            msg = trigger.message.replace('\'', '"')
            contact = loads(msg)
            if 'phone_number' not in contact.keys():
                contact['phone_number'] = None
            if 'first_name' not in contact.keys():
                contact['first_name'] = None
            if 'last_name' not in contact.keys():
                contact['last_name'] = None
            bot.send_contact(update.message.chat.id,
                             contact['phone_number'],
                             contact['first_name'],
                             contact['last_name'])
        elif trigger.message_type == MessageType.VIDEO.value:
            bot.send_video(update.message.chat.id, trigger.message)
        elif trigger.message_type == MessageType.VIDEO_NOTE.value:
            bot.send_video_note(update.message.chat.id, trigger.message)
        elif trigger.message_type == MessageType.LOCATION.value:
            msg = trigger.message.replace('\'', '"')
            location = loads(msg)
            bot.send_location(update.message.chat.id, location['latitude'], location['longitude'])
        elif trigger.message_type == MessageType.PHOTO.value:
            bot.send_photo(update.message.chat.id, trigger.message)
        else:
            send_async(bot, chat_id=update.message.chat.id, text=trigger.message, disable_web_page_preview=True)


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True
)
def del_global_trigger(bot: MQBot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)[1]
    trigger = Session.query(Trigger).filter_by(trigger=msg).first()
    if trigger is not None:
        Session.delete(trigger)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_DEL.format(msg))
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_DEL_ERROR)


@trigger_decorator
def list_triggers(bot: MQBot, update: Update, user: User):
    triggers = Session.query(Trigger).all()
    local_triggers = Session.query(LocalTrigger).filter_by(chat_id=update.message.chat.id).all()
    msg = MSG_TRIGGER_LIST_HEADER + \
        MSG_TRIGGER_GLOBAL + ('\n'.join([escape(trigger.trigger) for trigger in triggers]) or MSG_EMPTY) + \
        MSG_TRIGGER_LOCAL + ('\n'.join([escape(trigger.trigger) for trigger in local_triggers]) or MSG_EMPTY)
    send_async(bot, chat_id=update.message.chat.id, text=msg, parse_mode=ParseMode.HTML)


def add_trigger_db(msg: Message, chat, trigger_text: str):
    trigger = Session.query(LocalTrigger).filter_by(chat_id=chat.id, trigger=trigger_text).first()
    if trigger is None:
        trigger = LocalTrigger()
        trigger.chat_id = chat.id
        trigger.trigger = trigger_text
    if msg.audio:
        trigger.message = msg.audio.file_id
        trigger.message_type = MessageType.AUDIO.value
    elif msg.document:
        trigger.message = msg.document.file_id
        trigger.message_type = MessageType.DOCUMENT.value
    elif msg.voice:
        trigger.message = msg.voice.file_id
        trigger.message_type = MessageType.VOICE.value
    elif msg.sticker:
        trigger.message = msg.sticker.file_id
        trigger.message_type = MessageType.STICKER.value
    elif msg.contact:
        trigger.message = str(msg.contact)
        trigger.message_type = MessageType.CONTACT.value
    elif msg.video:
        trigger.message = msg.video.file_id
        trigger.message_type = MessageType.VIDEO.value
    elif msg.video_note:
        trigger.message = msg.video_note.file_id
        trigger.message_type = MessageType.VIDEO_NOTE.value
    elif msg.location:
        trigger.message = str(msg.location)
        trigger.message_type = MessageType.LOCATION.value
    elif msg.photo:
        trigger.message = msg.photo[-1].file_id
        trigger.message_type = MessageType.PHOTO.value
    else:
        trigger.message = msg.text
        trigger.message_type = MessageType.TEXT.value
    Session.add(trigger)
    Session.commit()


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def set_trigger(bot: MQBot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)
    if len(msg) == 2 and len(msg[1]) > 0 and update.message.reply_to_message:
        trigger = msg[1].strip()
        data = update.message.reply_to_message
        add_trigger_db(data, update.message.chat, trigger)
        send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_NEW.format(trigger))
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_NEW_ERROR)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def add_trigger(bot: MQBot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)
    if len(msg) == 2 and len(msg[1]) > 0 and update.message.reply_to_message:
        trigger_text = msg[1].strip()
        trigger = Session.query(LocalTrigger).filter_by(chat_id=update.message.chat.id, trigger=trigger_text).first()
        if trigger is None:
            data = update.message.reply_to_message
            add_trigger_db(data, update.message.chat, trigger_text)
            send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_NEW.format(trigger_text))
        else:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_EXISTS.format(trigger_text))
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_NEW_ERROR)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def enable_trigger_all(bot: MQBot, update: Update, user: User):
    group = update_group(update.message.chat)
    group.allow_trigger_all = True
    Session.add(group)
    Session.commit()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_ALL_ENABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def disable_trigger_all(bot: MQBot, update: Update, user: User):
    group = update_group(update.message.chat)
    group.allow_trigger_all = False
    Session.add(group)
    Session.commit()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_ALL_DISABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def del_trigger(bot: MQBot, update: Update, user: User):
    msg = update.message.text.split(' ', 1)[1]
    trigger = Session.query(LocalTrigger).filter_by(trigger=msg).first()
    if trigger is not None:
        Session.delete(trigger)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_DEL.format(msg))
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_TRIGGER_DEL_ERROR)
