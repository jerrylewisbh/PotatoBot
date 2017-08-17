import json
import asyncio

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, TelegramError
from telegram.ext.dispatcher import run_async

from core.template import fill_char_template
from core.types import User, Group, Admin, session, admin, Order, OrderGroup, OrderGroupItem, OrderCleared, Squad, \
    with_session, Character, Session, SquadMember
from core.utils import send_async, update_group, add_user
from core.functions.admins import del_adm
from enum import Enum
from core.enums import Castle, Icons
import logging
from core.types import AdminType
from datetime import datetime, timedelta
from core.texts import *
from multiprocessing.pool import ThreadPool

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


def bot_in_chat(bot: Bot, group: Group):
    try:
        #bot.getChatMember(group.id, bot.id)
        return True
    except TelegramError as e:
        logger.warning(e.message)
        group.bot_in_group = False
        session.add(group)
        session.commit()
        return False


@admin()
def send_status(bot: Bot, update: Update):
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
    group = session.query(Group).filter(Group.id == group_id).first()
    admins = session.query(Admin).filter(Admin.admin_group == group_id).all()
    adm_msg = ''
    adm_del_keys = []
    for adm in admins:
        user = session.query(User).filter_by(id=adm.user_id).first()
        adm_msg += MSG_GROUP_STATUS_ADMIN_FORMAT.format(user.id, user.username, user.first_name, user.last_name)
        adm_del_keys.append([InlineKeyboardButton(MSG_GROUP_STATUS_DEL_ADMIN.format(user.first_name, user.last_name),
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
                      {'t': QueryType.OrderGroup.value, 'txt': Icons.LES.value}))]]
    inline_markup = InlineKeyboardMarkup(flag_btns)
    return inline_markup


def generate_order_chats_markup(bot: Bot):
    squads = session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        inline_keys.append([InlineKeyboardButton(squad.squad_name, callback_data=json.dumps(
            {'t': QueryType.Order.value, 'g': False, 'id': squad.chat_id}))])
    inline_markup = InlineKeyboardMarkup(inline_keys)
    return inline_markup


def generate_order_groups_markup(bot: Bot, admin_user: list=None):
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
    groups = session.query(OrderGroup).all()
    inline_keys = []
    for group in groups:
        inline_keys.append([InlineKeyboardButton(group.name, callback_data=json.dumps(
            {'t': QueryType.OrderGroupManage.value, 'id': group.id}))])
    inline_keys.append([InlineKeyboardButton(MSG_ORDER_GROUP_ADD, callback_data=json.dumps(
        {'t': QueryType.OrderGroupAdd.value}))])
    return InlineKeyboardMarkup(inline_keys)


def generate_group_manage(group_id):
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


def generate_squad_members(members):
    inline_keys = []
    for member in members:
        inline_keys.append([InlineKeyboardButton(repr(member.user), callback_data=json.dumps(
            {'t': QueryType.ShowHero.value, 'id': member.user_id}))])
    return InlineKeyboardMarkup(inline_keys)


@with_session
def callback_query(bot: Bot, update: Update, chat_data: dict):
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
            msg = send_async(bot, chat_id=order.chat_id, text=MSG_ORDER_CLEARED_BY_HEADER + MSG_ORDER_CLEARED_BY_DUMMY).result()
            order.confirmed_msg = msg.message_id
            session.add(order)
            session.commit()
            markup = generate_ok_markup(order.id, 0)
            msg = send_async(bot, chat_id=order.chat_id, text=order.text, reply_markup=markup).result()
            try:
                bot.request.post(bot.base_url + '/pinChatMessage', {'chat_id': order.chat_id, 'message_id': msg.message_id,
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
                msg = send_async(bot, chat_id=order.chat_id, text=MSG_ORDER_CLEARED_BY_HEADER + MSG_ORDER_CLEARED_BY_DUMMY).result()
                order.confirmed_msg = msg.message_id
                session.add(order)
                session.commit()
                markup = generate_ok_markup(order.id, 0)
                msg = send_async(bot, chat_id=order.chat_id, text=order.text, reply_markup=markup).result()
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
                # if order.confirmed_msg != 0:
                #     confirmed = session.query(OrderCleared).filter_by(order_id=order.id).all()
                #     msg = MSG_ORDER_CLEARED_BY_HEADER
                #     for confirm in confirmed:
                #         msg += '\n' + str(confirm.user)
                #     msg += MSG_ORDER_CLEARED_BY_DUMMY
                #     bot.editMessageText(msg, order.chat_id, order.confirmed_msg)
                update.callback_query.answer(text=MSG_ORDER_CLEARED)
            else:
                update.callback_query.answer(text=MSG_ORDER_CLEARED_ERROR)
    elif data['t'] == QueryType.Orders.value:
        if 'txt' in data and len(data['txt']):
            if data['txt'] == Icons.LES.value:
                chat_data['order'] = Castle.LES.value
            elif data['txt'] == Icons.GORY.value:
                chat_data['order'] = Castle.GORY.value
            else:
                chat_data['order'] = data['txt']
        markup = generate_order_chats_markup(bot)
        bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    elif data['t'] == QueryType.OrderGroup.value:
        if 'txt' in data and len(data['txt']):
            if data['txt'] == Icons.LES.value:
                chat_data['order'] = Castle.LES.value
            elif data['txt'] == Icons.GORY.value:
                chat_data['order'] = Castle.GORY.value
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
