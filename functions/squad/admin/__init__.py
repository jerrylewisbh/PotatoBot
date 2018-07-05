import json
import logging
from datetime import datetime, timedelta

from sqlalchemy import func, tuple_, and_
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup

from core.bot import MQBot
from core.decorators import command_handler
from core.handler.callback import get_callback_action, CallbackAction
from core.handler.callback.util import create_callback
from core.template import fill_char_template
from core.texts import *
from core.texts import MSG_SQUAD_CLEAN
from core.types import AdminType, User, Session, Squad, Admin, SquadMember, Character, Report
from core.utils import send_async
from functions.inline_markup import QueryType
from functions.reply_markup import generate_user_markup

@command_handler(
    min_permission=AdminType.GROUP
)
def list_squad_requests(bot: MQBot, update: Update, user: User):
    admin = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
    group_admin = []
    for adm in admin:
        if adm.admin_type == AdminType.GROUP.value and adm.admin_group != 0:
            group_admin.append(adm)
    count = 0
    for adm in group_admin:
        members = Session.query(SquadMember).filter_by(squad_id=adm.admin_group, approved=False)
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


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def call_squad(bot: MQBot, update: Update, user: User):
    squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
    if squad is not None:
        users = Session.query(User).join(SquadMember).filter(User.id == SquadMember.user_id) \
            .filter(SquadMember.squad_id == squad.chat_id).all()
        all_users = []
        for user in users:
            if user.username is not None:
                all_users.append('@{}'.format(user.username))

        # Make batches of 4 users max...
        notify_users = [all_users[x:x + 4] for x in range(0, len(all_users), 4)]
        for batch in notify_users:
            text = ""
            for user in batch:
                text += "{} ".format(user)
            send_async(bot, chat_id=update.message.chat.id, text=text)
        if len(notify_users) > 0:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_CALL_HEADER)


@command_handler(
    min_permission=AdminType.GROUP
)
def battle_attendance_show(bot: MQBot, update: Update, user: User):
    admin = Session.query(Admin, Squad).filter(Admin.user_id == update.message.from_user.id,
                                               Squad.chat_id == Admin.admin_group).all()
    group_admin = []
    for adm, squad in admin:
        if squad is not None:
            group_admin.append([adm, squad])
    for adm, squad in group_admin:
        actual_profiles = Session.query(Character.user_id, func.max(Character.date)). \
            group_by(Character.user_id)
        actual_profiles = actual_profiles.all()
        today = datetime.today().date()
        battles = Session.query(Character, func.count(Report.user_id)) \
            .outerjoin(Report, Report.user_id == Character.user_id) \
            .join(SquadMember, SquadMember.user_id == Character.user_id) \
            .filter(Report.date > datetime(2017, 12, 11)) \
            .filter(tuple_(Character.user_id, Character.date)
                    .in_([(a[0], a[1]) for a in actual_profiles]),
                    Character.date > datetime.now() - timedelta(days=7)) \
            .filter(SquadMember.squad_id == adm.admin_group).group_by(Character) \
            .filter(Report.date > today - timedelta(days=today.weekday())) \
            .filter(Report.earned_exp > 0) \
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


@command_handler(
    min_permission=AdminType.GROUP
)
def battle_reports_show(bot: MQBot, update: Update, user: User):
    logging.info("battle_reports_show")
    admin = Session.query(Admin, Squad).filter(Admin.user_id == update.message.from_user.id,
                                               Squad.chat_id == Admin.admin_group).all()
    group_admin = []
    for adm, squad in admin:
        if squad is not None:
            group_admin.append([adm, squad])
    for adm, squad in group_admin:
        now = datetime.now()
        if now.hour < 7:
            now = now - timedelta(days=1)

        time_from = now.replace(hour=(int((now.hour + 1) / 8) * 8 - 1 + 24) % 24, minute=0, second=0)

        reports = Session.query(User, Report) \
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
                if not user.character:
                    continue
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
                # send_async(bot, chat_id=update.message.chat.id, text=repo_list, parse_mode=ParseMode.HTML,
                # reply_markup=markup)
                repo_list = ''


def squad_invite_decline(bot, update, user, data):
    if update.callback_query.from_user.id != data['id']:
        update.callback_query.answer(text=MSG_GO_AWAY)
        return
    user = Session.query(User).filter_by(id=data['id']).first()
    bot.edit_message_text(MSG_SQUAD_REQUEST_DECLINED.format('@' + user.username),
                          update.callback_query.message.chat.id,
                          update.callback_query.message.message_id)


def squad_invite_accept(bot, update, user, data):
    if update.callback_query.from_user.id != data['id']:
        update.callback_query.answer(text=MSG_GO_AWAY)
        return
    member = Session.query(SquadMember).filter_by(user_id=data['id']).first()
    if member is None:
        member = SquadMember()
        member.user_id = user.id
        member.squad_id = update.callback_query.message.chat.id
        member.approved = True
        Session.add(member)
        Session.commit()
        bot.edit_message_text(MSG_SQUAD_ADD_ACCEPTED.format('@' + user.username),
                              update.callback_query.message.chat.id,
                              update.callback_query.message.message_id)


@command_handler(
    min_permission=AdminType.GROUP
)
def list_squads(bot: MQBot, update: Update, user: User):
    # Check admin...
    admin = Session.query(Admin).filter(User.id == user.id).all()
    global_adm = False
    for adm in admin:
        if adm.admin_type <= AdminType.FULL.value:
            global_adm = True
            break
    if global_adm:
        squads = Session.query(Squad).all()
    else:
        group_ids = []
        for adm in admin:
            group_ids.append(adm.admin_group)
        squads = Session.query(Squad).filter(Squad.chat_id in group_ids).all()

    # List....
    inline_keys = []
    for squad in squads:
        inline_keys.append(__generate_squad_list_keyboard_button(user, squad))

    send_async(
        bot,
        chat_id=user.id,
        text=MSG_SQUAD_LIST,
        reply_markup=InlineKeyboardMarkup(inline_keys)
    )

@command_handler(
    min_permission=AdminType.GROUP
)
def list_squad_members(bot: MQBot, update: Update, user: User):
    if not update.callback_query:
        logging.warning("inline_list_squad_members without callback_query called")
        return

    action = get_callback_action(update.callback_query.data, update.effective_user.id)
    squad = Session.query(Squad).filter(Squad.chat_id == action.data['squad_id']).first()
    markups = __generate_squad_member_list_keyboard_button(user, squad)
    for markup in markups:
        send_async(
            bot,
            chat_id=update.callback_query.message.chat.id,
            text=squad.squad_name,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )

def squad_request_decline(bot, update, user, data):
    member = Session.query(SquadMember).filter_by(user_id=data['id'], approved=False).first()
    if member:
        bot.edit_message_text(MSG_SQUAD_REQUEST_DECLINED.format('@' + member.user.username),
                              update.callback_query.message.chat.id,
                              update.callback_query.message.message_id)
        Session.delete(member)
        Session.commit()
        send_async(bot, chat_id=member.user_id, text=MSG_SQUAD_REQUEST_DECLINED_ANSWER)


def squad_request_accept(bot, update, user, data):
    member = Session.query(SquadMember).filter_by(user_id=data['id'], approved=False).first()
    if member:
        member.approved = True
        Session.add(member)
        Session.commit()
        bot.edit_message_text(MSG_SQUAD_REQUEST_ACCEPTED.format('@' + member.user.username),
                              update.callback_query.message.chat.id,
                              update.callback_query.message.message_id)

        squad = Session.query(Squad).filter_by(chat_id=member.squad_id).first()
        answer = ""
        if squad.invite_link is None:
            answer = MSG_SQUAD_REQUEST_ACCEPTED_ANSWER
        else:
            answer = MSG_SQUAD_REQUEST_ACCEPTED_ANSWER_LINK.format(member.squad.invite_link)
        send_async(bot, chat_id=member.user_id, text=answer,
                   reply_markup=generate_user_markup(member.user_id))
        send_async(
            bot,
            chat_id=member.squad_id,
            text=MSG_SQUAD_REQUEST_ACCEPTED.format(
                '@' + member.user.username))


def inline_squad_delete(bot, update, user, data):
    squad = Session.query(Squad).filter_by(chat_id=data['gid']).first()
    if squad is not None:
        for member in squad.members:
            Session.delete(member)
        Session.delete(squad)
        Session.commit()
        send_async(bot, chat_id=data['gid'], text=MSG_SQUAD_DELETE)
    msg = MSG_GROUP_STATUS_CHOOSE_CHAT
    squads = Session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        inline_keys.append(InlineKeyboardButton(squad.squad_name,
                                                callback_data=json.dumps({'t': QueryType.GroupInfo.value,
                                                                          'id': squad.chat_id})))
    inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
    bot.edit_message_text(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                          reply_markup=inline_markup)


def other_report(bot, update, user, data):
    squad = Session.query(Squad).filter(Squad.chat_id == data['c']).first()
    time_from = datetime.fromtimestamp(data['ts'])
    time_to = time_from + timedelta(hours=4)
    reports = Session.query(User, Report) \
        .join(SquadMember) \
        .outerjoin(Report, and_(User.id == Report.user_id, Report.date > time_from, Report.date < time_to)) \
        .filter(SquadMember.squad_id == data['c']).order_by(Report.date.desc()).all()
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
            text = MSG_REPORT_SUMMARY_ROW.format(icon,
                                                 report.name, user.username, report.attack, report.defence,
                                                 report.earned_exp, report.earned_gold, report.earned_stock)
            texts.append(text)
            full_atk += report.attack
            full_def += report.defence
            full_exp += report.earned_exp
            full_gold += report.earned_gold
            full_stock += report.earned_stock
            total_reports += 1
        else:
            text = MSG_REPORT_SUMMARY_ROW_EMPTY.format(user.character.name if user.character else "Unknown",
                                                       user.username)
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
                chat_id=update.callback_query.message.chat.id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=markup)
            repo_list = ''


def group_list(bot: MQBot, update: Update, user: User, data):
    msg = MSG_GROUP_STATUS_CHOOSE_CHAT
    squads = Session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        inline_keys.append(InlineKeyboardButton(squad.squad_name,
                                                callback_data=json.dumps({'t': QueryType.GroupInfo.value,
                                                                          'id': squad.chat_id})))
    inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
    bot.edit_message_text(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                          reply_markup=inline_markup)


def generate_fire_up(members):
    inline_keys = []
    inline_list = []
    limit = 50
    count = 0
    limit = limit if len(members) > limit else len(members)
    logging.debug("generate_fire_up - limit: %s", limit)
    for member in members:
        if not member.user.character:
            continue
        inline_keys.append([
            InlineKeyboardButton(
                '🔥{}: {}⚔ {}🛡'.format(
                    member.user,
                    member.user.character.attack,
                    member.user.character.defence
                ),
                callback_data=json.dumps(
                    {'t': QueryType.LeaveSquad.value, 'id': member.user_id}
                )
            )
        ])
        count = count + 1
        if count >= limit:
            count = 0
            inline_list.append(InlineKeyboardMarkup(inline_keys))
            inline_keys = []

    if inline_keys:
        inline_list.append(InlineKeyboardMarkup(inline_keys))

    return inline_list


def generate_squad_request_answer(user_id):
    inline_keys = [InlineKeyboardButton(BTN_ACCEPT,
                                        callback_data=json.dumps(
                                            {'t': QueryType.RequestSquadAccept.value, 'id': user_id})),
                   InlineKeyboardButton(BTN_DECLINE,
                                        callback_data=json.dumps(
                                            {'t': QueryType.RequestSquadDecline.value, 'id': user_id}))]
    return InlineKeyboardMarkup([inline_keys])


def generate_squad_invite_answer(user_id):
    inline_keys = [InlineKeyboardButton(MSG_SQUAD_GREEN_INLINE_BUTTON,
                                        callback_data=json.dumps(
                                            {'t': QueryType.InviteSquadAccept.value, 'id': user_id})),
                   InlineKeyboardButton(MSG_SQUAD_RED_INLINE_BUTTON,
                                        callback_data=json.dumps(
                                            {'t': QueryType.InviteSquadDecline.value, 'id': user_id}))]
    return InlineKeyboardMarkup([inline_keys])


def __generate_squad_member_list_keyboard_button(user: User, squad: Squad):
    inline_keys = []
    user_ids = []
    for member in squad.members:
        user_ids.append(member.user_id)

    actual_profiles = Session.query(Character.user_id, func.max(Character.date)).filter(
        Character.user_id.in_(user_ids)
    ).group_by(Character.user_id).all()

    characters = Session.query(Character).filter(
        tuple_(Character.user_id, Character.date).in_([(a[0], a[1]) for a in actual_profiles])
    ).order_by(Character.level.desc()).all()

    for character in characters:
        time_passed = datetime.now() - character.date
        status_emoji = '❇'
        if time_passed > timedelta(days=6):
            status_emoji = '⁉'
        elif time_passed > timedelta(days=5):
            status_emoji = '‼'
        elif time_passed > timedelta(days=3):
            status_emoji = '❗'
        elif time_passed < timedelta(days=1):
            status_emoji = '🕐'
        inline_keys.append([
            InlineKeyboardButton(
                '{}{}: {}⚔ {}🛡 {}🏅'.format(
                    status_emoji,
                    character.name,
                    character.attack,
                    character.defence,
                    character.level
                ),
                callback_data=create_callback(
                    CallbackAction.HERO,
                    user.id,
                    profile_id=character.user.id,
                    back_button=InlineKeyboardButton(
                        MSG_BACK,
                        callback_data=create_callback(
                            CallbackAction.SQUAD_LIST_MEMBERS,
                            user.id,
                            squad_id=squad.chat_id
                        )
                    )
                )
            )
        ])

    back_button = [InlineKeyboardButton(
        MSG_BACK,
        callback_data=json.dumps(
            {'t': QueryType.SquadList.value}
        )
    )]

    markup_blocks = [inline_keys[x:x + 50] for x in range(0, len(inline_keys), 50)]
    keyboards = []
    for markup_block in markup_blocks:
        markup_block.append(back_button)
        keyboards.append(InlineKeyboardMarkup(markup_block))

    return keyboards

def generate_leave_squad(user_id):
    inline_keys = [[InlineKeyboardButton(BTN_LEAVE,
                                         callback_data=json.dumps({'t': QueryType.LeaveSquad.value,
                                                                   'id': user_id}))]]
    return InlineKeyboardMarkup(inline_keys)


def generate_other_reports(time: datetime, squad_id):
    inline_keys = [[InlineKeyboardButton('<< ' + (time - timedelta(hours=8)).strftime('%d-%m-%Y %H:%M'),
                                         callback_data=json.dumps(
                                             {'t': QueryType.OtherReport.value,
                                              'ts': (time - timedelta(hours=8)).timestamp(),
                                              'c': squad_id}))]]
    if time + timedelta(hours=4) < datetime.now():
        inline_keys[0].append(InlineKeyboardButton((time + timedelta(hours=8)).strftime('%d-%m-%Y %H:%M') + ' >>',
                                                   callback_data=json.dumps(
                                                       {'t': QueryType.OtherReport.value,
                                                        'ts': (time + timedelta(hours=8)).timestamp(),
                                                        'c': squad_id})))
    return InlineKeyboardMarkup(inline_keys)


def __generate_squad_list_keyboard_button(user: User, squad: Squad):
    attack = 0
    defence = 0
    level = 0
    members = squad.members
    user_ids = []
    for member in members:
        user_ids.append(member.user_id)
    actual_profiles = Session.query(Character.user_id, func.max(Character.date)). \
        filter(Character.user_id.in_(user_ids)). \
        group_by(Character.user_id).all()
    characters = Session.query(Character).filter(tuple_(Character.user_id, Character.date)
                                                 .in_([(a[0], a[1]) for a in actual_profiles])).all()
    for character in characters:
        attack += character.attack
        defence += character.defence
        level += character.level
    return [
        InlineKeyboardButton(
            '{} : {}⚔ {}🛡 {}👥 {}🏅'.format(
                squad.squad_name,
                attack,
                defence,
                len(members),
                int(level / (len(members) or 1))
            ),
            callback_data=create_callback(
                CallbackAction.SQUAD_LIST_MEMBERS,
                user.id,
                squad_id=squad.chat_id
            )
        )
    ]


@command_handler(
    min_permission=AdminType.GROUP
)
def remove_from_squad(bot: MQBot, update: Update, user: User):
    admin = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
    group_admin = []
    for adm in admin:
        squad = Session.query(Squad).filter_by(chat_id=adm.admin_group).first()
        if squad is not None:
            group_admin.append(adm)
    for adm in group_admin:
        members = Session.query(SquadMember).filter_by(squad_id=adm.admin_group, approved=True).all()
        markups = generate_fire_up(members)
        squad = Session.query(Squad).filter_by(chat_id=adm.admin_group).first()
        for markup in markups:
            send_async(
                bot,
                chat_id=update.message.chat.id,
                text=MSG_SQUAD_CLEAN.format(squad.squad_name),
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
