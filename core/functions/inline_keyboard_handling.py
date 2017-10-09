from datetime import datetime, timedelta
from enum import Enum
import json
from json import loads
import logging

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, TelegramError, Message
from telegram.ext.dispatcher import run_async

from core.enums import Castle, Icons
from core.functions.admins import del_adm
from core.template import fill_char_template
from core.types import (
    User, Group, Admin, admin_allowed, Order, OrderGroup,
    OrderGroupItem, OrderCleared, Squad, user_allowed,
    Character, SquadMember, MessageType, AdminType)
from core.texts import *
from core.utils import send_async, update_group, add_user

from sqlalchemy import func


LOGGER = logging.getLogger('MyApp')


class QueryType(Enum):
    GroupList = 0
    GroupInfo = 1
    DelAdm = 2
    Order = 3
    OrderOk = 4
    Orders = 5
    OrderGroup = 6
    OrderGroupManage = 7
    OrderGroupTriggerChat = 8
    OrderGroupAdd = 9
    OrderGroupDelete = 10
    OrderGroupList = 11
    ShowStock = 12
    ShowEquip = 13
    ShowHero = 14
    MemberList = 15
    LeaveSquad = 16
    RequestSquad = 17
    RequestSquadAccept = 18
    RequestSquadDecline = 19
    InviteSquadAccept = 20
    InviteSquadDecline = 21
    TriggerOrderPin = 22
    SquadList = 23
    GroupDelete = 24


@admin_allowed()
def send_status(bot: Bot, update: Update, session):
    msg = MSG_GROUP_STATUS_CHOOSE_CHAT
    squads = session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        inline_keys.append(InlineKeyboardButton(squad.squad_name,
                                                callback_data=json.dumps({'t': QueryType.GroupInfo.value,
                                                                          'id': squad.chat_id})))
    inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
    send_async(bot, chat_id=update.message.chat.id, text=msg, reply_markup=inline_markup)


def generate_group_info(group_id, session):
    group = session.query(Group).filter(Group.id == group_id).first()
    admins = session.query(Admin).filter(Admin.admin_group == group_id).all()
    adm_msg = ''
    adm_del_keys = []
    for adm in admins:
        user = session.query(User).filter_by(id=adm.user_id).first()
        adm_msg += MSG_GROUP_STATUS_ADMIN_FORMAT.\
            format(user.id, user.username or '', user.first_name or '', user.last_name or '')
        adm_del_keys.append([InlineKeyboardButton(MSG_GROUP_STATUS_DEL_ADMIN.
                                                  format(user.first_name or '', user.last_name or ''),
                                                  callback_data=json.dumps(
                                                      {'t': QueryType.DelAdm.value, 'uid': user.id,
                                                       'gid': group_id}))])
    msg = MSG_GROUP_STATUS.format(group.title,
                                  adm_msg,
                                  MSG_ON if group.welcome_enabled else MSG_OFF,
                                  MSG_ON if group.allow_trigger_all else MSG_OFF,
                                  MSG_ON if len(group.squad) and group.squad[0].thorns_enabled else MSG_OFF)
    adm_del_keys.append([InlineKeyboardButton(MSG_ORDER_GROUP_DEL, callback_data=json.dumps(
        {'t': QueryType.GroupDelete.value, 'gid': group_id}))])
    adm_del_keys.append([InlineKeyboardButton(MSG_BACK, callback_data=json.dumps(
        {'t': QueryType.GroupList.value}))])
    inline_markup = InlineKeyboardMarkup(adm_del_keys)
    return msg, inline_markup


def generate_flag_orders():
    flag_btns = [[InlineKeyboardButton(Castle.BLACK.value, callback_data=json.dumps(
                      {'t': QueryType.OrderGroup.value, 'txt': Castle.BLACK.value})),
                  InlineKeyboardButton(Castle.WHITE.value, callback_data=json.dumps(
                      {'t': QueryType.OrderGroup.value, 'txt': Castle.WHITE.value})),
                  InlineKeyboardButton(Castle.BLUE.value, callback_data=json.dumps(
                      {'t': QueryType.OrderGroup.value, 'txt': Castle.BLUE.value}))],
                 [InlineKeyboardButton(Castle.YELLOW.value, callback_data=json.dumps(
                      {'t': QueryType.OrderGroup.value, 'txt': Castle.YELLOW.value})),
                  InlineKeyboardButton(Castle.RED.value, callback_data=json.dumps(
                      {'t': QueryType.OrderGroup.value, 'txt': Castle.RED.value})),
                  InlineKeyboardButton(Castle.DUSK.value, callback_data=json.dumps(
                      {'t': QueryType.OrderGroup.value, 'txt': Castle.DUSK.value}))],
                 [InlineKeyboardButton(Castle.MINT.value, callback_data=json.dumps(
                      {'t': QueryType.OrderGroup.value, 'txt': Castle.MINT.value})),
                  InlineKeyboardButton(Castle.GORY.value, callback_data=json.dumps(
                      {'t': QueryType.OrderGroup.value, 'txt': Icons.GORY.value})),
                  InlineKeyboardButton(Castle.LES.value, callback_data=json.dumps(
                      {'t': QueryType.OrderGroup.value, 'txt': Icons.LES.value}))],
                 [InlineKeyboardButton(Castle.SEA.value, callback_data=json.dumps(
                      {'t': QueryType.OrderGroup.value, 'txt': Icons.SEA.value}))]]
    inline_markup = InlineKeyboardMarkup(flag_btns)
    return inline_markup


def generate_order_chats_markup(session, pin=True):
    squads = session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        inline_keys.append([InlineKeyboardButton(squad.squad_name, callback_data=json.dumps(
            {'t': QueryType.Order.value, 'g': False, 'id': squad.chat_id}))])
    inline_keys.append([InlineKeyboardButton(MSG_ORDER_PIN if pin else MSG_ORDER_NO_PIN, callback_data=json.dumps(
        {'t': QueryType.TriggerOrderPin.value, 'g': False}))])
    inline_markup = InlineKeyboardMarkup(inline_keys)
    return inline_markup


def generate_order_groups_markup(session, admin_user: list=None, pin: bool=True):
    if admin_user:
        group_adm = True
        for adm in admin_user:
            if adm.admin_type < AdminType.GROUP.value:
                group_adm = False
                break
        if group_adm:
            inline_keys = []
            for adm in admin_user:
                group = session.query(Group).filter_by(id=adm.admin_group, bot_in_group=True).first()
                if group:
                    inline_keys.append([InlineKeyboardButton(group.title, callback_data=json.dumps(
                        {'t': QueryType.Order.value, 'g': False, 'id': group.id}))])
                inline_keys.append(
                    [InlineKeyboardButton(MSG_ORDER_PIN if pin else MSG_ORDER_NO_PIN, callback_data=json.dumps(
                        {'t': QueryType.TriggerOrderPin.value, 'g': True}))])
            inline_markup = InlineKeyboardMarkup(inline_keys)
            return inline_markup
    groups = session.query(OrderGroup).all()
    inline_keys = []
    for group in groups:
        inline_keys.append([InlineKeyboardButton(group.name, callback_data=json.dumps(
            {'t': QueryType.Order.value, 'g': True, 'id': group.id}))])
    inline_keys.append([InlineKeyboardButton(MSG_ORDER_TO_SQUADS, callback_data=json.dumps(
        {'t': QueryType.Orders.value}))])
    inline_keys.append([InlineKeyboardButton(MSG_ORDER_PIN if pin else MSG_ORDER_NO_PIN, callback_data=json.dumps(
        {'t': QueryType.TriggerOrderPin.value, 'g': True}))])
    inline_markup = InlineKeyboardMarkup(inline_keys)
    return inline_markup


def generate_ok_markup(order_id, count):
    inline_markup = InlineKeyboardMarkup([[InlineKeyboardButton(MSG_ORDER_ACCEPT.format(count),
                                                                callback_data=json.dumps(
                                                                    {'t': QueryType.OrderOk.value, 'id': order_id}))]])
    return inline_markup


def generate_groups_manage(session):
    groups = session.query(OrderGroup).all()
    inline_keys = []
    for group in groups:
        inline_keys.append([InlineKeyboardButton(group.name, callback_data=json.dumps(
            {'t': QueryType.OrderGroupManage.value, 'id': group.id}))])
    inline_keys.append([InlineKeyboardButton(MSG_ORDER_GROUP_ADD, callback_data=json.dumps(
        {'t': QueryType.OrderGroupAdd.value}))])
    return InlineKeyboardMarkup(inline_keys)


def generate_group_manage(group_id, session):
    squads = session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        in_group = False
        for item in squad.chat.group_items:
            if item.group_id == group_id:
                in_group = True
                break
        inline_keys.append([InlineKeyboardButton((MSG_SYMBOL_ON if in_group else MSG_SYMBOL_OFF) +
                                                 squad.squad_name, callback_data=json.dumps(
            {'t': QueryType.OrderGroupTriggerChat.value, 'id': group_id, 'c': squad.chat_id}))])
    inline_keys.append([InlineKeyboardButton(MSG_ORDER_GROUP_DEL, callback_data=json.dumps(
        {'t': QueryType.OrderGroupDelete.value, 'id': group_id}))])
    inline_keys.append([InlineKeyboardButton(MSG_BACK, callback_data=json.dumps(
        {'t': QueryType.OrderGroupList.value}))])
    return InlineKeyboardMarkup(inline_keys)


def generate_profile_buttons(user, back_key=False):
    inline_keys = [[InlineKeyboardButton('🏅Герой', callback_data=json.dumps(
        {'t': QueryType.ShowHero.value, 'id': user.id, 'b': back_key}))]]
    if user.stock:
        inline_keys.append([InlineKeyboardButton('📦Склад', callback_data=json.dumps(
            {'t': QueryType.ShowStock.value, 'id': user.id, 'b': back_key}))])
    if user.equip:
        inline_keys.append([InlineKeyboardButton('🎽Экипировка', callback_data=json.dumps(
            {'t': QueryType.ShowEquip.value, 'id': user.id, 'b': back_key}))])
    if back_key:
        inline_keys.append(
            [InlineKeyboardButton(MSG_BACK,
                                  callback_data=json.dumps(
                                      {'t': QueryType.MemberList.value, 'id': user.member.squad_id}
                                  ))])
    return InlineKeyboardMarkup(inline_keys)


def generate_squad_list_key(squad, session):
    attack = 0
    defence = 0
    members = squad.members
    user_ids = []
    for member in members:
        user_ids.append(member.user_id)
    actual_profiles = session.query(Character.user_id, func.max(Character.date)).\
        filter(Character.user_id.in_(user_ids)).\
        group_by(Character.user_id).all()
    characters = session.query(Character).filter(Character.user_id.in_([a[0] for a in actual_profiles]),
                                                 Character.date.in_([a[1] for a in actual_profiles])).all()
    for character in characters:
        attack += character.attack
        defence += character.defence
    return [InlineKeyboardButton(
        '{} : {}⚔ {}🛡 {}👥'.format(
            squad.squad_name,
            attack,
            defence,
            len(members)
        ),
        callback_data=json.dumps({'t': QueryType.MemberList.value, 'id': squad.chat_id}))]


def generate_squad_list(squads, session):
    inline_keys = []
    for squad in squads:
        inline_keys.append(generate_squad_list_key(squad, session))
    return InlineKeyboardMarkup(inline_keys)


def generate_leave_squad(user_id):
    inline_keys = [[InlineKeyboardButton('Выйти',
                                         callback_data=json.dumps({'t': QueryType.LeaveSquad.value,
                                                                   'id': user_id}))]]
    return InlineKeyboardMarkup(inline_keys)


def generate_squad_request(session):
    inline_keys = []
    squads = session.query(Squad).filter_by(hiring=True).all()
    for squad in squads:
        inline_keys.append([InlineKeyboardButton(squad.squad_name,
                                                 callback_data=json.dumps(
                                                     {'t': QueryType.RequestSquad.value, 'id': squad.chat_id}))])
    return InlineKeyboardMarkup(inline_keys)


def generate_squad_members(members, session):
    inline_keys = []
    user_ids = []
    for member in members:
        user_ids.append(member.user_id)
    actual_profiles = session.query(Character.user_id, func.max(Character.date)). \
        filter(Character.user_id.in_(user_ids)). \
        group_by(Character.user_id).all()
    characters = session.query(Character).filter(Character.user_id.in_([a[0] for a in actual_profiles]),
                                                 Character.date.in_([a[1] for a in actual_profiles]))\
        .order_by(Character.level.desc()).all()
    for character in characters:
        time_passed = datetime.now() - character.date
        status_emoji = '❇'
        if time_passed > timedelta(days=7):
            status_emoji = '⁉'
        elif time_passed > timedelta(days=4):
            status_emoji = '‼'
        elif time_passed > timedelta(days=3):
            status_emoji = '❗'
        elif time_passed < timedelta(days=1):
            status_emoji = '🕐'
        inline_keys.append(
            [InlineKeyboardButton('{}{}: {}⚔ {}🛡 {}🏅'.
                                  format(status_emoji,
                                         character.name,
                                         character.attack,
                                         character.defence,
                                         character.level),
                                  callback_data=json.dumps(
                                      {'t': QueryType.ShowHero.value,
                                       'id': character.user_id,
                                       'b': True}
                                  ))])
    inline_keys.append(
        [InlineKeyboardButton(MSG_BACK,
                              callback_data=json.dumps(
                                  {'t': QueryType.SquadList.value}
                              ))])
    return InlineKeyboardMarkup(inline_keys)


def generate_squad_request_answer(user_id):
    inline_keys = [InlineKeyboardButton('✅Принять',
                                        callback_data=json.dumps(
                                            {'t': QueryType.RequestSquadAccept.value, 'id': user_id})),
                   InlineKeyboardButton('❌Отклонить',
                                        callback_data=json.dumps(
                                            {'t': QueryType.RequestSquadDecline.value, 'id': user_id}))]
    return InlineKeyboardMarkup([inline_keys])


def generate_squad_invite_answer(user_id):
    inline_keys = [InlineKeyboardButton(MSG_SQUAD_GREEN_INLINE_BUTTON,
                                        callback_data=json.dumps(
                                            {'t': QueryType.InviteSquadAccept.value, 'id': user_id})),
                   InlineKeyboardButton(MSG_SQUAD_RED_INLINE_BUTTON,
                                        callback_data=json.dumps(
                                            {'t': QueryType.InviteSquadDecline.value, 'id': user_id}))]
    return InlineKeyboardMarkup([inline_keys])


def generate_fire_up(members):
    inline_keys = []
    for member in members:
        inline_keys.append([InlineKeyboardButton('🔥{}: {}⚔ {}🛡'.format(member.user, member.user.character.attack,
                                                                       member.user.character.defence),
                                                 callback_data=json.dumps(
                                                     {'t': QueryType.LeaveSquad.value, 'id': member.user_id}))])
    return InlineKeyboardMarkup(inline_keys)


@run_async
def send_order(bot, order, order_type, chat_id, markup):
    try:
        msg_sent = None
        if order_type == MessageType.AUDIO.value:
            msg_sent = bot.send_audio(chat_id, order, reply_markup=markup)
        elif order_type == MessageType.DOCUMENT.value:
            msg_sent = bot.send_document(chat_id, order, reply_markup=markup)
        elif order_type == MessageType.VOICE.value:
            msg_sent = bot.send_voice(chat_id, order, reply_markup=markup)
        elif order_type == MessageType.STICKER.value:
            msg_sent = bot.send_sticker(chat_id, order, reply_markup=markup)
        elif order_type == MessageType.CONTACT.value:
            msg = order.replace('\'', '"')
            contact = loads(msg)
            if 'phone_number' not in contact.keys():
                contact['phone_number'] = None
            if 'first_name' not in contact.keys():
                contact['first_name'] = None
            if 'last_name' not in contact.keys():
                contact['last_name'] = None
                msg_sent = bot.send_contact(chat_id,
                                            contact['phone_number'],
                                            contact['first_name'],
                                            contact['last_name'],
                                            reply_markup=markup)
        elif order_type == MessageType.VIDEO.value:
            msg_sent = bot.send_video(chat_id, order, reply_markup=markup)
        elif order_type == MessageType.VIDEO_NOTE.value:
            msg_sent = bot.send_video_note(chat_id, order, reply_markup=markup)
        elif order_type == MessageType.LOCATION.value:
            msg = order.replace('\'', '"')
            location = loads(msg)
            msg_sent = bot.send_location(chat_id, location['latitude'], location['longitude'], reply_markup=markup)
        elif order_type == MessageType.PHOTO.value:
            msg_sent = bot.send_photo(chat_id, order, reply_markup=markup)
        else:
            msg_sent = send_async(bot, chat_id=chat_id, text=order, disable_web_page_preview=True, reply_markup=markup)
        return msg_sent
    except TelegramError as err:
        bot.logger.error(err.message)
        return None


@run_async
@user_allowed
def callback_query(bot: Bot, update: Update, session, chat_data: dict):
    update_group(update.callback_query.message.chat, session)
    user = add_user(update.callback_query.from_user, session)
    data = json.loads(update.callback_query.data)
    if data['t'] == QueryType.GroupList.value:
        msg = MSG_GROUP_STATUS_CHOOSE_CHAT
        squads = session.query(Squad).all()
        inline_keys = []
        for squad in squads:
            inline_keys.append(InlineKeyboardButton(squad.squad_name,
                                                    callback_data=json.dumps({'t': QueryType.GroupInfo.value,
                                                                              'id': squad.chat_id})))
        inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    elif data['t'] == QueryType.GroupInfo.value:
        msg, inline_markup = generate_group_info(data['id'], session)
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    elif data['t'] == QueryType.DelAdm.value:
        admin_user = session.query(User).filter_by(id=data['uid']).first()
        if admin_user:
            del_adm(bot, data['gid'], admin_user, session)
        msg, inline_markup = generate_group_info(data['gid'], session)
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    elif data['t'] == QueryType.Order.value:
        order_text = chat_data['order']
        order_type = chat_data['order_type']
        order_pin = True if 'pin' in chat_data and chat_data['pin'] or 'pin' not in chat_data else False
        if not data['g']:
            order = Order()
            order.text = order_text
            order.chat_id = data['id']
            order.date = datetime.now()
            msg = send_async(bot, chat_id=order.chat_id, text=MSG_ORDER_CLEARED_BY_HEADER + MSG_EMPTY).result()
            if msg:
                order.confirmed_msg = msg.message_id
            else:
                order.confirmed_msg = 0
            session.add(order)
            session.commit()
            markup = generate_ok_markup(order.id, 0)
            msg = send_order(bot, order.text, order_type, order.chat_id, markup).result()
            if order_pin and msg:
                try:
                    bot.request.post(bot.base_url + '/pinChatMessage', {'chat_id': order.chat_id,
                                                                        'message_id': msg.message_id,
                                                                        'disable_notification': False})
                except TelegramError as err:
                    bot.logger.error(err.message)
        else:
            group = session.query(OrderGroup).filter_by(id=data['id']).first()
            for item in group.items:
                order = Order()
                order.text = order_text
                order.chat_id = item.chat_id
                order.date = datetime.now()
                msg = send_async(bot, chat_id=order.chat_id, text=MSG_ORDER_CLEARED_BY_HEADER + MSG_EMPTY).result()
                if msg:
                    order.confirmed_msg = msg.message_id
                else:
                    order.confirmed_msg = 0
                session.add(order)
                session.commit()
                markup = generate_ok_markup(order.id, 0)
                msg = send_order(bot, order.text, order_type, order.chat_id, markup).result().result()
                if order_pin and msg:
                    try:
                        bot.request.post(bot.base_url + '/pinChatMessage',
                                         {'chat_id': order.chat_id, 'message_id': msg.message_id,
                                          'disable_notification': False})
                    except TelegramError as err:
                        bot.logger.error(err.message)
        update.callback_query.answer(text=MSG_ORDER_SENT)
    elif data['t'] == QueryType.OrderOk.value:
        order = session.query(Order).filter_by(id=data['id']).first()
        if order is not None:
            squad = session.query(Squad).filter_by(chat_id=order.chat_id).first()
            if squad is not None:
                squad_member = session.query(SquadMember).filter_by(squad_id=squad.chat_id,
                                                                    user_id=update.callback_query.from_user.id).first()
                if squad_member is not None:
                    order_ok = session.query(OrderCleared).filter_by(order_id=data['id'],
                                                                     user_id=squad_member.user_id).first()
                    if order_ok is None and datetime.now() - order.date < timedelta(minutes=10):
                        order_ok = OrderCleared()
                        order_ok.order_id = data['id']
                        order_ok.user_id = update.callback_query.from_user.id
                        session.add(order_ok)
                        session.commit()
                        if order.confirmed_msg != 0:
                            confirmed = order.cleared
                            msg = MSG_ORDER_CLEARED_BY_HEADER
                            for confirm in confirmed:
                                msg += str(confirm.user) + '\n'
                            bot.editMessageText(msg, order.chat_id, order.confirmed_msg)
                        update.callback_query.answer(text=MSG_ORDER_CLEARED)
                    else:
                        update.callback_query.answer(text=MSG_ORDER_CLEARED_ERROR)
                else:
                    update.callback_query.answer(text=MSG_ORDER_CLEARED_ERROR)
            else:
                order_ok = session.query(OrderCleared).filter_by(order_id=data['id'],
                                                                 user_id=update.callback_query.from_user.id).first()
                if order_ok is None and datetime.now() - order.date < timedelta(minutes=10):
                    order_ok = OrderCleared()
                    order_ok.order_id = data['id']
                    order_ok.user_id = update.callback_query.from_user.id
                    session.add(order_ok)
                    session.commit()
                    update.callback_query.answer(text=MSG_ORDER_CLEARED)
                else:
                    update.callback_query.answer(text=MSG_ORDER_CLEARED_ERROR)
    elif data['t'] == QueryType.Orders.value:
        if 'txt' in data and len(data['txt']):
            if data['txt'] == Icons.LES.value:
                chat_data['order'] = Castle.LES.value
            elif data['txt'] == Icons.GORY.value:
                chat_data['order'] = Castle.GORY.value
            elif data['txt'] == Icons.SEA.value:
                chat_data['order'] = Castle.SEA.value
            else:
                chat_data['order'] = data['txt']
        markup = generate_order_chats_markup(session, chat_data['pin'] if 'pin' in chat_data else True)
        bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    elif data['t'] == QueryType.OrderGroup.value:
        if 'txt' in data and len(data['txt']):
            chat_data['order_type'] = MessageType.TEXT
            if data['txt'] == Icons.LES.value:
                chat_data['order'] = Castle.LES.value
            elif data['txt'] == Icons.GORY.value:
                chat_data['order'] = Castle.GORY.value
            elif data['txt'] == Icons.SEA.value:
                chat_data['order'] = Castle.SEA.value
            else:
                chat_data['order'] = data['txt']
        admin_user = session.query(Admin).filter(Admin.user_id == update.callback_query.from_user.id).all()
        markup = generate_order_groups_markup(session, admin_user, chat_data['pin'] if 'pin' in chat_data else True)
        bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    elif data['t'] == QueryType.OrderGroupManage.value:
        group = session.query(OrderGroup).filter_by(id=data['id']).first()
        markup = generate_group_manage(data['id'], session)
        bot.editMessageText(MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    elif data['t'] == QueryType.OrderGroupTriggerChat.value:
        group = session.query(OrderGroup).filter_by(id=data['id']).first()
        deleted = False
        for item in group.items:
            if item.chat_id == data['c']:
                session.delete(item)
                session.commit()
                deleted = True
        if not deleted:
            item = OrderGroupItem()
            item.group_id = group.id
            item.chat_id = data['c']
            session.add(item)
            session.commit()
        markup = generate_group_manage(data['id'], session)
        bot.editMessageText(MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    elif data['t'] == QueryType.OrderGroupAdd.value:
        chat_data['wait_group_name'] = True
        send_async(bot, chat_id=update.callback_query.message.chat.id,
                   text=MSG_ORDER_GROUP_NEW)
    elif data['t'] == QueryType.OrderGroupDelete.value:
        group = session.query(OrderGroup).filter_by(id=data['id']).first()
        session.delete(group)
        session.commit()
        bot.editMessageText(MSG_ORDER_GROUP_LIST,
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=generate_groups_manage(session))
    elif data['t'] == QueryType.OrderGroupList.value:
        bot.editMessageText(MSG_ORDER_GROUP_LIST,
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=generate_groups_manage(session))
    elif data['t'] == QueryType.ShowEquip.value:
        user = session.query(User).filter_by(id=data['id']).first()
        update.callback_query.answer(text=MSG_CLEARED)
        back = data['b'] if 'b' in data else False
        bot.editMessageText('{}\n🕑 Последнее обновление {}'.format(user.equip.equip, user.equip.date),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=generate_profile_buttons(user, back)
                            )
    elif data['t'] == QueryType.ShowStock.value:
        user = session.query(User).filter_by(id=data['id']).first()
        update.callback_query.answer(text=MSG_CLEARED)
        back = data['b'] if 'b' in data else False
        bot.editMessageText('{}\n🕑 Последнее обновление {}'.
                            format(user.stock.stock, user.stock.date.strftime("%Y-%m-%d %H:%M:%S")),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=generate_profile_buttons(user, back)
                            )
    elif data['t'] == QueryType.ShowHero.value:
        user = session.query(User).filter_by(id=data['id']).first()
        update.callback_query.answer(text=MSG_CLEARED)
        back = data['b'] if 'b' in data else False
        bot.editMessageText(fill_char_template(MSG_PROFILE_SHOW_FORMAT,
                                               user, user.character),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=generate_profile_buttons(user, back)
                            )
    elif data['t'] == QueryType.MemberList.value:
        squad = session.query(Squad).filter_by(chat_id=data['id']).first()
        markup = generate_squad_members(squad.members, session)
        bot.editMessageText(squad.squad_name,
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    elif data['t'] == QueryType.LeaveSquad.value:
        member = session.query(SquadMember).filter_by(user_id=data['id']).first()
        if member:
            squad = member.squad
            user = member.user
            session.delete(member)
            session.commit()
            admins = session.query(Admin).filter_by(admin_group=squad.chat_id).all()
            for adm in admins:
                if adm.user_id != update.callback_query.from_user.id:
                    send_async(bot, chat_id=adm.user_id,
                               text=MSG_SQUAD_LEAVED.format(user.character.name, squad.squad_name))
            send_async(bot, chat_id=member.squad_id,
                       text=MSG_SQUAD_LEAVED.format(user.character.name, squad.squad_name))
            send_async(bot, chat_id=member.user_id,
                       text=MSG_SQUAD_LEAVED.format(user.character.name, squad.squad_name))
            if data['id'] == update.callback_query.from_user.id:
                bot.editMessageText(MSG_SQUAD_LEAVED.format(user.character.name, squad.squad_name),
                                    update.callback_query.message.chat.id,
                                    update.callback_query.message.message_id)
            else:
                members = session.query(SquadMember).filter_by(squad_id=member.squad_id).all()
                bot.editMessageText(update.callback_query.message.text,
                                    update.callback_query.message.chat.id,
                                    update.callback_query.message.message_id,
                                    reply_markup=generate_fire_up(members))
        else:
            update.callback_query.answer(text='Этот пользователь уже выпилен из отряда, кнопка больше не работает =(')
    elif data['t'] == QueryType.RequestSquad.value:
        member = session.query(SquadMember).filter_by(user_id=update.callback_query.from_user.id).first()
        if member is None:
            member = SquadMember()
            member.user_id = update.callback_query.from_user.id
            member.squad_id = data['id']
            session.add(member)
            session.commit()
            admins = session.query(Admin).filter_by(admin_group=data['id']).all()
            usernames = ['@' + session.query(User).filter_by(id=admin.user_id).first().username for admin in admins]
            bot.editMessageText(MSG_SQUAD_REQUESTED.format(member.squad.squad_name, ', '.join(usernames)),
                                update.callback_query.message.chat.id,
                                update.callback_query.message.message_id)
            admins = session.query(Admin).filter_by(admin_group=member.squad.chat_id).all()
            for adm in admins:
                send_async(bot, chat_id=adm.user_id, text=MSG_SQUAD_REQUEST_NEW)
        else:
            markup = generate_leave_squad(user.id)
            bot.editMessageText(MSG_SQUAD_REQUEST_EXISTS,
                                update.callback_query.message.chat.id,
                                update.callback_query.message.message_id,
                                reply_markup=markup)
    elif data['t'] == QueryType.RequestSquadAccept.value:
        member = session.query(SquadMember).filter_by(user_id=data['id']).first()
        if member:
            member.approved = True
            session.add(member)
            session.commit()
            bot.editMessageText(MSG_SQUAD_REQUEST_ACCEPTED.format('@'+member.user.username),
                                update.callback_query.message.chat.id,
                                update.callback_query.message.message_id)
            send_async(bot, chat_id=member.user_id, text=MSG_SQUAD_REQUEST_ACCEPTED_ANSWER)
            send_async(bot, chat_id=member.squad_id, text=MSG_SQUAD_REQUEST_ACCEPTED.format('@'+member.user.username))
    elif data['t'] == QueryType.RequestSquadDecline.value:
        member = session.query(SquadMember).filter_by(user_id=data['id']).first()
        if member:
            bot.editMessageText(MSG_SQUAD_REQUEST_DECLINED.format('@' + member.user.username),
                                update.callback_query.message.chat.id,
                                update.callback_query.message.message_id)
            session.delete(member)
            session.commit()
            send_async(bot, chat_id=member.user_id, text=MSG_SQUAD_REQUEST_DECLINED_ANSWER)
    elif data['t'] == QueryType.InviteSquadAccept.value:
        if update.callback_query.from_user.id != data['id']:
            update.callback_query.answer(text='Пшёл вон!')
            return
        member = session.query(SquadMember).filter_by(user_id=data['id']).first()
        if member is None:
            member = SquadMember()
            member.user_id = user.id
            member.squad_id = update.callback_query.message.chat.id
            session.add(member)
            session.commit()
            member.approved = True
            session.add(member)
            session.commit()
            bot.editMessageText(MSG_SQUAD_ADD_ACCEPTED.format('@'+user.username),
                                update.callback_query.message.chat.id,
                                update.callback_query.message.message_id)
    elif data['t'] == QueryType.InviteSquadDecline.value:
        if update.callback_query.from_user.id != data['id']:
            update.callback_query.answer(text='Пшёл вон!')
            return
        user = session.query(User).filter_by(id=data['id']).first()
        bot.editMessageText(MSG_SQUAD_REQUEST_DECLINED.format('@' + user.username),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id)
    elif data['t'] == QueryType.TriggerOrderPin.value:
        if 'pin' in chat_data:
            chat_data['pin'] = not chat_data['pin']
        else:
            chat_data['pin'] = False
        if data['g']:
            admin_user = session.query(Admin).filter(Admin.user_id == update.callback_query.from_user.id).all()
            markup = generate_order_groups_markup(session, admin_user, chat_data['pin'] if 'pin' in chat_data else True)
            bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                                update.callback_query.message.chat.id,
                                update.callback_query.message.message_id,
                                reply_markup=markup)
        else:
            markup = generate_order_chats_markup(session, chat_data['pin'] if 'pin' in chat_data else True)
            bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                                update.callback_query.message.chat.id,
                                update.callback_query.message.message_id,
                                reply_markup=markup)
    elif data['t'] == QueryType.SquadList.value:
        admin = session.query(Admin).filter_by(user_id=update.callback_query.from_user.id).all()
        global_adm = False
        for adm in admin:
            if adm.admin_type <= AdminType.FULL.value:
                global_adm = True
                break
        if global_adm:
            squads = session.query(Squad).all()
        else:
            group_ids = []
            for adm in admin:
                group_ids.append(adm.admin_group)
            squads = session.query(Squad).filter(Squad.chat_id in group_ids).all()
        markup = generate_squad_list(squads, session)
        bot.editMessageText(MSG_SQUAD_LIST,
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    elif data['t'] == QueryType.GroupDelete.value:
        squad = session.query(Squad).filter_by(chat_id=data['gid']).first()
        if squad is not None:
            for member in squad.members:
                session.delete(member)
            session.delete(squad)
            session.commit()
            send_async(bot, chat_id=data['gid'], text=MSG_SQUAD_DELETE)
        msg = MSG_GROUP_STATUS_CHOOSE_CHAT
        squads = session.query(Squad).all()
        inline_keys = []
        for squad in squads:
            inline_keys.append(InlineKeyboardButton(squad.squad_name,
                                                    callback_data=json.dumps({'t': QueryType.GroupInfo.value,
                                                                              'id': squad.chat_id})))
        inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
