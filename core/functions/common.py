from telegram import Update, Bot, ParseMode
import logging
from core.functions.triggers import trigger_decorator
from core.types import AdminType, Admin, Stock, admin, session
from core.utils import send_async
from core.functions.reply_markup import generate_standard_markup
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class StockType(Enum):
    Stock = 0
    TradeBot = 1


def error(bot: Bot, update, error, **kwargs):
    """ Error handling """
    logger.error("An error (%s) occurred: %s"
                 % (type(error), error.message))


def start(bot: Bot, update: Update):
    if update.message.chat.type == 'private':
        send_async(bot, chat_id=update.message.chat.id, text='Привет')


@admin()
def admin_panel(bot: Bot, update: Update):
    if update.message.chat.type == 'private':
        send_async(bot, chat_id=update.message.chat.id, text='Да здравствует админ!', reply_markup=generate_standard_markup())


@admin()
def kick(bot: Bot, update: Update):
    bot.leave_chat(update.message.chat.id)


@trigger_decorator
def help_msg(bot: Bot, update):
    admin_user = session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
    global_adm = False
    for adm in admin_user:
        if adm.admin_type == AdminType.FULL.value:
            global_adm = True
            break
    if global_adm:
        send_async(bot, chat_id=update.message.chat.id, text='Команды приветствия:\n'
                                                             '/enable_welcome - Включить приветствие\n'
                                                             '/disable_welcome - Выключить приветствие\n'
                                                             '/set_welcome <текст> - Установить текст приветствия. '
                                                             'Может содержать %username% - будет заменено на @username, '
                                                             'если не установлено на Имя Фамилия, %first_name% - на имя, '
                                                             '%last_name% - на фамилию, %id% - на id\n'
                                                             '/show_welcome - Показать текущий текст приветствия для '
                                                             'данного чата'
                                                             '\n\n'
                                                             'Команды триггеров:\n'
                                                             '/set_trigger <триггер>::<сообщение> - Установить сообщение, '
                                                             'которое бот будет кидать по триггеру.\n'
                                                             '/add_trigger <триггер>::<сообщение> - Добавляет сообщение, '
                                                             'которое бот будет кидать по триггеру, но не заменяет старый.\n'
                                                             '/del_trigger <триггер> - Удалить соответствующий триггер\n'
                                                             '/list_triggers - Показать все существующие триггеры'
                                                             '\n\n'
                                                             'Команды глобаладмина:\n'
                                                             '/add_admin <юзернэйм> - Добавить админа для текущего чата\n'
                                                             '/del_admin <юзернэйм> - Забрать привелегии у админа текущего '
                                                             'чата\n'
                                                             '/list_admins - Показать список местных админов\n'
                                                             '/enable_trigger - Разрешить триггерить всем в группе\n'
                                                             '/disable_trigger - Запретить триггерить всем в группе')
    elif len(admin_user) != 0:
        send_async(bot, chat_id=update.message.chat.id, text='Команды приветствия:\n'
                                                             '/enable_welcome - Включить приветствие\n'
                                                             '/disable_welcome - Выключить приветствие\n'
                                                             '/set_welcome <текст> - Установить текст приветствия. '
                                                             'Может содержать %username% - будет заменено на @username, '
                                                             'если не установлено на Имя Фамилия, %first_name% - на имя, '
                                                             '%last_name% - на фамилию, %id% - на id\n'
                                                             '/show_welcome - Показать текущий текст приветствия для '
                                                             'данного чата'
                                                             '\n\n'
                                                             'Команды триггеров:\n'
                                                             '/add_trigger <триггер>::<сообщение> - Добавляет сообщение, '
                                                             'которое бот будет кидать по триггеру, но не заменяет старый.\n'
                                                             '/list_triggers - Показать все существующие триггеры\n'
                                                             '/enable_trigger - Разрешить триггерить всем в группе\n'
                                                             '/disable_trigger - Запретить триггерить всем в группе')
    else:
        send_async(bot, chat_id=update.message.chat.id, text='Команды триггеров:\n'
                                                             '/list_triggers - Показать все существующие триггеры')


@admin(adm_type=AdminType.GROUP)
def ping(bot: Bot, update: Update):
    send_async(bot, chat_id=update.message.chat.id, text='Иди освежись, @' + update.message.from_user.username + '!')


def get_diff(dict_one, dict_two):
    resource_diff_add = {}
    resource_diff_del = {}
    for key, val in dict_one.items():
        if key in dict_two:
            diff_count = dict_one[key] - dict_two[key]
            if diff_count > 0:
                resource_diff_add[key] = diff_count
            elif diff_count < 0:
                resource_diff_del[key] = diff_count
        else:
            resource_diff_add[key] = val
    for key, val in dict_two.items():
        if key not in dict_one:
            resource_diff_del[key] = -val
    resource_diff_add = dict(sorted(resource_diff_add.items(), key=lambda x: x[0]))
    resource_diff_del = dict(sorted(resource_diff_del.items(), key=lambda x: x[0]))
    return resource_diff_add, resource_diff_del


def stock_compare(bot: Bot, update: Update, chat_data: dict):
    old_stock = session.query(Stock).filter_by(user_id=update.message.from_user.id,
                                               stock_type=StockType.Stock.value).order_by(Stock.date.desc()).first()
    new_stock = Stock()
    new_stock.stock = update.message.text
    new_stock.stock_type = StockType.Stock.value
    new_stock.user_id = update.message.from_user.id
    new_stock.date = datetime.now()
    session.add(new_stock)
    session.commit()
    if old_stock is not None:
        resources_old = {}
        resources_new = {}
        strings = old_stock.stock.splitlines()
        for string in strings[1:]:
            resource = string.split(' (')
            resource[1] = resource[1][:-1]
            resources_old[resource[0]] = int(resource[1])
        strings = new_stock.stock.splitlines()
        for string in strings[1:]:
            resource = string.split(' (')
            resource[1] = resource[1][:-1]
            resources_new[resource[0]] = int(resource[1])
        resource_diff_add, resource_diff_del = get_diff(resources_new, resources_old)
        msg = '📦<b>Награблено:</b>\n'
        if len(resource_diff_add):
            for key, val in resource_diff_add.items():
                msg += '{} ({})\n'.format(key, val)
        else:
            msg += 'Ничего\n'
        msg += '\n📦<b>Потеряно:</b>\n'
        if len(resource_diff_del):
            for key, val in resource_diff_del.items():
                msg += '{} ({})\n'.format(key, val)
        else:
            msg += 'Ничего\n'
        send_async(bot, chat_id=update.message.chat.id, text=msg, parse_mode=ParseMode.HTML)
    else:
        send_async(bot, chat_id=update.message.chat.id, text='Жду с чем сравнивать...')


def trade_compare(bot: Bot, update: Update, chat_data: dict):
    old_stock = session.query(Stock).filter_by(user_id=update.message.from_user.id,
                                               stock_type=StockType.TradeBot.value).order_by(Stock.date.desc()).first()
    new_stock = Stock()
    new_stock.stock = update.message.text
    new_stock.stock_type = StockType.TradeBot.value
    new_stock.user_id = update.message.from_user.id
    new_stock.date = datetime.now()
    session.add(new_stock)
    session.commit()
    if old_stock is not None:
        items_old = {}
        items_new = {}
        strings = old_stock.stock.splitlines()
        for string in strings:
            if string.startswith('/add_'):
                item = string.split('   ')[1]
                item = item.split(' x ')
                items_old[item[0]] = int(item[1])
        strings = new_stock.stock.splitlines()
        for string in strings:
            if string.startswith('/add_'):
                item = string.split('   ')[1]
                item = item.split(' x ')
                items_new[item[0]] = int(item[1])
        resource_diff_add, resource_diff_del = get_diff(items_new, items_old)
        msg = '📦<b>Награблено:</b>\n'
        if len(resource_diff_add):
            for key, val in resource_diff_add.items():
                msg += '{} ({})\n'.format(key, val)
        else:
            msg += 'Ничего\n'
        msg += '\n📦<b>Потеряно:</b>\n'
        if len(resource_diff_del):
            for key, val in resource_diff_del.items():
                msg += '{} ({})\n'.format(key, val)
        else:
            msg += 'Ничего\n'
        send_async(bot, chat_id=update.message.chat.id, text=msg, parse_mode=ParseMode.HTML)
    else:
        send_async(bot, chat_id=update.message.chat.id, text='Жду с чем сравнивать...')
