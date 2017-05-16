from telegram import Update, Bot
from core.types import User, Wellcomed, WelcomeMsg, AdminType, admin, session
from core.template import fill_template
from time import time
from core.utils import logger, send_async

last_welcome = 0


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
