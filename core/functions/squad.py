from telegram import Update, Bot
from core.types import User, AdminType, Admin, admin, session, OrderGroup, Group, Squad
from core.utils import send_async
from core.functions.inline_keyboard_handling import generate_groups_manage, generate_group_manage


@admin()
def add_squad(bot: Bot, update: Update):
    if update.message.chat.type == 'supergroup':
        squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
        if squad is None:
            squad = Squad()
            squad.chat_id = update.message.chat.id
            msg = update.message.text.split(' ', 1)
            if len(msg) == 2:
                squad.squad_name = msg[1]
            else:
                group = session.query(Group).filter_by(id=update.message.chat.id).first()
                squad.squad_name = group.title
            session.add(squad)
            session.commit()
            send_async(bot, chat_id=update.message.chat.id, text='Теперь здесь будет обитать отряд {}!\n'
                                                                 'Не забудьте задать ссылку для '
                                                                 'приглашения новых участников.'.format(squad.squad_name))


@admin()
def set_invite_link(bot: Bot, update: Update):
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and squad is not None:
        msg = update.message.text.split(' ', 1)
        if len(msg) == 2:
            squad.invite_link = msg[1]
            session.add(squad)
            session.commit()
            send_async(bot, chat_id=update.message.chat.id, text='Ссылка приглашений сохранена!\n'
                                                                 'Новые участники теперь не пройдут мимо!')


@admin()
def set_squad_name(bot: Bot, update: Update):
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and squad is not None:
        msg = update.message.text.split(' ', 1)
        if len(msg) == 2:
            squad.squad_name = msg[1]
            session.add(squad)
            session.commit()
            send_async(bot, chat_id=update.message.chat.id, text='Теперь этот отряд будет называться {}!'.format(squad.squad_name))


@admin()
def del_squad(bot: Bot, update: Update):
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and squad is not None:
        session.delete(squad)
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text='Отряд распущен')


@admin()
def enable_thorns(bot: Bot, update: Update):
    group = session.query(Group).filter_by(id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and group is not None and len(group.squad) == 1:
        group.squad[0].thorns_enabled = True
        session.add(group.squad[0])
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text='Непроходимые тернии выросли вокруг')


@admin()
def disable_thorns(bot: Bot, update: Update):
    group = session.query(Group).filter_by(id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and group is not None and len(group.squad) == 1:
        group.squad[0].thorns_enabled = False
        session.add(group.squad[0])
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text='Тернии завяли, теперь каждый может видеть происходящее')
