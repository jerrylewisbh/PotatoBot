import json
import logging
import telegram
from datetime import datetime, timedelta
from html import escape

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import run_async, JobQueue, Job

from core.decorators import command_handler
from core.enums import CASTLE_LIST, TACTICTS_COMMAND_PREFIX
from core.handler.callback.util import create_callback, CallbackAction, get_callback_action
from core.texts import *
from core.texts import MSG_ORDER_SEND_HEADER
from core.types import Admin, AdminType, MessageType, Session, User, Order, OrderGroup, Squad, SquadMember, OrderCleared
from core.utils import send_async
from functions.inline_markup import QueryType
from functions.order.groups import generate_order_groups_markup
from functions.order.util import __send_order

Session()

order_updated = {}

@command_handler(
    min_permission=AdminType.GROUP,
)
def manage(bot: Bot, update: Update, user: User, chat_data):
    chat_data['order_wait'] = False
    if not update.callback_query:
        # Order was sent/forwarded to Botato
        admin_user = Session.query(Admin).filter(Admin.user_id == update.effective_user.id).all()

        msg = update.message
        if msg.audio:
            chat_data['order'] = msg.audio.file_id
            chat_data['order_type'] = MessageType.AUDIO
        elif msg.document:
            chat_data['order'] = msg.document.file_id
            chat_data['order_type'] = MessageType.DOCUMENT
        elif msg.voice:
            chat_data['order'] = msg.voice.file_id
            chat_data['order_type'] = MessageType.VOICE
        elif msg.sticker:
            chat_data['order'] = msg.sticker.file_id
            chat_data['order_type'] = MessageType.STICKER
        elif msg.contact:
            chat_data['order'] = str(msg.contact)
            chat_data['order_type'] = MessageType.CONTACT
        elif msg.video:
            chat_data['order'] = msg.video.file_id
            chat_data['order_type'] = MessageType.VIDEO
        elif msg.video_note:
            chat_data['order'] = msg.video_note.file_id
            chat_data['order_type'] = MessageType.VIDEO_NOTE
        elif msg.location:
            chat_data['order'] = str(msg.location)
            chat_data['order_type'] = MessageType.LOCATION
        elif msg.photo:
            chat_data['order'] = msg.photo[-1].file_id
            chat_data['order_type'] = MessageType.PHOTO
        else:
            chat_data['order'] = msg.text
            chat_data['order_type'] = MessageType.TEXT

    else:
        # Order was initiated by inline buttons
        admin_user = Session.query(Admin).filter(Admin.user_id == update.callback_query.from_user.id).all()
        action = get_callback_action(update.callback_query.data, user.id)

        chat_data['order_type'] = MessageType.TEXT
        chat_data['order'] = action.data['text']

    markup = generate_order_groups_markup(
        user,
        admin_user,
        chat_data['pin'] if 'pin' in chat_data else False,
        chat_data['btn'] if 'btn' in chat_data else True
    )

    if chat_data['order_type'] == MessageType.TEXT:
        text = MSG_ORDER_SEND_HEADER.format(escape(chat_data['order']))
    else:
        text = MSG_ORDER_SEND_HEADER.format(chat_data['order_type'])

    bot.edit_message_text(
        text,
        update.callback_query.message.chat.id,
        update.callback_query.message.message_id,
        reply_markup=markup,
        parse_mode=ParseMode.HTML
    )


@command_handler(
    min_permission=AdminType.GROUP,
)
def select_orders(bot: Bot, update: Update, user: User, chat_data):
    markup = __get_castle_orders_keyboard(user)
    chat_data['order_wait'] = True
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=MSG_FLAG_CHOOSE_HEADER,
        reply_markup=markup
    )


@run_async
def order_button(bot: Bot, update: Update, user: User, data, chat_data):
    order_text = chat_data['order']
    order_type = chat_data['order_type']
    order_pin = chat_data['pin'] if 'pin' in chat_data else True
    order_btn = chat_data['btn'] if 'btn' in chat_data else True
    logging.info(
        "Order: text='%s', order_btn='%s', order_text IN CASTLE_LIST='%s'",
        order_text,
        order_btn,
        (order_text in CASTLE_LIST)
    )
    if not data['g']:
        if order_btn:
            order = Order()
            order.text = order_text
            order.chat_id = data['id']
            order.date = datetime.now()
            msg = bot.send_message(
                chat_id=order.chat_id,
                text=MSG_ORDER_CLEARED_BY_HEADER + MSG_EMPTY
            ).result()
            if msg:
                order.confirmed_msg = msg.message_id
            else:
                order.confirmed_msg = 0
            Session.add(order)
            Session.commit()
            markup = generate_ok_markup(
                order.id,
                0,
                order_text in CASTLE_LIST or order_text.startswith(TACTICTS_COMMAND_PREFIX),
                order_text
            )
            __send_order(
                bot=bot,
                text=order.text,
                message_type=order_type,
                chat_id=order.chat_id,
                markup=markup,
                pin=order_pin
            )
        else:
            markup = None
            if order_text in CASTLE_LIST or order_text.startswith(TACTICTS_COMMAND_PREFIX):
                markup = generate_forward_markup(order_text, 0)
            __send_order(
                bot=bot,
                text=order_text,
                message_type=order_type,
                chat_id=data['id'],
                markup=markup,
                pin=order_pin
            )
    else:
        group = Session.query(OrderGroup).filter_by(id=data['id']).first()
        for item in group.items:
            if order_btn:
                order = Order()
                order.text = order_text
                order.chat_id = item.chat_id
                order.date = datetime.now()
                msg = bot.send_message(
                    chat_id=order.chat_id,
                    text=MSG_ORDER_CLEARED_BY_HEADER + MSG_EMPTY
                ).result()

                if msg:
                    order.confirmed_msg = msg.message_id
                else:
                    order.confirmed_msg = 0
                Session.add(order)
                Session.commit()
                markup = generate_ok_markup(
                    order.id,
                    0,
                    order_text in CASTLE_LIST or order_text.startswith(TACTICTS_COMMAND_PREFIX),
                    order_text
                )
                __send_order(
                    bot=bot,
                    text=order.text,
                    message_type=order_type,
                    chat_id=order.chat_id,
                    markup=markup,
                    pin=order_pin
                )
            else:
                markup = None
                if order_text in CASTLE_LIST or order_text.startswith(TACTICTS_COMMAND_PREFIX):
                    markup = generate_forward_markup(order_text, 0)

                __send_order(
                    bot=bot,
                    text=order_text,
                    message_type=order_type,
                    chat_id=item.chat_id,
                    markup=markup,
                    pin=order_pin
                )

    update.callback_query.answer(text=MSG_ORDER_SENT)


def trigger_order_button(bot: Bot, update: Update, user: User, data: dict, chat_data: dict):
    if 'btn' in chat_data:
        chat_data['btn'] = not chat_data['btn']
    else:
        chat_data['btn'] = False
    if data['g']:
        admin_user = Session.query(Admin).filter(Admin.user_id == update.callback_query.from_user.id).all()
        markup = generate_order_groups_markup(
            user,
            admin_user,
            chat_data['pin'] if 'pin' in chat_data else False,
            chat_data['btn'] if 'btn' in chat_data else True
        )
        bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    else:
        markup = generate_order_chats_markup(chat_data['pin'] if 'pin' in chat_data else True,
                                             chat_data['btn'] if 'btn' in chat_data else True)
        bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)


def trigger_order_pin(bot: Bot, update: Update, user: User, data: dict, chat_data: dict):
    if 'pin' in chat_data:
        chat_data['pin'] = not chat_data['pin']
    else:
        chat_data['pin'] = False
    if data['g']:
        admin_user = Session.query(Admin).filter(Admin.user_id == update.callback_query.from_user.id).all()
        markup = generate_order_groups_markup(
            user,
            admin_user,
            chat_data['pin'] if 'pin' in chat_data else False,
            chat_data['btn'] if 'btn' in chat_data else True
        )
        bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    else:
        markup = generate_order_chats_markup(chat_data['pin'] if 'pin' in chat_data else True,
                                             chat_data['btn'] if 'btn' in chat_data else True)
        bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)


def inline_order_confirmed(bot: Bot, update: Update, user: User, data: dict, job_queue: JobQueue):
    order = Session.query(Order).filter_by(id=data['id']).first()
    if order is not None:
        squad = Session.query(Squad).filter_by(chat_id=order.chat_id).first()
        if squad is not None:
            squad_member = Session.query(SquadMember).filter_by(squad_id=squad.chat_id,
                                                                user_id=update.callback_query.from_user.id,
                                                                approved=True).first()
            if squad_member is not None:
                order_ok = Session.query(OrderCleared).filter_by(order_id=data['id'],
                                                                 user_id=squad_member.user_id).first()
                if order_ok is None and datetime.now() - order.date < timedelta(minutes=10):
                    order_ok = OrderCleared()
                    order_ok.order_id = data['id']
                    order_ok.user_id = update.callback_query.from_user.id
                    Session.add(order_ok)
                    Session.commit()
                    if order.confirmed_msg != 0:
                        if order.id not in order_updated or \
                                    datetime.now() - order_updated[order.id] > timedelta(seconds=4):
                            order_updated[order.id] = datetime.now()
                            job_queue.run_once(update_confirmed, 5, order)
                    update.callback_query.answer(text=MSG_ORDER_CLEARED)
                else:
                    update.callback_query.answer(text=MSG_ORDER_CLEARED_ERROR)
            else:
                update.callback_query.answer(text=MSG_ORDER_CLEARED_ERROR)
        else:
            order_ok = Session.query(OrderCleared).filter_by(order_id=data['id'],
                                                             user_id=update.callback_query.from_user.id).first()
            if order_ok is None and datetime.now() - order.date < timedelta(minutes=10):
                order_ok = OrderCleared()
                order_ok.order_id = data['id']
                order_ok.user_id = update.callback_query.from_user.id
                Session.add(order_ok)
                Session.commit()
                if order.confirmed_msg != 0:
                    if order.id not in order_updated or \
                            datetime.now() - order_updated[order.id] > timedelta(seconds=4):
                        order_updated[order.id] = datetime.now()
                        job_queue.run_once(update_confirmed, 5, order)
                update.callback_query.answer(text=MSG_ORDER_CLEARED)
            else:
                update.callback_query.answer(text=MSG_ORDER_CLEARED_ERROR)


def inline_orders(bot: Bot, update: Update, user: User, data: dict, chat_data: dict):
    chat_data['order_wait'] = False
    if 'txt' in data and len(data['txt']):
            chat_data['order'] = data['txt']
    markup = generate_order_chats_markup(chat_data['pin'] if 'pin' in chat_data else True,
                                         chat_data['btn'] if 'btn' in chat_data else True)
    bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=markup)


def update_confirmed(bot: Bot, job: Job):
    order = job.context
    confirmed = order.cleared
    msg = MSG_ORDER_CLEARED_BY_HEADER
    for confirm in confirmed:
        msg += str(confirm.user) + '\n'
    bot.editMessageText(msg, order.chat_id, order.confirmed_msg)


def __get_castle_orders_keyboard(user: User):
    buttons = []

    split = [CASTLE_LIST[x:x + 3] for x in range(0, len(CASTLE_LIST), 3)]
    for row in split:
        button_row = []
        for button in row:
            button_row.append(
                InlineKeyboardButton(
                    button,
                    callback_data=create_callback(
                        CallbackAction.ORDER,
                        user.id,
                        text=button
                    )
                )
            )
        buttons.append(button_row)
    import pprint
    pprint.pprint(buttons)
    return InlineKeyboardMarkup(buttons)


def generate_ok_markup(order_id, count, forward=False, order=''):

    buttons = [[InlineKeyboardButton(MSG_ORDER_ACCEPT.format(count),
                                     callback_data=json.dumps(
        {'t': QueryType.OrderOk.value, 'id': order_id}))]]
    if forward:
        buttons.append([InlineKeyboardButton(text=MSG_ORDER_FORWARD, switch_inline_query=order)])
    inline_markup = InlineKeyboardMarkup(buttons)
    return inline_markup


def generate_forward_markup(order_id, count):
    inline_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=MSG_ORDER_FORWARD, switch_inline_query=order_id)]])
    return inline_markup


def generate_order_chats_markup(pin=True, btn=True):
    squads = Session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        inline_keys.append([
            InlineKeyboardButton(
                squad.squad_name,
                callback_data=json.dumps(
                    {'t': QueryType.Order.value, 'g': False, 'id': squad.chat_id}
                ))
        ])

    inline_keys.append([
        InlineKeyboardButton(
            MSG_ORDER_PIN if pin else MSG_ORDER_NO_PIN,
            callback_data=json.dumps(
                {'t': QueryType.TriggerOrderPin.value, 'g': False}
            )
        )
    ])

    inline_keys.append([
        InlineKeyboardButton(
            MSG_ORDER_BUTTON if btn else MSG_ORDER_NO_BUTTON,
            callback_data=json.dumps(
                {'t': QueryType.TriggerOrderButton.value, 'g': False}
            )
        )
    ])

    inline_markup = InlineKeyboardMarkup(inline_keys)
    return inline_markup
