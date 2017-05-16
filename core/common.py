from telegram import Update, Bot
from core.types import User, Group, AdminType, Admin, admin, trigger_decorator, session
from core.utils import logger, send_async


def error(bot: Bot, update, error, **kwargs):
    """ Error handling """
    logger.error("An error (%s) occurred: %s"
                 % (type(error), error.message))


def start(bot: Bot, update: Update):
    pass


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


def add_user(bot: Bot, update: Update):
    user = session.query(User).filter_by(id=update.message.from_user.id).first()
    if user is None:
        user = User(id=update.message.from_user.id, username=update.message.from_user.username or '',
                    first_name=update.message.from_user.first_name or '',
                    last_name=update.message.from_user.last_name or '')
        session.add(user)
    else:
        updated = False
        if user.username != update.message.from_user.username:
            user.username = update.message.from_user.username
            updated = True
        if user.first_name != update.message.from_user.first_name:
            user.first_name = update.message.from_user.first_name
            updated = True
        if user.last_name != update.message.from_user.last_name:
            user.last_name = update.message.from_user.last_name
            updated = True
        if updated:
            session.add(user)
    try:
        session.commit()
    except Exception:
        session.rollback()


def update_group(bot: Bot, update: Update):
    if update.message.chat.type in ['group', 'supergroup', 'channel']:
        group = session.query(Group).filter_by(id=update.message.chat.id).first()
        if group is None:
            group = Group(id=update.message.chat.id, title=update.message.chat.title,
                          username=update.message.chat.username)
            session.add(group)
        else:
            updated = False
            if group.username != update.message.chat.username:
                group.username = update.message.chat.username
                updated = True
            if group.title != update.message.chat.title:
                group.title = update.message.chat.title
                updated = True
            if updated:
                session.add(group)
        session.commit()
