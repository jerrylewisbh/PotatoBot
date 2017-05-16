import json
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from core.types import User, Group, Admin, session, admin
from core.utils import send_async
from core.functions.admins import del_adm
from enum import Enum
import logging

logger = logging.getLogger('MyApp')


class QueryType(Enum):
    GroupList = 0
    GroupInfo = 1
    DelAdm = 2
    Order = 3


@admin()
def send_status(bot: Bot, update: Update):
    msg = 'Выбери чат'
    groups = session.query(Group).all()
    inline_keys = []
    for group in groups:
        inline_keys.append(InlineKeyboardButton(group.title, callback_data=json.dumps({'type': QueryType.GroupInfo.value, 'id': group.id})))
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
                                                      {'type': QueryType.DelAdm.value, 'uid': user.id,
                                                       'gid': group_id}))])
    msg += '\n' \
           'Приветствие: {}\n' \
           'Триггерят все: {}'.format('Включено' if group.welcome_enabled else 'Выключено',
                                      'Включено' if group.allow_trigger_all else 'Выключено')
    adm_del_keys.append([InlineKeyboardButton('Назад', callback_data=json.dumps(
        {'type': QueryType.GroupList.value}))])
    inline_markup = InlineKeyboardMarkup(adm_del_keys)
    return msg, inline_markup


def generate_order_group_markup():
    groups = session.query(Group).all()
    inline_keys = []
    for group in groups:
        inline_keys.append(InlineKeyboardButton(group.title, callback_data=json.dumps(
            {'type': QueryType.Order.value, 'id': group.id})))
    inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
    return inline_markup


def callback_query(bot: Bot, update: Update, chat_data):
    data = json.loads(update.callback_query.data)
    logger.warning(data)
    if data['type'] == QueryType.GroupList.value:
        msg = 'Выбери чат'
        groups = session.query(Group).all()
        inline_keys = []
        for group in groups:
            inline_keys.append(InlineKeyboardButton(group.title, callback_data=json.dumps(
                {'type': QueryType.GroupInfo.value, 'id': group.id})))
        inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    if data['type'] == QueryType.GroupInfo.value:
        msg, inline_markup = generate_group_info(data['id'])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    if data['type'] == QueryType.DelAdm.value:
        user = session.query(User).filter_by(id=data['uid']).first()
        del_adm(bot, data['gid'], user)
        msg, inline_markup = generate_group_info(data['gid'])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    if data['type'] == QueryType.Order.value:
        send_async(bot, chat_id=data['id'], text=chat_data['order'])
