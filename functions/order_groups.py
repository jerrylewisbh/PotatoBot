from telegram import Bot, Update

from core.decorators import command_handler
from core.enums import Icons, Castle
from core.texts import MSG_ORDER_GROUP_LIST, MSG_ORDER_GROUP_NEW, MSG_ORDER_GROUP_CONFIG_HEADER, MSG_ORDER_SEND_HEADER
from core.types import AdminType, OrderGroup, Session, User, OrderGroupItem, MessageType, Admin
from core.utils import send_async
from functions.inline_markup import generate_groups_manage, generate_group_manage, generate_order_groups_markup, \
    generate_group_info

Session()


@command_handler(
    min_permission=AdminType.FULL,
)
def group_list(bot: Bot, update: Update, user: User):
    markup = generate_groups_manage()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_ORDER_GROUP_LIST, reply_markup=markup)


@command_handler(
    min_permission=AdminType.FULL,
)
def add_group(bot: Bot, update: Update, user: User, chat_data):
    chat_data['wait_group_name'] = False
    group = OrderGroup()
    group.name = update.message.text
    Session.add(group)
    Session.commit()
    markup = generate_group_manage(group.id)
    send_async(bot, chat_id=update.message.chat.id,
               text=MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name), reply_markup=markup)


def order_group_list(bot, update):
    bot.editMessageText(MSG_ORDER_GROUP_LIST,
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=generate_groups_manage())


def order_group_delete(bot, update, user, data):
    group = Session.query(OrderGroup).filter_by(id=data['id']).first()
    Session.delete(group)
    Session.commit()
    bot.editMessageText(MSG_ORDER_GROUP_LIST,
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=generate_groups_manage())


def order_group_add(bot: Bot, update: Update, user: User, data: dict, chat_data: dict):
    chat_data['wait_group_name'] = True
    send_async(bot, chat_id=update.callback_query.message.chat.id,
               text=MSG_ORDER_GROUP_NEW)


def order_group_tirgger_chat(bot, update, user, data):
    group = Session.query(OrderGroup).filter_by(id=data['id']).first()
    deleted = False
    for item in group.items:
        if item.chat_id == data['c']:
            Session.delete(item)
            Session.commit()
            deleted = True
    if not deleted:
        item = OrderGroupItem()
        item.group_id = group.id
        item.chat_id = data['c']
        Session.add(item)
        Session.commit()
    markup = generate_group_manage(data['id'])
    bot.editMessageText(MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=markup)


def order_group_manage(bot, update, user, data):
    group = Session.query(OrderGroup).filter_by(id=data['id']).first()
    markup = generate_group_manage(data['id'])
    bot.editMessageText(MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=markup)


def order_group(bot: Bot, update: Update, user: User, data: dict, chat_data: dict):
    chat_data['order_wait'] = False
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
    admin_user = Session.query(Admin).filter(Admin.user_id == update.callback_query.from_user.id).all()
    markup = generate_order_groups_markup(admin_user, chat_data['pin'] if 'pin' in chat_data else True,
                                          chat_data['btn'] if 'btn' in chat_data else True)
    bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=markup)


def group_info(bot, update, user, data):
    msg, inline_markup = generate_group_info(data['id'])
    bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                        reply_markup=inline_markup)
