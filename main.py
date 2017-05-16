# -*- coding: utf-8 -*-
import logging
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext.dispatcher import run_async
from core.types import User, Group, Wellcomed, WelcomeMsg, Trigger, AdminType, Admin, admin, trigger_decorator, \
    session
from core.template import fill_template
from time import time

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
last_welcome = 0


@run_async
def send_async(bot: Bot, *args, **kwargs):
    bot.sendMessage(*args, **kwargs)


def error(bot: Bot, update, error, **kwargs):
    """ Error handling """
    logger.error("An error (%s) occurred: %s"
                 % (type(error), error.message))


def welcome(bot: Bot, update: Update):
    global last_welcome
    if update.message.chat.type in ['group', 'supergroup']:
        welcome_msg = session.query(WelcomeMsg).filter_by(chat_id=update.message.chat.id).first()
        if welcome_msg is None:
            welcome_msg = WelcomeMsg(chat_id=update.message.chat.id, message='Привет, %username%!')
            logger.info("I have been added to the new chat")
            session.add(welcome_msg)

        if update.message.new_chat_member is not None:
            user = session.query(User).filter_by(id=update.message.new_chat_member.id).first()
            if user is None:
                user = User(id=update.message.new_chat_member.id, username=update.message.new_chat_member.username or '',
                            first_name=update.message.new_chat_member.first_name or '',
                            last_name=update.message.new_chat_member.last_name or '')
                session.add(user)
            else:
                updated = False
                if user.username != update.message.new_chat_member.username:
                    user.username = update.message.new_chat_member.username
                    updated = True
                if user.first_name != update.message.new_chat_member.first_name:
                    user.first_name = update.message.new_chat_member.first_name
                    updated = True
                if user.last_name != update.message.new_chat_member.last_name:
                    user.last_name = update.message.new_chat_member.last_name
                    updated = True
                if updated:
                    session.add(user)

            if welcome_msg.enabled:
                wellcomed = session.query(Wellcomed).filter_by(user_id=update.message.new_chat_member.id,
                                                               chat_id=update.message.chat.id).first()
                if wellcomed is None:
                    if time() - last_welcome > 30:
                        send_async(bot, chat_id=update.message.chat.id, text=fill_template(welcome_msg.message, user))
                        last_welcome = time()
                    wellcomed = Wellcomed(user_id=update.message.new_chat_member.id, chat_id=update.message.chat.id)
                    session.add(wellcomed)
        try:
            session.commit()
        except Exception:
            session.rollback()


def start(bot: Bot, update: Update):
    pass


@admin()
def set_trigger(bot: Bot, update: Update):
    msg = update.message.text.split(' ', 1)[1]
    new_trigger = msg.split('::', 1)
    if len(new_trigger) == 2:
        trigger = session.query(Trigger).filter_by(trigger=new_trigger[0]).first()
        if trigger is None:
            trigger = Trigger(trigger=new_trigger[0], message=new_trigger[1])
        else:
            trigger.message = new_trigger[1]
        session.add(trigger)
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text='Триггер на фразу "{}" установлен.'.format(new_trigger[0]))
    else:
        send_async(bot, chat_id=update.message.chat.id, text='Какие-то у тебя несвежие мысли, попробуй ещё раз.')


@admin(adm_type=AdminType.GROUP)
def add_trigger(bot: Bot, update: Update):
    msg = update.message.text.split(' ', 1)[1]
    new_trigger = msg.split('::', 1)
    if len(new_trigger) == 2:
        trigger = session.query(Trigger).filter_by(trigger=new_trigger[0]).first()
        if trigger is None:
            trigger = Trigger(trigger=new_trigger[0], message=new_trigger[1])
            session.add(trigger)
            session.commit()
            send_async(bot, chat_id=update.message.chat.id,
                       text='Триггер на фразу "{}" установлен.'.format(new_trigger[0]))
        else:
            send_async(bot, chat_id=update.message.chat.id,
                       text='Триггер "{}" уже существует, выбери другой.'.format(new_trigger[0]))
    else:
        send_async(bot, chat_id=update.message.chat.id, text='Какие-то у тебя несвежие мысли, попробуй ещё раз.')


@admin(adm_type=AdminType.GROUP)
def set_welcome(bot: Bot, update: Update):
    if update.message.chat.type in ['group', 'supergroup']:
        welcome_msg = session.query(WelcomeMsg).filter_by(chat_id=update.message.chat.id).first()
        if welcome_msg is None:
            welcome_msg = WelcomeMsg(chat_id=update.message.chat.id, message=update.message.text.split(' ', 1)[1])
        else:
            welcome_msg.message = update.message.text.split(' ', 1)[1]
        session.add(welcome_msg)
        try:
            session.commit()
        except Exception:
            session.rollback()
        send_async(bot, chat_id=update.message.chat.id, text='Текст приветствия установлен.')


@admin(adm_type=AdminType.GROUP)
def enable_welcome(bot: Bot, update: Update):
    if update.message.chat.type in ['group', 'supergroup']:
        welcome_msg = session.query(WelcomeMsg).filter_by(chat_id=update.message.chat.id).first()
        if welcome_msg is None:
            welcome_msg = WelcomeMsg(chat_id=update.message.chat.id, message='Привет, %username%!', enabled=True)
        else:
            welcome_msg.enabled = True
        session.add(welcome_msg)
        try:
            session.commit()
        except Exception:
            session.rollback()
        send_async(bot, chat_id=update.message.chat.id, text='Приветствие включено.')


@admin(adm_type=AdminType.GROUP)
def disable_welcome(bot: Bot, update: Update):
    if update.message.chat.type in ['group', 'supergroup']:
        welcome_msg = session.query(WelcomeMsg).filter_by(chat_id=update.message.chat.id).first()
        if welcome_msg is None:
            welcome_msg = WelcomeMsg(chat_id=update.message.chat.id, message='Привет, %username%!', enabled=False)
        else:
            welcome_msg.enabled = False
        session.add(welcome_msg)
        try:
            session.commit()
        except Exception:
            session.rollback()
        send_async(bot, chat_id=update.message.chat.id, text='Приветствие выключено.')


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
def show_welcome(bot: Bot, update):
    if update.message.chat.type in ['group', 'supergroup']:
        welcome_msg = session.query(WelcomeMsg).filter_by(chat_id=update.message.chat.id).first()
        if welcome_msg is None:
            welcome_msg = WelcomeMsg(chat_id=update.message.chat.id, message='Привет, %username%!')
            session.add(welcome_msg)
            try:
                session.commit()
            except Exception:
                session.rollback()
        send_async(bot, chat_id=update.message.chat.id, text=welcome_msg.message)


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


@trigger_decorator
def trigger_show(bot: Bot, update: Update):
    trigger = session.query(Trigger).filter_by(trigger=update.message.text).first()
    if trigger is not None:
        send_async(bot, chat_id=update.message.chat.id, text=trigger.message)


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


def manage_text(bot: Bot, update: Update):
    add_user(bot, update)
    update_group(bot, update)
    if str(update.message.text).upper().startswith('Приветствие:'.upper()):
        set_welcome(bot, update)
    elif update.message.text.upper() == 'Помощь'.upper():
        help_msg(bot, update)
    elif update.message.text.upper() == 'Покажи приветствие'.upper():
        show_welcome(bot, update)
    elif update.message.text.upper() == 'Включи приветствие'.upper():
        enable_welcome(bot, update)
    elif update.message.text.upper() == 'Выключи приветствие'.upper():
        disable_welcome(bot, update)
    elif str(update.message.text).upper().startswith('Затриггерь:'.upper()):
        set_trigger(bot, update)
    elif str(update.message.text).upper().startswith('Разтриггерь:'.upper()):
        del_trigger(bot, update)
    elif update.message.text.upper() == 'Список триггеров'.upper():
        list_triggers(bot, update)
    elif update.message.text.upper() == 'Список админов'.upper():
        list_admins(bot, update)
    elif update.message.text.upper() == 'Пинг'.upper():
        ping(bot, update)
    elif update.message.text.upper() == 'Разрешить триггерить всем'.upper():
        enable_trigger_all(bot, update)
    elif update.message.text.upper() == 'Запретить триггерить всем'.upper():
        disable_trigger_all(bot, update)
    elif update.message.text.upper() == 'Админы'.upper():
        admins_for_users(bot, update)
    trigger_show(bot, update)


@admin(adm_type=AdminType.GROUP)
def enable_trigger_all(bot: Bot, update: Update):
    welcome_msg = session.query(WelcomeMsg).filter_by(chat_id=update.message.chat.id).first()
    if welcome_msg is None:
        welcome_msg = WelcomeMsg(chat_id=update.message.chat.id, message='Привет, %username%!', allow_trigger_all=True)
    else:
        welcome_msg.allow_trigger_all = True
    session.add(welcome_msg)
    try:
        session.commit()
    except Exception:
        session.rollback()
    send_async(bot, chat_id=update.message.chat.id, text='Теперь триггерить могут все.')


@admin(adm_type=AdminType.GROUP)
def disable_trigger_all(bot: Bot, update: Update):
    welcome_msg = session.query(WelcomeMsg).filter_by(chat_id=update.message.chat.id).first()
    if welcome_msg is None:
        welcome_msg = WelcomeMsg(chat_id=update.message.chat.id, message='Привет, %username%!', allow_trigger_all=False)
    else:
        welcome_msg.allow_trigger_all = False
    session.add(welcome_msg)
    try:
        session.commit()
    except Exception:
        session.rollback()
    send_async(bot, chat_id=update.message.chat.id, text='Теперь триггерить могут только админы.')


@admin()
def del_trigger(bot: Bot, update: Update):
    msg = update.message.text.split(' ', 1)[1]
    trigger = session.query(Trigger).filter_by(trigger=msg).first()
    if trigger is not None:
        session.delete(trigger)
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text='Триггер на фразу "{}" удалён.'.format(msg))
    else:
        send_async(bot, chat_id=update.message.chat.id, text='Где ты такой триггер видел? 0_о')


@trigger_decorator
def list_triggers(bot: Bot, update: Update):
    triggers = session.query(Trigger).all()
    msg = 'Список текущих триггеров:\n' + ('\n'.join([trigger.trigger for trigger in triggers]) or '[Пусто]')
    send_async(bot, chat_id=update.message.chat.id, text=msg)


@admin()
def set_admin(bot: Bot, update: Update):
    msg = update.message.text.split(' ', 1)[1]
    msg = msg.replace('@', '')
    if msg != '':
        user = session.query(User).filter_by(username=msg).first()
        if user is None:
            send_async(bot, chat_id=update.message.chat.id, text='Не знаю таких')
        else:
            adm = session.query(Admin).filter_by(user_id=user.id, admin_group=update.message.chat.id).first()
            if adm is None:
                new_group_admin = Admin(user_id=user.id,
                                        admin_type=AdminType.GROUP.value,
                                        admin_group=update.message.chat.id)
                session.add(new_group_admin)
                session.commit()
                send_async(bot, chat_id=update.message.chat.id,
                           text='Приветствуйте нового админа: @{}!\n'
                                'Для списка команд бота используй /help'.format(user.username))
            else:
                send_async(bot, chat_id=update.message.chat.id,
                           text='@{} и без тебя тут правит!'.format(user.username))


@admin()
def del_admin(bot: Bot, update: Update):
    msg = update.message.text.split(' ', 1)[1]
    if msg.find('@') != -1:
        msg = msg.replace('@', '')
        if msg != '':
            user = session.query(User).filter_by(username=msg).first()
            if user is None:
                send_async(bot, chat_id=update.message.chat.id, text='Не знаю таких')
            else:
                adm = session.query(Admin).filter_by(user_id=user.id, admin_group=update.message.chat.id).first()
                if adm is None:
                    send_async(bot, chat_id=update.message.chat.id,
                               text='У @{} здесь нет власти!'.format(user.username))
                else:
                    session.delete(adm)
                    session.commit()
                    send_async(bot, chat_id=update.message.chat.id,
                               text='@{}, тебя разжаловали.'.format(user.username))
    else:
        user = session.query(User).filter_by(id=msg).first()
        if user is None:
            send_async(bot, chat_id=update.message.chat.id, text='Не знаю таких')
        else:
            adm = session.query(Admin).filter_by(user_id=msg, admin_group=update.message.chat.id).first()
            if adm is None:
                send_async(bot, chat_id=update.message.chat.id,
                           text='У @{} здесь нет власти!'.format(user.username))
            else:
                session.delete(adm)
                session.commit()
                send_async(bot, chat_id=update.message.chat.id,
                           text='@{}, тебя разжаловали.'.format(user.username))


@admin()
def kick(bot: Bot, update: Update):
    bot.leave_chat(update.message.chat.id)


@admin()
def list_admins(bot: Bot, update: Update):
    admins = session.query(Admin).filter(Admin.admin_group == update.message.chat.id).all()
    users = []
    for admin_user in admins:
        users.append(session.query(User).filter_by(id=admin_user.user_id).first())
    msg = 'Список здешних админов:\n'
    for user in users:
        msg += '{} @{} {} {}\n'.format(user.id, user.username, user.first_name, user.last_name)
    send_async(bot, chat_id=update.message.chat.id, text=msg)


def admins_for_users(bot: Bot, update: Update):
    admins = session.query(Admin).filter(Admin.admin_group == update.message.chat.id).all()
    users = []
    for admin_user in admins:
        users.append(session.query(User).filter_by(id=admin_user.user_id).first())
    msg = 'Список здешних админов:\n'
    if users is None:
        msg += '[Пусто]'
    else:
        for user in users:
            msg += '@{} {} {}\n'.format(user.username, user.first_name, user.last_name)
    send_async(bot, chat_id=update.message.chat.id, text=msg)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("386494081:AAFFK6Wy0RYktHqPr_Pyqi9vXXbupWC3sgI")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_msg))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("set_trigger", set_trigger))
    dp.add_handler(CommandHandler("add_trigger", add_trigger))
    dp.add_handler(CommandHandler("del_trigger", del_trigger))
    dp.add_handler(CommandHandler("list_triggers", list_triggers))
    dp.add_handler(CommandHandler("set_welcome", set_welcome))
    dp.add_handler(CommandHandler("enable_welcome", enable_welcome))
    dp.add_handler(CommandHandler("disable_welcome", disable_welcome))
    dp.add_handler(CommandHandler("show_welcome", show_welcome))
    dp.add_handler(CommandHandler("add_admin", set_admin))
    dp.add_handler(CommandHandler("del_admin", del_admin))
    dp.add_handler(CommandHandler("list_admins", list_admins))
    dp.add_handler(CommandHandler("kick", kick))
    dp.add_handler(CommandHandler("enable_trigger", enable_trigger_all))
    dp.add_handler(CommandHandler("disable_trigger", disable_trigger_all))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.status_update, welcome))
    dp.add_handler(MessageHandler(Filters.text, manage_text))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()