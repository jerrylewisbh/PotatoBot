import json
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from core.types import User, Group, Admin, session, admin
from core.utils import send_async
from core.functions.admins import del_adm
from enum import Enum
from core.enums import Castle, Icons
import logging

logger = logging.getLogger('MyApp')


class QueryType(Enum):
    GroupList = 0
    GroupInfo = 1
    DelAdm = 2
    Order = 3
    OrderOk = 4
    Orders = 5


@admin()
def send_status(bot: Bot, update: Update):
    msg = 'Выбери чат'
    groups = session.query(Group).all()
    inline_keys = []
    for group in groups:
        inline_keys.append(InlineKeyboardButton(group.title, callback_data=json.dumps({'t': QueryType.GroupInfo.value, 'id': group.id})))
    inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
    send_async(bot, chat_id=update.message.chat.id, text=msg, reply_markup=inline_markup)


def generate_group_info(group_id):
    group = session.query(Group).filter(Group.id == group_id).first()
    admins = session.query(Admin).filter(Admin.admin_group == group_id).all()
    msg = 'Группа: ' + group.title + '\n\n' \
                                     'Админы:\n'
    adm_del_keys = []
    for adm in admins:
        user = session.query(User).filter_by(id=adm.user_id).first()
        msg += '{} @{} {} {}\n'.format(user.id, user.username, user.first_name, user.last_name)
        adm_del_keys.append([InlineKeyboardButton('Разжаловать {} {}'.format(user.first_name, user.last_name),
                                                  callback_data=json.dumps(
                                                      {'t': QueryType.DelAdm.value, 'uid': user.id,
                                                       'gid': group_id}))])
    msg += '\n' \
           'Приветствие: {}\n' \
           'Триггерят все: {}'.format('Включено' if group.welcome_enabled else 'Выключено',
                                      'Включено' if group.allow_trigger_all else 'Выключено')
    adm_del_keys.append([InlineKeyboardButton('Назад', callback_data=json.dumps(
        {'t': QueryType.GroupList.value}))])
    inline_markup = InlineKeyboardMarkup(adm_del_keys)
    return msg, inline_markup


def generate_flag_orders():
    flag_btns = []
    flag_btns.append([InlineKeyboardButton(Castle.BLACK.value, callback_data=json.dumps(
        {'t': QueryType.Orders.value, 'txt': Castle.BLACK.value})),
                      InlineKeyboardButton(Castle.WHITE.value, callback_data=json.dumps(
        {'t': QueryType.Orders.value, 'txt': Castle.WHITE.value})),
                      InlineKeyboardButton(Castle.BLUE.value, callback_data=json.dumps(
        {'t': QueryType.Orders.value, 'txt': Castle.BLUE.value}))])
    flag_btns.append([InlineKeyboardButton(Castle.YELLOW.value, callback_data=json.dumps(
        {'t': QueryType.Orders.value, 'txt': Castle.YELLOW.value})),
                      InlineKeyboardButton(Castle.RED.value, callback_data=json.dumps(
        {'t': QueryType.Orders.value, 'txt': Castle.RED.value})),
                      InlineKeyboardButton(Castle.DUSK.value, callback_data=json.dumps(
        {'t': QueryType.Orders.value, 'txt': Castle.DUSK.value}))])
    flag_btns.append([InlineKeyboardButton(Castle.MINT.value, callback_data=json.dumps(
        {'t': QueryType.Orders.value, 'txt': Castle.MINT.value})),
                      InlineKeyboardButton(Castle.GORY.value, callback_data=json.dumps(
        {'t': QueryType.Orders.value, 'txt': Icons.GORY.value})),
                      InlineKeyboardButton(Castle.LES.value, callback_data=json.dumps(
        {'t': QueryType.Orders.value, 'txt': Icons.LES.value}))])
    inline_markup = InlineKeyboardMarkup(flag_btns)
    return inline_markup


def generate_order_group_markup():
    groups = session.query(Group).all()
    inline_keys = []
    for group in groups:
        inline_keys.append(InlineKeyboardButton(group.title, callback_data=json.dumps(
            {'t': QueryType.Order.value, 'id': group.id})))
    inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
    return inline_markup


def generate_ok_markup(group_id):
    inline_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Принято!', callback_data=json.dumps(
            {'t': QueryType.OrderOk.value, 'id': group_id}))]])
    return inline_markup


def callback_query(bot: Bot, update: Update, chat_data: dict):
    data = json.loads(update.callback_query.data)
    logger.warning(data)
    if data['t'] == QueryType.GroupList.value:
        msg = 'Выбери чат'
        groups = session.query(Group).all()
        inline_keys = []
        for group in groups:
            inline_keys.append(InlineKeyboardButton(group.title, callback_data=json.dumps(
                {'t': QueryType.GroupInfo.value, 'id': group.id})))
        inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    if data['t'] == QueryType.GroupInfo.value:
        msg, inline_markup = generate_group_info(data['id'])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    if data['t'] == QueryType.DelAdm.value:
        user = session.query(User).filter_by(id=data['uid']).first()
        del_adm(bot, data['gid'], user)
        msg, inline_markup = generate_group_info(data['gid'])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    if data['t'] == QueryType.Order.value:
        markup = generate_ok_markup(data['id'])
        send_async(bot, chat_id=data['id'], text=chat_data['order'], reply_markup=markup)
    if data['t'] == QueryType.OrderOk.value:
        if 'order_ok' not in chat_data.keys():
            chat_data['order_ok'] = 0
        chat_data['order_ok'] += 1
        logger.warning('{}: {}'.format(update.callback_query.message.chat.title, chat_data['order_ok']))
    if data['t'] == QueryType.Orders.value:
        if data['txt'] == Icons.LES.value:
            chat_data['order'] = Castle.LES.value
        elif data['txt'] == Icons.GORY.value:
            chat_data['order'] = Castle.GORY.value
        else:
            chat_data['order'] = data['txt']
        markup = generate_order_group_markup()
        bot.editMessageText('Куда слать?', update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=markup)
