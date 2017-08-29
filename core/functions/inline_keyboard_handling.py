import json

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, TelegramError
from telegram.ext.dispatcher import run_async

from core.template import fill_char_template
from core.types import User, Group, Admin, Session, admin, Order, OrderGroup, OrderGroupItem, OrderCleared, Squad, \
    Character, Session, SquadMember, MessageType
from core.utils import send_async, update_group, add_user
from core.functions.admins import del_adm
from enum import Enum
from core.enums import Castle, Icons
import logging
from core.types import AdminType
from datetime import datetime, timedelta
from core.texts import *
from multiprocessing.pool import ThreadPool
from json import loads

logger = logging.getLogger('MyApp')


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


@admin()
def send_status(bot: Bot, update: Update):
    session = Session()
    msg = MSG_GROUP_STATUS_CHOOSE_CHAT
    squads = session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        inline_keys.append(InlineKeyboardButton(squad.squad_name,
                                                callback_data=json.dumps({'t': QueryType.GroupInfo.value,
                                                                          'id': squad.chat_id})))
    inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
    send_async(bot, chat_id=update.message.chat.id, text=msg, reply_markup=inline_markup)


def generate_group_info(group_id):
    session = Session()
    group = session.query(Group).filter(Group.id == group_id).first()
    admins = session.query(Admin).filter(Admin.admin_group == group_id).all()
    adm_msg = ''
    adm_del_keys = []
    for adm in admins:
        user = session.query(User).filter_by(id=adm.user_id).first()
        adm_msg += MSG_GROUP_STATUS_ADMIN_FORMAT.format(user.id, user.username or '', user.first_name or '', user.last_name or '')
        adm_del_keys.append([InlineKeyboardButton(MSG_GROUP_STATUS_DEL_ADMIN.format(user.first_name or '', user.last_name or ''),
                                                  callback_data=json.dumps(
                                                      {'t': QueryType.DelAdm.value, 'uid': user.id,
                                                       'gid': group_id}))])
    msg = MSG_GROUP_STATUS.format(group.title,
                                  adm_msg,
                                  MSG_ON if group.welcome_enabled else MSG_OFF,
                                  MSG_ON if group.allow_trigger_all else MSG_OFF,
                                  MSG_ON if len(group.squad) and group.squad[0].thorns_enabled else MSG_OFF)
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


def generate_order_chats_markup(bot: Bot):
    session = Session()
    squads = session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        inline_keys.append([InlineKeyboardButton(squad.squad_name, callback_data=json.dumps(
            {'t': QueryType.Order.value, 'g': False, 'id': squad.chat_id}))])
    inline_markup = InlineKeyboardMarkup(inline_keys)
    return inline_markup


def generate_order_groups_markup(bot: Bot, admin_user: list=None):
    session = Session()
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
            inline_markup = InlineKeyboardMarkup(inline_keys)
            return inline_markup
    groups = session.query(OrderGroup).all()
    inline_keys = []
    for group in groups:
        inline_keys.append([InlineKeyboardButton(group.name, callback_data=json.dumps(
            {'t': QueryType.Order.value, 'g': True, 'id': group.id}))])
    inline_keys.append([InlineKeyboardButton(MSG_ORDER_TO_SQUADS, callback_data=json.dumps(
        {'t': QueryType.Orders.value}))])
    inline_markup = InlineKeyboardMarkup(inline_keys)
    return inline_markup


def generate_ok_markup(order_id, count):
    inline_markup = InlineKeyboardMarkup([[InlineKeyboardButton(MSG_ORDER_ACCEPT.format(count),
                                                                callback_data=json.dumps(
                                                                    {'t': QueryType.OrderOk.value, 'id': order_id}))]])
    return inline_markup


def generate_groups_manage():
    session = Session()
    groups = session.query(OrderGroup).all()
    inline_keys = []
    for group in groups:
        inline_keys.append([InlineKeyboardButton(group.name, callback_data=json.dumps(
            {'t': QueryType.OrderGroupManage.value, 'id': group.id}))])
    inline_keys.append([InlineKeyboardButton(MSG_ORDER_GROUP_ADD, callback_data=json.dumps(
        {'t': QueryType.OrderGroupAdd.value}))])
    return InlineKeyboardMarkup(inline_keys)


def generate_group_manage(group_id):
    session = Session()
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


def generate_profile_buttons(user):
    inline_keys = []
    inline_keys.append([InlineKeyboardButton('🏅Герой', callback_data=json.dumps(
        {'t': QueryType.ShowHero.value, 'id': user.id}))])
    if user.stock:
        inline_keys.append([InlineKeyboardButton('📦Склад', callback_data=json.dumps(
            {'t': QueryType.ShowStock.value, 'id': user.id}))])
    if user.equip:
        inline_keys.append([InlineKeyboardButton('🎽Экипировка', callback_data=json.dumps(
            {'t': QueryType.ShowEquip.value, 'id': user.id}))])
    return InlineKeyboardMarkup(inline_keys)


def generate_squad_list_key(squad):
    session = Session()
    attack = 0
    defence = 0
    members = session.query(SquadMember).filter_by(squad_id=squad.chat_id).all()
    for member in members:
        character = session.query(Character).filter_by(user_id=member.user_id).order_by(Character.date.desc()).limit(1).first()
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


def generate_squad_list(squads):
    inline_keys = []
    pool = ThreadPool(processes=10)
    threads = []
    for squad in squads:
        threads.append(pool.apply_async(generate_squad_list_key, (squad,)))
    for thread in threads:
        inline_keys.append(thread.get())
    return InlineKeyboardMarkup(inline_keys)


def generate_leave_squad(user_id):
    inline_keys = []
    inline_keys.append([InlineKeyboardButton('Выйти',
                        callback_data=json.dumps({'t': QueryType.LeaveSquad.value, 'id': user_id}))])
    return InlineKeyboardMarkup(inline_keys)


def generate_squad_request():
    session = Session()
    inline_keys = []
    squads = session.query(Squad).filter_by(hiring=True).all()
    for squad in squads:
        inline_keys.append([InlineKeyboardButton(squad.squad_name,
                                                 callback_data=json.dumps(
                                                     {'t': QueryType.RequestSquad.value, 'id': squad.chat_id}))])
    return InlineKeyboardMarkup(inline_keys)


def generate_squad_members(members):
    inline_keys = []
    for member in members:
        user = member.user
        character = user.character
        inline_keys.append([InlineKeyboardButton('{}: {}⚔ {}🛡'.format(user, character.attack, character.defence), callback_data=json.dumps(
            {'t': QueryType.ShowHero.value, 'id': member.user_id}))])
    return InlineKeyboardMarkup(inline_keys)


def generate_squad_request_answer(user_id):
    inline_keys = []
    inline_keys.append(InlineKeyboardButton('✅Принять',
                                            callback_data=json.dumps(
                                                {'t': QueryType.RequestSquadAccept.value, 'id': user_id})))
    inline_keys.append(InlineKeyboardButton('❌Отклонить',
                                            callback_data=json.dumps(
                                                {'t': QueryType.RequestSquadDecline.value, 'id': user_id})))
    return InlineKeyboardMarkup([inline_keys])


def generate_fire_up(members):
    inline_keys = []
    for member in members:
        inline_keys.append([InlineKeyboardButton('🔥{}: {}⚔ {}🛡'.format(member.user, member.user.character.attack,
                                                                       member.user.character.defence),
                                                 callback_data=json.dumps(
                                                     {'t': QueryType.LeaveSquad.value, 'id': member.user_id}))])


@run_async
def send_order(bot, order, order_type, chat_id, markup):
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


@run_async
def callback_query(bot: Bot, update: Update, chat_data: dict):
    session = Session()
    update_group(update.callback_query.message.chat)
    user = add_user(update.callback_query.from_user)
    data = json.loads(update.callback_query.data)
    logger.warning(data)
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
        msg, inline_markup = generate_group_info(data['id'])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    elif data['t'] == QueryType.DelAdm.value:
        del_adm(bot, data['gid'], user)
        msg, inline_markup = generate_group_info(data['gid'])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    elif data['t'] == QueryType.Order.value:
        if not data['g']:
            order = Order()
            order.text = chat_data['order']
            order.chat_id = data['id']
            order.date = datetime.now()
            order.confirmed_msg = 0
            session.add(order)
            session.commit()
            markup = generate_ok_markup(order.id, 0)
            msg = send_order(bot, order.text, chat_data['order_type'], order.chat_id, markup).result().result()
            try:
                bot.request.post(bot.base_url + '/pinChatMessage', {'chat_id': order.chat_id,
                                                                    'message_id': msg.message_id,
                                                                    'disable_notification': False})
            except:
                pass
        else:
            group = session.query(OrderGroup).filter_by(id=data['id']).first()
            for item in group.items:
                order = Order()
                order.text = chat_data['order']
                order.chat_id = item.chat_id
                order.date = datetime.now()
                order.confirmed_msg = 0
                session.add(order)
                session.commit()
                markup = generate_ok_markup(order.id, 0)
                msg = send_order(bot, order.text, chat_data['order_type'], order.chat_id, markup).result().result()
                try:
                    bot.request.post(bot.base_url + '/pinChatMessage',
                                     {'chat_id': order.chat_id, 'message_id': msg.message_id,
                                      'disable_notification': False})
                except:
                    pass
        update.callback_query.answer(text=MSG_ORDER_SENT)
    elif data['t'] == QueryType.OrderOk.value:
        order = session.query(Order).filter_by(id=data['id']).first()
        if order is not None:
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
        markup = generate_order_chats_markup(bot)
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
        markup = generate_order_groups_markup(bot, admin_user)
        bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    elif data['t'] == QueryType.OrderGroupManage.value:
        group = session.query(OrderGroup).filter_by(id=data['id']).first()
        markup = generate_group_manage(data['id'])
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
        markup = generate_group_manage(data['id'])
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
                            reply_markup=generate_groups_manage())
    elif data['t'] == QueryType.OrderGroupList.value:
        bot.editMessageText(MSG_ORDER_GROUP_LIST,
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=generate_groups_manage())
    elif data['t'] == QueryType.ShowEquip.value:
        user = session.query(User).filter_by(id=data['id']).first()
        update.callback_query.answer(text=MSG_CLEARED)
        bot.editMessageText('{}\n🕑 Последнее обновление {}'.format(user.equip.equip, user.equip.date),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=generate_profile_buttons(user))
    elif data['t'] == QueryType.ShowStock.value:
        user = session.query(User).filter_by(id=data['id']).first()
        update.callback_query.answer(text=MSG_CLEARED)
        bot.editMessageText('{}\n🕑 Последнее обновление {}'.format(user.stock.stock, user.stock.date.strftime("%Y-%m-%d %H:%M:%S")),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=generate_profile_buttons(user))
    elif data['t'] == QueryType.ShowHero.value:
        user = session.query(User).filter_by(id=data['id']).first()
        update.callback_query.answer(text=MSG_CLEARED)
        bot.editMessageText(fill_char_template(MSG_PROFILE_SHOW_FORMAT,
                                               user, user.character),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=generate_profile_buttons(user))
    elif data['t'] == QueryType.MemberList.value:
        squad = session.query(Squad).filter_by(chat_id=data['id']).first()
        markup = generate_squad_members(squad.members)
        bot.editMessageText(squad.squad_name,
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    elif data['t'] == QueryType.LeaveSquad.value:
        member = session.query(SquadMember).filter_by(user_id=data['id']).first()
        squad_id = member.squad_id
        if member:
            session.delete(member)
            session.commit()
            admins = session.query(Admin).filter_by(admin_group=member.squad.chat_id).all()
            for adm in admins:
                if adm.user_id != update.callback_query.from_user.id:
                    send_async(bot, chat_id=adm.user_id,
                               text=MSG_SQUAD_LEAVED.format(member.user.character.name, member.squad.squad_name))
            send_async(bot, chat_id=squad_id,
                       text=MSG_SQUAD_LEAVED.format(member.user.character.name, member.squad.squad_name))
            send_async(bot, chat_id=member.user_id,
                       text=MSG_SQUAD_LEAVED.format(member.user.character.name, member.squad.squad_name))
        if data['id'] == update.callback_query.from_user.id:
            bot.editMessageText(MSG_SQUAD_LEAVED.format(member.user.character.name, member.squad.squad_name),
                                update.callback_query.message.chat.id,
                                update.callback_query.message.message_id)
        else:
            members = session.query(SquadMember).filter_by(squad_id=squad_id).all()
            bot.editMessageText(update.callback_query.message.text,
                                update.callback_query.message.chat.id,
                                update.callback_query.message.message_id,
                                reply_markup=generate_fire_up(members))
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
            bot.editMessageText(MSG_SQUAD_REQUEST_ACCEPTED.format('@'+user.username),
                                update.callback_query.message.chat.id,
                                update.callback_query.message.message_id)
            send_async(bot, chat_id=member.user_id, text=MSG_SQUAD_REQUEST_ACCEPTED_ANSWER)
    elif data['t'] == QueryType.RequestSquadDecline.value:
        member = session.query(SquadMember).filter_by(user_id=data['id']).first()
        if member:
            bot.editMessageText(MSG_SQUAD_REQUEST_DECLINED.format('@' + member.user.username),
                                update.callback_query.message.chat.id,
                                update.callback_query.message.message_id)
            session.delete(member)
            session.commit()
            send_async(bot, chat_id=member.user_id, text=MSG_SQUAD_REQUEST_DECLINED_ANSWER)
