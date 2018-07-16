import logging
from datetime import datetime, timedelta
from html import escape
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import JobQueue, Job

from core.bot import MQBot
from core.decorators import command_handler
from core.enums import CASTLE_LIST, TACTICTS_COMMAND_PREFIX, AdminType, MessageType
from core.handler.callback.util import create_callback, CallbackAction, get_callback_action
from core.texts import *
from core.db import Session
from core.model import Group, User, Admin, OrderGroup, Order, OrderCleared, Squad, SquadMember
from core.utils import send_async
from functions.order.groups import list
from functions.order.util import OrderDraft, __send_order

Session()

order_updated = {}


@command_handler(
    min_permission=AdminType.GROUP,
)
def manage(bot: MQBot, update: Update, user: User, chat_data):
    if not update.callback_query:
        __handle_direct_message_order(bot, chat_data, update, user)
    else:
        __handle_button_order(bot, chat_data, update, user)


def __handle_button_order(bot, chat_data, update, user):
    # Order was initiated by inline buttons
    # Do we already have an order drafted?
    if "order" in chat_data:
        logging.debug("Order: Existing Order")
        o = chat_data['order']
    else:
        logging.debug("Order: New Order")
        o = OrderDraft()
        o.type = MessageType.TEXT
    admin_user = Session.query(Admin).filter(Admin.user_id == update.callback_query.from_user.id).all()
    action = get_callback_action(update.callback_query.data, user.id)
    # Specific Sub-Functions called?
    if "sub_action" in action.data:
        if action.data['sub_action'] == "toggle_button":
            o.button = not o.button
        elif action.data['sub_action'] == "toggle_pin":
            o.pin = not o.pin
    elif "text" in action.data:
        o.order = action.data['text']
    # Save to chat_data
    chat_data['order'] = o

    if "sub_action" in action.data and action.data['sub_action'] == "select_squads":
        logging.debug("Order: Choose Squad")
        markup = __get_select_chat_for_orders_keyboard(
            user,
            o.pin,
            o.button,
        )
    else:
        logging.debug("Order: Choose Group")
        markup = __get_select_groups_for_orders_keyboard(
            user,
            admin_user,
            o.pin,
            o.button,
        )
    if o.type == MessageType.TEXT:
        text = MSG_ORDER_SEND_HEADER.format(escape(o.order))
    else:
        text = MSG_ORDER_SEND_HEADER.format(chat_data['order_type'])
    bot.edit_message_text(
        text,
        update.callback_query.message.chat.id,
        update.callback_query.message.message_id,
        reply_markup=markup,
        parse_mode=ParseMode.HTML
    )


def __handle_direct_message_order(bot, chat_data, update, user):
    # Order was sent/forwarded to Botato
    admin_user = Session.query(Admin).filter(Admin.user_id == update.effective_user.id).all()
    o = OrderDraft()
    msg = update.message
    if msg.audio:
        o.order = msg.audio.file_id
        o.type = MessageType.AUDIO
    elif msg.document:
        o.order = msg.document.file_id
        o.type = MessageType.DOCUMENT
    elif msg.voice:
        o.order = msg.voice.file_id
        o.type = MessageType.VOICE
    elif msg.sticker:
        o.order = msg.sticker.file_id
        o.type = MessageType.STICKER
    elif msg.contact:
        o.order = str(msg.contact)
        o.type = MessageType.CONTACT
    elif msg.video:
        o.order = msg.video.file_id
        o.type = MessageType.VIDEO
    elif msg.video_note:
        o.order = msg.video_note.file_id
        o.type = MessageType.VIDEO_NOTE
    elif msg.location:
        o.order = str(msg.location)
        o.type = MessageType.LOCATION
    elif msg.photo:
        o.order = msg.photo[-1].file_id
        o.type = MessageType.PHOTO
    else:
        o.order = msg.text
        o.type = MessageType.TEXT
    markup = __get_select_groups_for_orders_keyboard(
        user,
        admin_user,
        o.pin,
        o.button,
    )
    if o.type == MessageType.TEXT:
        text = MSG_ORDER_SEND_HEADER.format(escape(o.order))
    else:
        text = MSG_ORDER_SEND_HEADER.format(chat_data['order_type'])

    chat_data['order'] = o

    send_async(
        bot,
        text=text,
        chat_id=user.id,
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
        chat_data=chat_data
    )


@command_handler(
    min_permission=AdminType.GROUP,
)
def select_orders(bot: MQBot, update: Update, user: User, chat_data):
    markup = __get_castle_orders_keyboard(user)
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=MSG_FLAG_CHOOSE_HEADER,
        reply_markup=markup
    )


@command_handler(
    min_permission=AdminType.GROUP,
)
def send_order(bot: MQBot, update: Update, user: User, chat_data=None):
    if not update.callback_query:
        logging.warning("Tried to call send_order without callback_query")
        return

    action = get_callback_action(update.callback_query.data, user.id)

    o = chat_data['order']
    logging.info(
        "Order: text='%s', order_btn='%s', order_text IN CASTLE_LIST='%s'",
        o.order,
        o.button,
        o.order in CASTLE_LIST
    )

    # Send to a Group/Squad
    if "group_id" in action.data:
        logging.info("Sending order for group='%s'", action.data['group_id'])
        if o.button:
            order = Order()
            order.text = o.order
            order.chat_id = action.data['group_id']
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

            markup = __get_confirm_keyboard(
                user,
                order.id,
                0,
                o.order in CASTLE_LIST or o.order.startswith(TACTICTS_COMMAND_PREFIX),
                o.order
            )
            __send_order(
                bot=bot,
                order=o,
                chat_id=order.chat_id,
                markup=markup
            )
        else:
            markup = None
            if o.order in CASTLE_LIST or o.order.startswith(TACTICTS_COMMAND_PREFIX):
                markup = __get_forward_keyboard(o.order, 0)

            __send_order(
                bot=bot,
                order=o,
                chat_id=action.data['group_id'],
                markup=markup
            )
    if "order_group_id" in action.data:
        logging.info("Sending order for order_group='%s'", action.data['order_group_id'])
        group = Session.query(OrderGroup).filter_by(id=action.data['order_group_id']).first()
        for item in group.items:
            logging.info("Order for chat_id='%s'", item.chat_id)
            if o.button:
                order = Order()
                order.text = o.order
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
                markup = __get_confirm_keyboard(
                    user,
                    order.id,
                    0,
                    o.order in CASTLE_LIST or o.order.startswith(TACTICTS_COMMAND_PREFIX),
                    o.order
                )
                __send_order(
                    bot=bot,
                    order=o,
                    chat_id=order.chat_id,
                    markup=markup
                )
            else:
                markup = None
                if o.order in CASTLE_LIST or o.order.startswith(TACTICTS_COMMAND_PREFIX):
                    markup = __get_forward_keyboard(o.order, 0)

                __send_order(
                    bot=bot,
                    order=o,
                    chat_id=item.chat_id,
                    markup=markup,
                )

    update.callback_query.answer(text=MSG_ORDER_SENT)

# NOTE: Since every user can trigger this


def inline_order_confirmed(bot: MQBot, update: Update, user: User, job_queue: JobQueue):
    if not update.callback_query:
        logging.warning("Tried to call inline_order_confirmed without callback_query")
        return

    logging.info("inline_order_confirmed called by user_id='%s'", user.id)
    action = get_callback_action(update.callback_query.data, user.id)

    order = Session.query(Order).filter_by(id=action.data['order_id']).first()
    if order is not None:
        squad = Session.query(Squad).filter_by(chat_id=order.chat_id).first()
        if squad is not None:
            squad_member = Session.query(SquadMember).filter_by(
                squad_id=squad.chat_id,
                user_id=update.callback_query.from_user.id,
                approved=True
            ).first()

            if squad_member:
                order_ok = Session.query(OrderCleared).filter_by(
                    order_id=action.data['order_id'],
                    user_id=squad_member.user_id
                ).first()
                if not order_ok and datetime.now() - order.date < timedelta(minutes=10):
                    order_ok = OrderCleared()
                    order_ok.order_id = action.data['order_id']
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
            order_ok = Session.query(OrderCleared).filter_by(
                order_id=action.data['order_id'],
                user_id=update.callback_query.from_user.id
            ).first()

            if order_ok is None and datetime.now() - order.date < timedelta(minutes=10):
                order_ok = OrderCleared()
                order_ok.order_id = action.data['order_id']
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


def update_confirmed(bot: MQBot, job: Job):
    order = job.context
    confirmed = order.cleared
    msg = MSG_ORDER_CLEARED_BY_HEADER
    for confirm in confirmed:
        msg += str(confirm.user) + '\n'
    bot.edit_message_text(msg, order.chat_id, order.confirmed_msg)


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
    return InlineKeyboardMarkup(buttons)


def __get_confirm_keyboard(user: User, order_id, count, forward=False, order=''):
    buttons = [
        [InlineKeyboardButton(
            MSG_ORDER_ACCEPT.format(count),
            callback_data=create_callback(
                CallbackAction.ORDER_CONFIRM,
                user.id,
                order_id=order_id
            )
        )]
    ]
    if forward:
        buttons.append(
            [
                InlineKeyboardButton(text=MSG_ORDER_FORWARD, switch_inline_query=order)
            ]
        )
    inline_markup = InlineKeyboardMarkup(buttons)
    return inline_markup


def __get_forward_keyboard(order_id, count):
    inline_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=MSG_ORDER_FORWARD, switch_inline_query=order_id)]])
    return inline_markup


def __get_select_chat_for_orders_keyboard(user, pin=True, btn=True):
    squads = Session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        inline_keys.append([
            InlineKeyboardButton(
                squad.squad_name,
                callback_data=create_callback(
                    CallbackAction.ORDER_GIVE,
                    user.id,
                    group_id=squad.chat_id,
                )
            )
        ])

    inline_keys.append([
        InlineKeyboardButton(
            MSG_BACK,
            callback_data=create_callback(
                CallbackAction.ORDER,
                user.id
            )
        )
    ])

    inline_keys.append([
        InlineKeyboardButton(
            MSG_ORDER_PIN if pin else MSG_ORDER_NO_PIN,
            callback_data=create_callback(
                CallbackAction.ORDER,
                user.id,
                sub_action='toggle_pin'
            )
        )
    ])

    inline_keys.append([
        InlineKeyboardButton(
            MSG_ORDER_BUTTON if btn else MSG_ORDER_NO_BUTTON,
            callback_data=create_callback(
                CallbackAction.ORDER,
                user.id,
                sub_action='toggle_button'
            )
        )
    ])



    inline_markup = InlineKeyboardMarkup(inline_keys)
    return inline_markup


def __get_select_groups_for_orders_keyboard(user, admin_user: list = None, pin: bool = True, btn=True):
    if admin_user:
        group_adm = True
        for adm in admin_user:
            if adm.admin_type < AdminType.GROUP.value:
                group_adm = False
                break
        if group_adm:
            inline_keys = []
            for adm in admin_user:
                group = Session.query(Group).filter_by(id=adm.group_id, bot_in_group=True).first()
                if group:
                    inline_keys.append([
                        InlineKeyboardButton(
                            group.title,
                            callback_data=create_callback(
                                CallbackAction.ORDER_GIVE,
                                user.id,
                                group_id=group.id
                            )
                        )
                    ])

            inline_keys.append([
                InlineKeyboardButton(
                    MSG_ORDER_PIN if pin else MSG_ORDER_NO_PIN,
                    callback_data=create_callback(
                        CallbackAction.ORDER,
                        user.id,
                        sub_action='toggle_pin'
                    )
                )
            ])
            inline_keys.append([
                InlineKeyboardButton(
                    MSG_ORDER_BUTTON if btn else MSG_ORDER_NO_BUTTON,
                    callback_data=create_callback(
                        CallbackAction.ORDER,
                        user.id,
                        sub_action='toggle_button'
                    )
                )
            ])
        else:
            order_groups = Session.query(OrderGroup).all()
            inline_keys = []
            for order_group in order_groups:
                inline_keys.append([
                    InlineKeyboardButton(
                        order_group.name,
                        callback_data=create_callback(
                            CallbackAction.ORDER_GIVE,
                            user.id,
                            order_group_id=order_group.id,
                        )
                    )
                ])

            inline_keys.append([
                InlineKeyboardButton(
                    MSG_ORDER_TO_SQUADS,
                    callback_data=create_callback(
                        CallbackAction.ORDER,
                        user.id,
                        sub_action='select_squads'
                    )
                )
            ])

            inline_keys.append([
                InlineKeyboardButton(
                    MSG_ORDER_PIN if pin else MSG_ORDER_NO_PIN,
                    callback_data=create_callback(
                        CallbackAction.ORDER,
                        user.id,
                        sub_action='toggle_pin'
                    )
                )
            ])
            inline_keys.append([
                InlineKeyboardButton(
                    MSG_ORDER_BUTTON if btn else MSG_ORDER_NO_BUTTON,
                    callback_data=create_callback(
                        CallbackAction.ORDER,
                        user.id,
                        sub_action='toggle_button'
                    )
                )
            ])

        inline_markup = InlineKeyboardMarkup(inline_keys)
        return inline_markup
