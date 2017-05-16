from telegram import Update, Bot
from core.types import User, Wellcomed, WelcomeMsg, Group, AdminType, admin, session
from core.template import fill_template
from time import time
from core.utils import send_async, add_user, update_group

last_welcome = 0


def welcome(bot: Bot, update: Update):
    global last_welcome
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        if group is not None and group.welcome_enabled:
            welcome_msg = session.query(WelcomeMsg).filter_by(chat_id=group.id).first()
            if welcome_msg is None:
                welcome_msg = WelcomeMsg(chat_id=group.id, message='Привет, %username%!')
                session.add(welcome_msg)

            if update.message.new_chat_member is not None:
                add_user(update.message.new_chat_member)

            welcomed = session.query(Wellcomed).filter_by(user_id=update.message.new_chat_member.id,
                                                          chat_id=update.message.chat.id).first()
            if welcomed is None:
                if time() - last_welcome > 30:
                    send_async(bot, chat_id=update.message.chat.id, text=fill_template(welcome_msg.message, user))
                    last_welcome = time()
                welcomed = Wellcomed(user_id=update.message.new_chat_member.id, chat_id=update.message.chat.id)
                session.add(welcomed)
            session.commit()


@admin(adm_type=AdminType.GROUP)
def set_welcome(bot: Bot, update: Update):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        welcome_msg = session.query(WelcomeMsg).filter_by(chat_id=group.id).first()
        if welcome_msg is None:
            welcome_msg = WelcomeMsg(chat_id=group.id, message=update.message.text.split(' ', 1)[1])
        else:
            welcome_msg.message = update.message.text.split(' ', 1)[1]
        session.add(welcome_msg)
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text='Текст приветствия установлен.')


@admin(adm_type=AdminType.GROUP)
def enable_welcome(bot: Bot, update: Update):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        group.welcome_enabled = True
        session.add(group)
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text='Приветствие включено.')


@admin(adm_type=AdminType.GROUP)
def disable_welcome(bot: Bot, update: Update):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        group.welcome_enabled = False
        session.add(group)
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text='Приветствие выключено.')


@admin(adm_type=AdminType.GROUP)
def show_welcome(bot: Bot, update):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        welcome_msg = session.query(WelcomeMsg).filter_by(chat_id=group.id).first()
        if welcome_msg is None:
            welcome_msg = WelcomeMsg(chat_id=group.id, message='Привет, %username%!')
            session.add(welcome_msg)
            session.commit()
        send_async(bot, chat_id=group.id, text=welcome_msg.message)
