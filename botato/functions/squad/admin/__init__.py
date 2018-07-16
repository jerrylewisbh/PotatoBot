import logging
from datetime import datetime, timedelta
from sqlalchemy import func, tuple_, and_
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup

from core.bot import MQBot
from core.decorators import command_handler
from core.handler.callback import get_callback_action, CallbackAction
from core.handler.callback.util import create_callback
from core.state import get_last_battle
from core.template import fill_char_template
from core.texts import *
from core.texts import MSG_SQUAD_CLEAN
from core.db import Session
from core.enums import AdminType
from core.model import User, Admin, Character, Report, Squad, SquadMember
from core.utils import send_async
from functions.reply_markup import generate_user_markup


@command_handler(
    min_permission=AdminType.GROUP
)
def list_requests(bot: MQBot, update: Update, user: User):
    admin = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
    group_admin = []
    for adm in admin:
        if adm.admin_type == AdminType.GROUP.value and adm.group_id != 0:
            group_admin.append(adm)
    count = 0
    for adm in group_admin:
        members = Session.query(SquadMember).filter_by(squad_id=adm.group_id, approved=False)
        for member in members:
            count += 1

            inline_keys = [
                [InlineKeyboardButton(
                    BTN_ACCEPT,
                    callback_data=create_callback(
                        CallbackAction.SQUAD_MANAGE,
                        user.id,
                        sub_action='accept_application',
                        applicant_id=member.user_id
                    )
                ),
                    InlineKeyboardButton(
                        BTN_DECLINE,
                        callback_data=create_callback(
                            CallbackAction.SQUAD_MANAGE,
                            user.id,
                            sub_action='decline_application',
                            applicant_id=member.user_id
                        )
                )]
            ]

            send_async(
                bot,
                chat_id=update.message.chat.id,
                text=fill_char_template(
                    MSG_PROFILE_SHOW_FORMAT,
                    member.user,
                    member.user.character,
                    member.user.profession,
                    True),
                reply_markup=InlineKeyboardMarkup(inline_keys),
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
                                               Squad.chat_id == Admin.group_id).all()
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
            .filter(SquadMember.squad_id == adm.group_id).group_by(Character) \
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
def battle_reports(bot: MQBot, update: Update, user: User):
    logging.info("battle_reports_show")

    admin = Session.query(Admin, Squad).filter(
        Admin.user_id == update.message.from_user.id,
        Squad.chat_id == Admin.group_id
    ).all()
    group_admin = []
    for adm, squad in admin:
        if squad is not None:
            group_admin.append([adm, squad])
    for adm, squad in group_admin:
        time_from = get_last_battle()

        reports = Session.query(User, Report).join(SquadMember).outerjoin(
            Report, and_(User.id == Report.user_id, Report.date > time_from)
        ).filter(
            SquadMember.squad_id == adm.group_id
        ).order_by(Report.date.desc()).all()

        texts = []
        full_def = 0
        full_atk = 0
        full_exp = 0
        full_gold = 0
        full_stock = 0
        total_reports = 0
        total_members = 0
        for report_user, report in reports:
            total_members += 1
            if report:
                icon = REST_ICON if report.earned_exp == 0 else ATTACK_ICON if report.earned_stock > 0 else DEFENSE_ICON
                icon = PRELIMINARY_ICON + icon if report.preliminary_report else icon
                text = MSG_REPORT_SUMMARY_ROW.format(
                    icon, report.name, report_user.username, report.attack, report.defence,
                    report.earned_exp, report.earned_gold, report.earned_stock)
                texts.append(text)
                full_atk += report.attack
                full_def += report.defence
                full_exp += report.earned_exp
                full_gold += report.earned_gold
                full_stock += report.earned_stock
                total_reports += 1
            else:
                if not report_user.character:
                    continue
                text = MSG_REPORT_SUMMARY_ROW_EMPTY.format(report_user.character.name, report_user.username)
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
                markup = __generate_report_paging(user, time_from, squad.chat_id)
                bot.sendMessage(
                    chat_id=update.message.chat.id,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup)

                repo_list = ''


@command_handler(
    min_permission=AdminType.GROUP
)
def list_squads(bot: MQBot, update: Update, user: User):
    # Check admin...
    admin = Session.query(Admin).filter(User.id == user.id).all()
    global_adm = False


    group_ids = []
    global_admin = False
    for permission in user.permissions:
        if permission.admin_type <= AdminType.FULL:
            global_admin = True
            break
        elif permission.admin_type == AdminType.GROUP:
            group_ids.append(permission.group_id)

    if global_admin:
        squads = Session.query(Squad)
    else:
        logging.info("User has access to these squads: %s", group_ids)
        squads = Session.query(Squad).filter(Squad.chat_id.in_(group_ids)).all()

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


def __request_decline(bot, update, user_id):
    member = Session.query(SquadMember).filter_by(user_id=user_id, approved=False).first()
    if member:
        bot.edit_message_text(
            MSG_SQUAD_REQUEST_DECLINED.format('@' + member.user.username),
            update.callback_query.message.chat.id,
            update.callback_query.message.message_id
        )
        Session.delete(member)
        Session.commit()

        send_async(
            bot,
            chat_id=member.user_id,
            text=MSG_SQUAD_REQUEST_DECLINED_ANSWER
        )


def __request_accept(bot, update, user_id):
    member = Session.query(SquadMember).filter_by(user_id=user_id, approved=False).first()
    if member:
        member.approved = True
        Session.add(member)
        Session.commit()

        bot.edit_message_text(
            MSG_SQUAD_REQUEST_ACCEPTED.format('@' + member.user.username),
            update.callback_query.message.chat.id,
            update.callback_query.message.message_id
        )

        squad = Session.query(Squad).filter_by(chat_id=member.squad_id).first()
        if squad.invite_link is None:
            answer = MSG_SQUAD_REQUEST_ACCEPTED_ANSWER
        else:
            answer = MSG_SQUAD_REQUEST_ACCEPTED_ANSWER_LINK.format(member.squad.invite_link)

        send_async(
            bot,
            chat_id=member.user_id,
            text=answer,
            reply_markup=generate_user_markup(member.user_id)
        )
        send_async(
            bot,
            chat_id=member.squad_id,
            text=MSG_SQUAD_REQUEST_ACCEPTED.format('@' + member.user.username)
        )


@command_handler(
    min_permission=AdminType.GROUP
)
def battle_reports_inline(bot: MQBot, update: Update, user: User):
    if not update.callback_query:
        logging.warning("squad_invite_answer without callback_query called")
        return
    action = get_callback_action(update.callback_query.data, user.id)

    squad = Session.query(Squad).filter(Squad.chat_id == action.data['squad_id']).first()
    time_from = action.data['timestamp']
    time_to = time_from + timedelta(hours=4)

    reports = Session.query(User, Report).join(SquadMember).outerjoin(
        Report, and_(User.id == Report.user_id, Report.date > time_from, Report.date < time_to)
    ).filter(
        SquadMember.squad_id == action.data['squad_id']
    ).order_by(Report.date.desc()).all()

    texts = []
    full_def = 0
    full_atk = 0
    full_exp = 0
    full_gold = 0
    full_stock = 0
    total_reports = 0
    total_members = 0
    for report_user, report in reports:
        total_members += 1
        if report:
            icon = REST_ICON if report.earned_exp == 0 else ATTACK_ICON if report.earned_stock > 0 else DEFENSE_ICON
            icon = PRELIMINARY_ICON + icon if report.preliminary_report else icon
            text = MSG_REPORT_SUMMARY_ROW.format(icon,
                                                 report.name, report_user.username, report.attack, report.defence,
                                                 report.earned_exp, report.earned_gold, report.earned_stock)
            texts.append(text)
            full_atk += report.attack
            full_def += report.defence
            full_exp += report.earned_exp
            full_gold += report.earned_gold
            full_stock += report.earned_stock
            total_reports += 1
        else:
            text = MSG_REPORT_SUMMARY_ROW_EMPTY.format(report_user.character.name if report_user.character else "Unknown",
                                                       report_user.username)
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
            markup = __generate_report_paging(user, time_from, squad.chat_id)

            bot.edit_message_text(
                chat_id=update.callback_query.message.chat.id,
                message_id=update.callback_query.message.message_id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=markup
            )

            repo_list = ''


def __generate_fire_up(user: User, members):
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
                callback_data=create_callback(
                    CallbackAction.SQUAD_LEAVE,
                    user.id,
                    leave=True,
                    leave_user_id=member.user.id
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
        callback_data=create_callback(
            CallbackAction.SQUAD_LIST,
            user.id,
        )
    )]

    markup_blocks = [inline_keys[x:x + 50] for x in range(0, len(inline_keys), 50)]
    keyboards = []
    for markup_block in markup_blocks:
        markup_block.append(back_button)
        keyboards.append(InlineKeyboardMarkup(markup_block))

    return keyboards


def __generate_report_paging(user: User, day: datetime, squad_id):
    row1 = [
        InlineKeyboardButton(
            "🕒 07:00 🔘" if day.hour == 7 else "🕒 07:00",
            callback_data=create_callback(
                CallbackAction.REPORT | CallbackAction.PAGINATION_SKIP_FORWARD,
                user.id,
                squad_id=squad_id,
                timestamp=day.replace(hour=7, minute=0)
            )
        ),
        InlineKeyboardButton(
            "🕒 15:00 🔘" if day.hour == 15 else "🕒 15:00",
            callback_data=create_callback(
                CallbackAction.REPORT | CallbackAction.PAGINATION_SKIP_FORWARD,
                user.id,
                squad_id=squad_id,
                timestamp=day.replace(hour=15, minute=0)
            )
        ),
        InlineKeyboardButton(
            "🕒 23:00 🔘" if day.hour == 23 else "🕒 23:00",
            callback_data=create_callback(
                CallbackAction.REPORT | CallbackAction.PAGINATION_SKIP_FORWARD,
                user.id,
                squad_id=squad_id,
                timestamp=day.replace(hour=23, minute=0)
            )
        ),
    ]

    row2 = [
        InlineKeyboardButton(
            "⏪ {}".format((day - timedelta(days=7)).strftime("%d/%m")),
            callback_data=create_callback(
                CallbackAction.REPORT | CallbackAction.PAGINATION_SKIP_FORWARD,
                user.id,
                squad_id=squad_id,
                timestamp=day - timedelta(days=7)
            )
        ),
        InlineKeyboardButton(
            "⬅️ {}".format((day - timedelta(days=1)).strftime("%d/%m")),
            callback_data=create_callback(
                CallbackAction.REPORT | CallbackAction.PAGINATION_SKIP_FORWARD,
                user.id,
                squad_id=squad_id,
                timestamp=day - timedelta(days=1)
            )
        ),
        InlineKeyboardButton(
            "{} ➡️".format((day + timedelta(days=1)).strftime("%d/%m")),
            callback_data=create_callback(
                CallbackAction.REPORT | CallbackAction.PAGINATION_SKIP_FORWARD,
                user.id,
                squad_id=squad_id,
                timestamp=day + timedelta(days=1)
            )
        ),
        InlineKeyboardButton(
            "{} ⏩".format((day + timedelta(days=1)).strftime("%d/%m")),
            callback_data=create_callback(
                CallbackAction.REPORT | CallbackAction.PAGINATION_SKIP_FORWARD,
                user.id,
                squad_id=squad_id,
                timestamp=day + timedelta(days=7)
            )
        )
    ]

    pagination = [row1, row2]

    return InlineKeyboardMarkup(pagination)


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
        squad = Session.query(Squad).filter_by(chat_id=adm.group_id).first()
        if squad is not None:
            group_admin.append(adm)
    for adm in group_admin:
        members = Session.query(SquadMember).filter_by(squad_id=adm.group_id, approved=True).all()
        markups = __generate_fire_up(user, members)
        squad = Session.query(Squad).filter_by(chat_id=adm.group_id).first()
        for markup in markups:
            send_async(
                bot,
                chat_id=update.message.chat.id,
                text=MSG_SQUAD_CLEAN.format(squad.squad_name),
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )


@command_handler(
    min_permission=AdminType.GROUP
)
def manage(bot: MQBot, update: Update, user: User):
    if not update.callback_query:
        logging.warning("manage without callback_query called")
        return

    action = get_callback_action(update.callback_query.data, update.effective_user.id)
    if action.data['sub_action'] == "accept_application":
        __request_accept(bot, update, action.data['applicant_id'])
    elif action.data['sub_action'] == "decline_application":
        __request_decline(bot, update, action.data['applicant_id'])
