from config import CASTLE
from datetime import datetime, timedelta

from core.constants import *
from core.functions.inline_markup import (generate_fire_up,
                                          generate_leave_squad,
                                          generate_other_reports,
                                          generate_squad_invite_answer,
                                          generate_squad_list,
                                          generate_squad_request,
                                          generate_squad_request_answer,
                                          generate_yes_no)
from core.functions.reply_markup import generate_squad_markup
from core.functions.top import gen_top_msg, generate_battle_top
from core.template import fill_char_template
from core.texts import *
from core.types import (Admin, AdminType, Character, Group, Report, Squad,
                        SquadMember, User, admin_allowed, user_allowed)
from core.utils import chunks, send_async
from sqlalchemy import and_ as text_
from sqlalchemy import func, text, tuple_
from telegram import Bot, ParseMode, TelegramError, Update

TOP_START_DATE = datetime(2017, 12, 11)


@user_allowed
def squad_about(bot: Bot, update: Update, session):
    admin = session.query(Admin).filter(Admin.user_id == update.message.from_user.id,
                                        Admin.admin_group != 0).first()

    squad_member = session.query(SquadMember).filter_by(user_id=update.message.from_user.id, approved=True).first()
    markup = generate_squad_markup(is_group_admin=admin is not None, in_squad=True if squad_member else False)

    if squad_member:
        squad_text = MSG_SQUAD_ABOUT.format(squad_member.squad.squad_name)
    else:
        squad_text = MSG_SQUAD_NONE

    send_async(bot,
               chat_id=update.message.chat.id,
               text=squad_text,
               reply_markup=markup)


@admin_allowed()
def add_squad(bot: Bot, update: Update, session):
    if update.message.chat.type == 'supergroup':
        squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
        if squad is None:
            squad = Squad()
            squad.chat_id = update.message.chat.id
            squad.thorns_enabled = False
            msg = update.message.text.split(' ', 1)
            if len(msg) == 2:
                squad.squad_name = msg[1]
            else:
                group = session.query(Group).filter_by(id=update.message.chat.id).first()
                squad.squad_name = group.title
            session.add(squad)
            session.commit()
            send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_NEW.format(squad.squad_name),
                       parse_mode=ParseMode.HTML)


@admin_allowed()
def set_invite_link(bot: Bot, update: Update, session):
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and squad is not None:
        new_invite_link = ''
        msg = update.message.text.split(' ', 1)
        if len(msg) == 2:
            new_invite_link = msg[1]
        else:
            try:
                new_invite_link = bot.export_chat_invite_link(update.effective_chat.id)
            except TelegramError:  # missing add_user admin permission
                return

    if new_invite_link:
        squad.invite_link = new_invite_link
        session.add(squad)
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_LINK_SAVED)


@admin_allowed()
def set_squad_name(bot: Bot, update: Update, session):
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and squad is not None:
        msg = update.message.text.split(' ', 1)
        if len(msg) == 2:
            squad.squad_name = msg[1]
            session.add(squad)
            session.commit()
            send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_RENAMED.format(squad.squad_name),
                       parse_mode=ParseMode.HTML)


@admin_allowed()
def del_squad(bot: Bot, update: Update, session):
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and squad is not None:
        for member in squad.members:
            session.delete(member)
        for order_group_item in squad.chat.group_items:
            session.delete(order_group_item)
        session.delete(squad)
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_DELETE)


@admin_allowed(AdminType.GROUP)
def enable_thorns(bot: Bot, update: Update, session):
    group = session.query(Group).filter_by(id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and group is not None and len(group.squad) == 1:
        group.squad[0].thorns_enabled = True
        session.add(group.squad[0])
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_THORNS_ENABLED)


@admin_allowed(AdminType.GROUP)
def enable_reminders(bot: Bot, update: Update, session):
    group = session.query(Group).filter_by(id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and group is not None and len(group.squad) == 1:
        group.squad[0].reminders_enabled = True
        session.add(group.squad[0])
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_REMINDERS_ENABLED)


@admin_allowed(AdminType.GROUP)
def enable_silence(bot: Bot, update: Update, session):
    group = session.query(Group).filter_by(id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and group is not None and len(group.squad) == 1:
        group.squad[0].silence_enabled = True
        session.add(group.squad[0])
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_SILENCE_ENABLED)


@admin_allowed(AdminType.GROUP)
def disable_thorns(bot: Bot, update: Update, session):
    group = session.query(Group).filter_by(id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and group is not None and len(group.squad) == 1:
        group.squad[0].thorns_enabled = False
        session.add(group.squad[0])
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_THORNS_DISABLED)


@admin_allowed(AdminType.GROUP)
def disable_silence(bot: Bot, update: Update, session):
    group = session.query(Group).filter_by(id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and group is not None and len(group.squad) == 1:
        group.squad[0].silence_enabled = False
        session.add(group.squad[0])
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_SILENCE_DISABLED)


@admin_allowed(AdminType.GROUP)
def disable_reminders(bot: Bot, update: Update, session):
    group = session.query(Group).filter_by(id=update.message.chat.id).first()
    if update.message.chat.type == 'supergroup' and group is not None and len(group.squad) == 1:
        group.squad[0].reminders_enabled = False
        session.add(group.squad[0])
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_REMINDERS_DISABLED)


@admin_allowed(AdminType.GROUP)
def squad_list(bot: Bot, update: Update, session):
    admin = session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
    global_adm = False
    for adm in admin:
        if adm.admin_type <= AdminType.FULL.value:
            global_adm = True
            break
    if global_adm:
        squads = session.query(Squad).all()
    else:
        group_ids = []
        for adm in admin:
            group_ids.append(adm.admin_group)
        squads = session.query(Squad).filter(Squad.chat_id.in_(group_ids)).all()
    markup = generate_squad_list(squads, session)
    send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_LIST, reply_markup=markup)


@user_allowed
def squad_request(bot: Bot, update: Update, session):
    user = session.query(User).filter_by(id=update.message.from_user.id).first()
    if user is not None:
        if user.username is None:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_NO_USERNAME)
        elif user.character:
            if user.member:
                markup = generate_leave_squad(user.id)
                send_async(bot, chat_id=update.message.chat.id,
                           text=MSG_SQUAD_REQUEST_EXISTS, reply_markup=markup)
            else:
                if user.character.level < MINIMUM_SQUAD_MEMBER_LEVEL:
                    send_async(bot, chat_id=update.message.chat.id,
                               text=MSG_SQUAD_LEVEL_TOO_LOW.format(MINIMUM_SQUAD_MEMBER_LEVEL))
                else:
                    markup = generate_squad_request(session)
                    send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_REQUEST, reply_markup=markup)
        else:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_NO_PROFILE_IN_BOT)


@admin_allowed(AdminType.GROUP)
def list_squad_requests(bot: Bot, update: Update, session):
    admin = session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
    group_admin = []
    for adm in admin:
        if adm.admin_type == AdminType.GROUP.value and adm.admin_group != 0:
            group_admin.append(adm)
    count = 0
    for adm in group_admin:
        members = session.query(SquadMember).filter_by(squad_id=adm.admin_group, approved=False)
        for member in members:
            count += 1
            markup = generate_squad_request_answer(member.user_id)
            send_async(
                bot,
                chat_id=update.message.chat.id,
                text=fill_char_template(
                    MSG_PROFILE_SHOW_FORMAT,
                    member.user,
                    member.user.character,
                    member.user.profession,
                    True),
                reply_markup=markup,
                parse_mode=ParseMode.HTML)
    if count == 0:
        send_async(bot, chat_id=update.message.chat.id,
                   text=MSG_SQUAD_REQUEST_EMPTY)


@admin_allowed(AdminType.GROUP)
def open_hiring(bot: Bot, update: Update, session):
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        squad.hiring = True
        session.add(squad)
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_RECRUITING_ENABLED)


@admin_allowed(AdminType.GROUP)
def close_hiring(bot: Bot, update: Update, session):
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        squad.hiring = False
        session.add(squad)
        session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_RECRUITING_DISABLED)


@admin_allowed(AdminType.GROUP)
def remove_from_squad(bot: Bot, update: Update, session):
    admin = session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
    group_admin = []
    for adm in admin:
        squad = session.query(Squad).filter_by(chat_id=adm.admin_group).first()
        if squad is not None:
            group_admin.append(adm)
    for adm in group_admin:
        members = session.query(SquadMember).filter_by(squad_id=adm.admin_group, approved=True).all()
        markups = generate_fire_up(members)
        squad = session.query(Squad).filter_by(chat_id=adm.admin_group).first()
        for markup in markups:
            send_async(bot, chat_id=update.message.chat.id,
                       text=MSG_SQUAD_CLEAN.format(squad.squad_name),
                       reply_markup=markup, parse_mode=ParseMode.HTML)


@user_allowed
def leave_squad_request(bot: Bot, update: Update, session):
    member = session.query(SquadMember).filter_by(user_id=update.message.from_user.id).first()
    user = session.query(User).filter_by(id=update.message.from_user.id).first()
    if member:
        squad = member.squad
        markup = generate_yes_no(user_id=user.id)
        send_async(bot, chat_id=member.user_id,
                   text=MSG_SQUAD_LEAVE_ASK.format(user.character.name, squad.squad_name), parse_mode=ParseMode.HTML,
                   reply_markup=markup)
    else:
        send_async(bot, chat_id=user.id,
                   text=MSG_SQUAD_NONE, parse_mode=ParseMode.HTML)


def leave_squad(bot: Bot, user: User, member: SquadMember, message, session):
    if member:
        squad = session.query(Squad).filter(Squad.chat_id == member.squad_id).first()
        member_user = session.query(User).filter(User.id == member.user_id).first()
        session.delete(member)
        session.commit()
        if member.approved:
            admins = session.query(Admin).filter_by(admin_group=squad.chat_id).all()
            for adm in admins:
                if adm.user_id != user.id:
                    send_async(bot, chat_id=adm.user_id,
                               text=MSG_SQUAD_LEAVED.format(member_user.character.name, squad.squad_name),
                               parse_mode=ParseMode.HTML)
            send_async(bot, chat_id=member.squad_id,
                       text=MSG_SQUAD_LEAVED.format(member_user.character.name, squad.squad_name),
                       parse_mode=ParseMode.HTML)
        try:
            bot.restrictChatMember(squad.chat_id, member.user_id)
            bot.kickChatMember(squad.chat_id, member.user_id)
        except TelegramError as err:
            bot.logger.error(err.message)

        if member.user_id == user.id:
            bot.editMessageText(MSG_SQUAD_LEAVED.format(member_user.character.name, squad.squad_name),
                                message.chat.id,
                                message.message_id, parse_mode=ParseMode.HTML)
        else:
            send_async(bot, chat_id=member.user_id,
                       text=MSG_SQUAD_LEAVED.format(member_user.character.name, squad.squad_name),
                       parse_mode=ParseMode.HTML)
            members = session.query(SquadMember).filter_by(squad_id=member.squad_id, approved=True).all()
            markups = generate_fire_up(members)
            for markup in markups:
                send_async(bot, chat_id=message.chat.id, text=message.text, reply_markup=markup)
    else:
        send_async(bot, chat_id=user.id, text=MSG_SQUAD_ALREADY_DELETED)


@admin_allowed(AdminType.GROUP)
def add_to_squad(bot: Bot, update: Update, session):
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        username = update.message.text.split(' ', 1)
        if len(username) == 2:
            username = username[1].replace('@', '')
            user = session.query(User).filter_by(username=username).first()
            if user is not None:
                if user.character is None:
                    send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_NO_PROFILE)
                elif user.member is not None:
                    send_async(bot, chat_id=update.message.chat.id,
                               text=MSG_SQUAD_ADD_IN_SQUAD.format('@' + username))
                else:
                    markup = generate_squad_invite_answer(user.id)
                    send_async(bot, chat_id=update.message.chat.id,
                               text=MSG_SQUAD_ADD.format('@' + username),
                               reply_markup=markup)


@admin_allowed(AdminType.FULL)
def force_add_to_squad(bot: Bot, update: Update, session):
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        username = update.message.text.split(' ', 1)
        if len(username) == 2:
            username = username[1].replace('@', '')
            user = session.query(User).filter_by(username=username).first()
            if user is not None:
                if user.character is None:
                    send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_NO_PROFILE)
                elif user.member is not None:
                    send_async(bot, chat_id=update.message.chat.id,
                               text=MSG_SQUAD_ADD_IN_SQUAD.format('@' + username))
                else:
                    member = session.query(SquadMember).filter_by(user_id=user.id).first()
                    if member is None:
                        member = SquadMember()
                        member.user_id = user.id
                        member.squad_id = update.message.chat.id
                        member.approved = True
                        session.add(member)
                        session.commit()
                        send_async(
                            bot,
                            chat_id=update.message.chat.id,
                            text=MSG_SQUAD_ADD_FORCED.format(
                                '@' + user.username))


@admin_allowed(AdminType.GROUP)
def call_squad(bot: Bot, update: Update, session):
    limit = 3
    count = 0
    squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        users = session.query(User).join(SquadMember).filter(User.id == SquadMember.user_id)\
            .filter(SquadMember.squad_id == squad.chat_id).all()
        msg = MSG_SQUAD_CALL_HEADER
        for user in users:
            if user.username is not None:
                msg += '@' + user.username + ' '
            if count > limit:
                send_async(bot, chat_id=update.message.chat.id, text=msg)
                msg = ""
                count = 0
            count += 1


@admin_allowed(AdminType.GROUP)
def battle_attendance_show(bot: Bot, update: Update, session):
    admin = session.query(Admin, Squad).filter(Admin.user_id == update.message.from_user.id,
                                               Squad.chat_id == Admin.admin_group).all()
    group_admin = []
    for adm, squad in admin:
        if squad is not None:
            group_admin.append([adm, squad])
    for adm, squad in group_admin:
        actual_profiles = session.query(Character.user_id, func.max(Character.date)). \
            group_by(Character.user_id)
        actual_profiles = actual_profiles.all()
        today = datetime.today().date()
        battles = session.query(Character, func.count(Report.user_id))\
            .outerjoin(Report, Report.user_id == Character.user_id) \
            .join(SquadMember, SquadMember.user_id == Character.user_id)\
            .filter(Report.date > TOP_START_DATE) \
            .filter(tuple_(Character.user_id, Character.date)
                    .in_([(a[0], a[1]) for a in actual_profiles]),
                    Character.date > datetime.now() - timedelta(days=7))\
            .filter(SquadMember.squad_id == adm.admin_group).group_by(Character)\
            .filter(Report.date > today - timedelta(days=today.weekday())) \
            .filter(Report.earned_exp > 0)\
            .order_by(func.count(Report.user_id).desc())
        battles = battles.all()
        text = MSG_TOP_WEEK_WARRIORS_SQUAD.format(squad.squad_name)
        str_format = MSG_TOP_FORMAT
        for i in range(0, len(battles)):
            text += str_format.format(i + 1, battles[i][0].name, battles[i][0].level, battles[i][1], '⛳️')
        if update.message:
            send_async(bot,
                       chat_id=update.message.chat.id,
                       text=text)


@admin_allowed(AdminType.GROUP)
def battle_reports_show(bot: Bot, update: Update, session):
    admin = session.query(Admin, Squad).filter(Admin.user_id == update.message.from_user.id,
                                               Squad.chat_id == Admin.admin_group).all()
    group_admin = []
    for adm, squad in admin:
        if squad is not None:
            group_admin.append([adm, squad])
    for adm, squad in group_admin:
        now = datetime.now()
        if (now.hour < 7):
            now = now - timedelta(days=1)

        time_from = now.replace(hour=(int((now.hour + 1) / 8) * 8 - 1 + 24) % 24, minute=0, second=0)

        reports = session.query(User, Report) \
            .join(SquadMember) \
            .outerjoin(Report, and_(User.id == Report.user_id, Report.date > time_from)) \
            .filter(SquadMember.squad_id == adm.admin_group).order_by(Report.date.desc()).all()
        texts = []
        full_def = 0
        full_atk = 0
        full_exp = 0
        full_gold = 0
        full_stock = 0
        total_reports = 0
        total_members = 0
        for user, report in reports:
            total_members += 1
            if report:
                icon = REST_ICON if report.earned_exp == 0 else ATTACK_ICON if report.earned_stock > 0 else DEFENSE_ICON
                icon = PRELIMINARY_ICON + icon if report.preliminary_report else icon
                text = MSG_REPORT_SUMMARY_ROW.format(
                    icon, report.name, user.username, report.attack, report.defence,
                    report.earned_exp, report.earned_gold, report.earned_stock)
                texts.append(text)
                full_atk += report.attack
                full_def += report.defence
                full_exp += report.earned_exp
                full_gold += report.earned_gold
                full_stock += report.earned_stock
                total_reports += 1
            else:
                text = MSG_REPORT_SUMMARY_ROW_EMPTY.format(user.character.name, user.username)
                texts.append(text)

        template = MSG_REPORT_SUMMARY_HEADER.format(
            squad.squad_name,
            time_from.strftime('%d-%m-%Y %H:%M'),
            total_reports,
            total_members,
            full_atk,
            full_def,
            full_exp,
            full_gold,
            full_stock)

        limit = 50
        count = 0
        repo_list = ''
        limit = limit if len(texts) > limit else len(texts)
        for element in texts:
            repo_list += element
            count = count + 1
            if count >= limit:
                count = 0
                text = template + repo_list
                markup = generate_other_reports(time_from, squad.chat_id)
                bot.sendMessage(
                    chat_id=update.message.chat.id,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup)
                #send_async(bot, chat_id=update.message.chat.id, text=repo_list, parse_mode=ParseMode.HTML, reply_markup=markup)
                repo_list = ''
