import json
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from core.types import User, Group, WelcomeMsg, Admin, session
from enum import Enum


class QueryType(Enum):
    GroupList = 0
    GroupInfo = 1
    DelAdm = 2


def callback_query(bot: Bot, update: Update):
    data = json.loads(update.callback_query.data)
    if data['type'] == 'group_list':
        msg = 'Выбери чат'
        groups = session.query(Group).all()
        inline_keys = []
        for group in groups:
            inline_keys.append(InlineKeyboardButton(group.title, callback_data=json.dumps(
                {'type': 'group_info', 'id': str(group.id)})))
        inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    if data['type'] == 'group_info':
        group = session.query(Group).filter(Group.id == data['id']).first()
        admins = session.query(Admin).filter(Admin.admin_group == data['id']).all()
        welcome = session.query(WelcomeMsg).filter(WelcomeMsg.chat_id == data['id']).first()
        msg = 'Группа: ' + group.title + '\n\n' \
              'Админы:\n'
        adm_del_keys = []
        for adm in admins:
            user = session.query(User).filter_by(id=adm.user_id).first()
            msg += '{} @{} {} {}\n'.format(user.id, user.username, user.first_name, user.last_name)
            adm_del_keys.append(InlineKeyboardButton('Разжаловать {} {}'.format(user.first_name, user.last_name) ,
                                                     callback_data=json.dumps(
                                                     {'type': 'del_adm', 'user_id': user.id, 'group_id': data['id']})))
        msg += '\n' \
               'Приветствие: {}\n' \
               'Триггерят все: {}'.format('Включено' if welcome.enabled else 'Выключено',
                                          'Включено' if welcome.allow_trigger_all else 'Выключено')
        adm_del_keys.extend([InlineKeyboardButton('Назад', callback_data=json.dumps(
                {'type': 'group_list'}))])
        inline_markup = InlineKeyboardMarkup([adm_del_keys])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    if data['type'] == 'del_adm':
        admin = session.query(Admin).filter(Admin.admin_group == data['group_id'],
                                             Admin.user_id == data['user_id']).first()
        session.delete(admin)
        session.commit()
        group = session.query(Group).filter(Group.id == data['group_id']).first()
        admins = session.query(Admin).filter(Admin.admin_group == data['group_id']).all()
        welcome = session.query(WelcomeMsg).filter(WelcomeMsg.chat_id == data['group_id']).first()
        msg = 'Группа: ' + group.title + '\n\n' \
              'Админы:\n'
        for adm in admins:
            user = session.query(User).filter_by(id=adm.user_id).first()
            msg += '{} @{} {} {}\n'.format(user.id, user.username, user.first_name, user.last_name)
        msg += '\n' \
               'Приветствие: {}\n' \
               'Триггерят все: {}'.format('Включено' if welcome.enabled else 'Выключено',
                                          'Включено' if welcome.allow_trigger_all else 'Выключено')
        inline_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Назад', callback_data=json.dumps(
            {'type': 'group_list'}))]])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)