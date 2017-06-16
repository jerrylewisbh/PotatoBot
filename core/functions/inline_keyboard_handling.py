import json
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, TelegramError
from core.types import User, Group, Admin, session, admin, Order, OrderGroup, OrderGroupItem, OrderCleared, Squad
from core.utils import send_async, update_group, add_user
from core.functions.admins import del_adm
from enum import Enum
from core.enums import Castle, Icons
import logging
from core.types import AdminType
from datetime import datetime, timedelta

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
    msg = 'Выбери чат'
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
    if len(group.squad) == 1:
        msg += '\nТернии: {}'.format('Включены' if group.squad[0].thorns_enabled else 'Выключены')
    adm_del_keys.append([InlineKeyboardButton('🔙Назад', callback_data=json.dumps(
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
            if adm.admin_type == AdminType.FULL.value:
                group_adm = False
                break
        if group_adm:
            inline_keys = []
            for adm in admin_user:
                group = session.query(Group).filter_by(id=adm.admin_group).first()
                inline_keys.append([InlineKeyboardButton(group.title, callback_data=json.dumps(
                    {'t': QueryType.Order.value, 'g': False, 'id': group.id}))])
            inline_markup = InlineKeyboardMarkup(inline_keys)
            return inline_markup
    groups = session.query(OrderGroup).all()
    inline_keys = []
    for group in groups:
        inline_keys.append([InlineKeyboardButton(group.name, callback_data=json.dumps(
            {'t': QueryType.Order.value, 'g': True, 'id': group.id}))])
    inline_keys.append([InlineKeyboardButton('По отрядам', callback_data=json.dumps(
        {'t': QueryType.Orders.value}))])
    inline_markup = InlineKeyboardMarkup(inline_keys)
    return inline_markup


def generate_ok_markup(order_id, count):
    inline_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Принято! ({})'.format(count),
                                                                callback_data=json.dumps(
                                                                    {'t': QueryType.OrderOk.value, 'id': order_id}))]])
    return inline_markup


def generate_groups_manage():
    groups = session.query(OrderGroup).all()
    inline_keys = []
    for group in groups:
        inline_keys.append([InlineKeyboardButton(group.name, callback_data=json.dumps(
            {'t': QueryType.OrderGroupManage.value, 'id': group.id}))])
    inline_keys.append([InlineKeyboardButton('➕Добавить группу', callback_data=json.dumps(
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
        inline_keys.append([InlineKeyboardButton(('✅' if in_group else '❌') +
                                                 squad.squad_name, callback_data=json.dumps(
            {'t': QueryType.OrderGroupTriggerChat.value, 'id': group_id, 'c': squad.chat_id}))])
    inline_keys.append([InlineKeyboardButton('🔥🚨Удалить группу🚨🔥', callback_data=json.dumps(
        {'t': QueryType.OrderGroupDelete.value, 'id': group_id}))])
    inline_keys.append([InlineKeyboardButton('🔙Назад', callback_data=json.dumps(
        {'t': QueryType.OrderGroupList.value}))])
    return InlineKeyboardMarkup(inline_keys)


def callback_query(bot: Bot, update: Update, chat_data: dict):
    update_group(update.callback_query.message.chat)
    add_user(update.callback_query.from_user)
    data = json.loads(update.callback_query.data)
    logger.warning(data)
    if data['t'] == QueryType.GroupList.value:
        msg = 'Выбери чат'
        groups = session.query(Group).filter_by(bot_in_group=True).all()
        inline_keys = []
        for group in groups:
            if bot_in_chat(bot, group):
                inline_keys.append(InlineKeyboardButton(group.title, callback_data=json.dumps(
                    {'t': QueryType.GroupInfo.value, 'id': group.id})))
        inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    elif data['t'] == QueryType.GroupInfo.value:
        msg, inline_markup = generate_group_info(data['id'])
        bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=inline_markup)
    elif data['t'] == QueryType.DelAdm.value:
        user = session.query(User).filter_by(id=data['uid']).first()
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
            msg = send_async(bot, chat_id=order.chat_id, text="Приказ выполнили:").result()
            order.confirmed_msg = msg.message_id
            session.add(order)
            session.commit()
            markup = generate_ok_markup(order.id, 0)
            send_async(bot, chat_id=order.chat_id, text=order.text, reply_markup=markup)
        else:
            group = session.query(OrderGroup).filter_by(id=data['id']).first()
            for item in group.items:
                order = Order()
                order.text = chat_data['order']
                order.chat_id = item.chat_id
                order.date = datetime.now()
                msg = send_async(bot, chat_id=order.chat_id, text="Приказ выполнили:").result()
                order.confirmed_msg = msg.message_id
                session.add(order)
                session.commit()
                markup = generate_ok_markup(order.id, 0)
                send_async(bot, chat_id=order.chat_id, text=order.text, reply_markup=markup)
            send_async(bot, chat_id=update.callback_query.message.chat.id,
                       text='Отправлено в {} отрядов'.format(len(group.items)))
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
                if order.confirmed_msg != 0:
                    confirmed = session.query(OrderCleared).filter_by(order_id=order.id).all()
                    msg = 'Приказ выполнили:\n'
                    for confirm in confirmed:
                        msg += str(confirm.user) + '\n'
                    bot.editMessageText(msg, order.chat_id, order.confirmed_msg)
            count = session.query(OrderCleared).filter_by(order_id=data['id']).count()
            bot.editMessageText(update.callback_query.message.text,
                                update.callback_query.message.chat.id,
                                update.callback_query.message.message_id,
                                reply_markup=generate_ok_markup(data['id'], count))
    elif data['t'] == QueryType.Orders.value:
        if 'txt' in data and len(data['txt']):
            if data['txt'] == Icons.LES.value:
                chat_data['order'] = Castle.LES.value
            elif data['txt'] == Icons.GORY.value:
                chat_data['order'] = Castle.GORY.value
            else:
                chat_data['order'] = data['txt']
        markup = generate_order_chats_markup(bot)
        bot.editMessageText('Приказ: {}\nКуда слать?'.format(chat_data['order']),
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
        bot.editMessageText('Приказ: {}\nКуда слать?'.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    elif data['t'] == QueryType.OrderGroupManage.value:
        group = session.query(OrderGroup).filter_by(id=data['id']).first()
        markup = generate_group_manage(data['id'])
        bot.editMessageText('Настройки группы {}'.format(group.name),
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
        bot.editMessageText('Настройки группы {}'.format(group.name),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    elif data['t'] == QueryType.OrderGroupAdd.value:
        chat_data['wait_group_name'] = True
        send_async(bot, chat_id=update.callback_query.message.chat.id,
                   text='Напиши мне название новой группы отрядов')
    elif data['t'] == QueryType.OrderGroupDelete.value:
        group = session.query(OrderGroup).filter_by(id=data['id']).first()
        session.delete(group)
        session.commit()
        bot.editMessageText('Список групп',
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=generate_groups_manage())
    elif data['t'] == QueryType.OrderGroupList.value:
        bot.editMessageText('Список групп',
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=generate_groups_manage())
