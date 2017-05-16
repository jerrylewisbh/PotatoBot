from telegram import Update, Bot
from core.types import WelcomeMsg, Trigger, AdminType, admin, trigger_decorator, session
from core.utils import send_async


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


@trigger_decorator
def trigger_show(bot: Bot, update: Update):
    trigger = session.query(Trigger).filter_by(trigger=update.message.text).first()
    if trigger is not None:
        send_async(bot, chat_id=update.message.chat.id, text=trigger.message)


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
