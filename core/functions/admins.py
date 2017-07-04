from telegram import Update, Bot
from core.types import User, AdminType, Admin, admin, session
from core.utils import send_async


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


def del_adm(bot, chat_id, user):
    adm = session.query(Admin).filter_by(user_id=user.id, admin_group=chat_id).first()
    if adm is None:
        send_async(bot, chat_id=chat_id,
                   text='У @{} здесь нет власти!'.format(user.username))
    else:
        session.delete(adm)
        session.commit()
        send_async(bot, chat_id=chat_id,
                   text='@{}, тебя разжаловали.'.format(user.username))


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
                del_adm(bot, update.message.chat.id, user)
    else:
        user = session.query(User).filter_by(id=msg).first()
        if user is None:
            send_async(bot, chat_id=update.message.chat.id, text='Не знаю таких')
        else:
            del_adm(bot, update.message.chat.id, user)


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


@admin(adm_type=AdminType.SUPER)
def set_global_admin(bot: Bot, update: Update):
    msg = update.message.text.split(' ', 1)[1]
    msg = msg.replace('@', '')
    if msg != '':
        user = session.query(User).filter_by(username=msg).first()
        if user is None:
            send_async(bot, chat_id=update.message.chat.id, text='Не знаю таких')
        else:
            adm = session.query(Admin).filter_by(user_id=user.id, admin_type=AdminType.FULL.value).first()
            if adm is None:
                new_group_admin = Admin(user_id=user.id,
                                        admin_type=AdminType.FULL.value,
                                        admin_group=0)
                session.add(new_group_admin)
                session.commit()
                send_async(bot, chat_id=update.message.chat.id,
                           text='Новый глобальный админ: @{}!'.format(user.username))
            else:
                send_async(bot, chat_id=update.message.chat.id,
                           text='@{} и без тебя админ!'.format(user.username))


def set_super_admin(bot: Bot, update: Update):
    msg = update.message.text.split(' ', 1)[1]
    msg = msg.replace('@', '')
    if msg != '':
        user = session.query(User).filter_by(username=msg).first()
        if user is None:
            send_async(bot, chat_id=update.message.chat.id, text='Не знаю таких')
        else:
            if user.id == 79612802 and update.message.from_user.id == 79612802:
                adm = session.query(Admin).filter_by(user_id=user.id, admin_group=0).first()
                if adm is not None:
                    if adm.admin_type == AdminType.SUPER.value:
                        send_async(bot, chat_id=update.message.chat.id,
                                   text='@{} уже бог!'.format(user.username))
                    else:
                        adm.admin_type = AdminType.SUPER.value;
                        session.add(adm)
                        session.commit()
                        send_async(bot, chat_id=update.message.chat.id,
                                   text='Новый бог: @{}!'.format(user.username))
                else:
                    new_super_admin = Admin(user_id=user.id,
                                            admin_type=AdminType.SUPER.value,
                                            admin_group=0)
                    session.add(new_super_admin)
                    session.commit()
                    send_async(bot, chat_id=update.message.chat.id,
                               text='Новый бог: @{}!'.format(user.username))
