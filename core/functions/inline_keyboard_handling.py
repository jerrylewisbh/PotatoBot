import json
import logging
from config import WAITING_ROOM_LINK
from datetime import datetime, timedelta
from json import loads
from uuid import uuid4

from sqlalchemy import and_
from telegram import (Bot, InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultArticle, InputTextMessageContent,
                      ParseMode, TelegramError, Update)
from telegram.ext import Job, JobQueue
from telegram.ext.dispatcher import run_async

from core.decorators import admin_allowed, user_allowed
from core.enums import CASTLE_LIST, TACTICTS_COMMAND_PREFIX, Castle, Icons
from core.functions.admins import del_adm
from core.functions.common import StockType, stock_compare_text
from core.functions.inline_markup import (QueryType, generate_forward_markup,
                                          generate_group_info,
                                          generate_group_manage,
                                          generate_groups_manage,
                                          generate_leave_squad,
                                          generate_ok_markup,
                                          generate_order_chats_markup,
                                          generate_order_groups_markup,
                                          generate_other_reports,
                                          generate_profile_buttons,
                                          generate_squad_list,
                                          generate_squad_members)
from core.functions.profile.util import (annotate_stock_with_price,
                                         send_settings)
from core.functions.reply_markup import generate_user_markup
from core.functions.squad import leave_squad
from core.functions.top import (global_battle_top, global_build_top,
                                global_squad_build_top, week_battle_top,
                                week_build_top, week_squad_build_top)
from core.template import fill_char_template
from core.texts import *
from core.types import (Admin, AdminType, Location, MessageType, Order,
                        OrderCleared, OrderGroup, OrderGroupItem, Report,
                        Session, Squad, SquadMember, Stock, User, UserQuest)
from core.utils import create_or_update_user, send_async, update_group
from core.functions.guild_stock import generate_gstock_requests

LOGGER = logging.getLogger('MyApp')

order_updated = {}

Session()


@admin_allowed()
def send_status(bot: Bot, update: Update):
    msg = MSG_GROUP_STATUS_CHOOSE_CHAT
    squads = Session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        inline_keys.append(InlineKeyboardButton(squad.squad_name,
                                                callback_data=json.dumps({'t': QueryType.GroupInfo.value,
                                                                          'id': squad.chat_id})))
    inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
    send_async(bot, chat_id=update.message.chat.id, text=msg, reply_markup=inline_markup)


@run_async
def send_order(bot, order, order_type, chat_id, markup):
    try:
        msg_sent = None
        if order_type == MessageType.AUDIO.value:
            msg_sent = bot.send_audio(chat_id, order, reply_markup=markup)
        elif order_type == MessageType.DOCUMENT.value:
            msg_sent = bot.send_document(chat_id, order, reply_markup=markup)
        elif order_type == MessageType.VOICE.value:
            msg_sent = bot.send_voice(chat_id, order, reply_markup=markup)
        elif order_type == MessageType.STICKER.value:
            msg_sent = bot.send_sticker(chat_id, order, reply_markup=markup)
        elif order_type == MessageType.CONTACT.value:
            msg = order.replace('\'', '"')
            contact = loads(msg)
            if 'phone_number' not in contact.keys():
                contact['phone_number'] = None
            if 'first_name' not in contact.keys():
                contact['first_name'] = None
            if 'last_name' not in contact.keys():
                contact['last_name'] = None
                msg_sent = bot.send_contact(chat_id,
                                            contact['phone_number'],
                                            contact['first_name'],
                                            contact['last_name'],
                                            reply_markup=markup)
        elif order_type == MessageType.VIDEO.value:
            msg_sent = bot.send_video(chat_id, order, reply_markup=markup)
        elif order_type == MessageType.VIDEO_NOTE.value:
            msg_sent = bot.send_video_note(chat_id, order, reply_markup=markup)
        elif order_type == MessageType.LOCATION.value:
            msg = order.replace('\'', '"')
            location = loads(msg)
            msg_sent = bot.send_location(chat_id, location['latitude'], location['longitude'], reply_markup=markup)
        elif order_type == MessageType.PHOTO.value:
            msg_sent = bot.send_photo(chat_id, order, reply_markup=markup)
        else:
            msg_sent = send_async(bot, chat_id=chat_id, text=order, disable_web_page_preview=True, reply_markup=markup)
        return msg_sent
    except TelegramError as err:
        bot.logger.error(err.message)
        return None


def update_confirmed(bot: Bot, job: Job):
    order = job.context
    confirmed = order.cleared
    msg = MSG_ORDER_CLEARED_BY_HEADER
    for confirm in confirmed:
        msg += str(confirm.user) + '\n'
    bot.editMessageText(msg, order.chat_id, order.confirmed_msg)


@run_async
@user_allowed
def callback_query(bot: Bot, update: Update, chat_data: dict, job_queue: JobQueue):
    try:
        update_group(update.callback_query.message.chat)

        user = create_or_update_user(update.effective_user)

        data = json.loads(update.callback_query.data)
        if data['t'] == QueryType.GroupList.value:
            group_list(bot, update, user, data)
        elif data['t'] == QueryType.GroupInfo.value:
            group_info(bot, update, user, data)
        elif data['t'] == QueryType.DelAdm.value:
            delete_admin(bot, update, user, data)
        elif data['t'] == QueryType.Order.value:
            order_button(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.OrderOk.value:
            order_confirmed(bot, update, user, data, job_queue)
        elif data['t'] == QueryType.Orders.value:
            orders(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.OrderGroup.value:
            order_group(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.OrderGroupManage.value:
            order_group_manage(bot, update, user, data)
        elif data['t'] == QueryType.OrderGroupTriggerChat.value:
            order_group_tirgger_chat(bot, update, user, data)
        elif data['t'] == QueryType.OrderGroupAdd.value:
            order_group_add(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.OrderGroupDelete.value:
            order_group_delete(bot, update, user, data)
        elif data['t'] == QueryType.OrderGroupList.value:
            order_group_list(bot, update)
        elif data['t'] == QueryType.ShowEquip.value:
            show_equip(bot, update, user, data)
        elif data['t'] == QueryType.ShowSkills.value:
            show_skills(bot, update, user, data)
        elif data['t'] == QueryType.ShowStock.value:
            show_stock(bot, update, user, data)
        elif data['t'] == QueryType.ShowHero.value:
            show_hero(bot, update, user, data)
        elif data['t'] == QueryType.MemberList.value:
            list_members(bot, update, user, data)
        elif data['t'] == QueryType.LeaveSquad.value:
            squad_leave(bot, data, update, user)
        elif data['t'] == QueryType.RequestSquad.value:
            squad_request(bot, data, update, user)
        elif data['t'] == QueryType.RequestSquadAccept.value:
            squad_request_accept(bot, update, user, data)
        elif data['t'] == QueryType.RequestSquadDecline.value:
            squad_request_decline(bot, update, user, data)
        elif data['t'] == QueryType.InviteSquadAccept.value:
            squad_invite_accept(bot, update, user, data)
        elif data['t'] == QueryType.InviteSquadDecline.value:
            squad_invite_decline(bot, update, user, data)
        elif data['t'] == QueryType.TriggerOrderPin.value:
            trigger_order_pin(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.TriggerOrderButton.value:
            trigger_order_button(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.SquadList.value:
            squad_list(bot, update)
        elif data['t'] == QueryType.GroupDelete.value:
            group_delete(bot, update, user, data)
        elif data['t'] == QueryType.DisableAPIAccess:
            diable_api(bot, update, user, data)
        elif data['t'] in [QueryType.EnableAutomatedReport, QueryType.DisableAutomatedReport]:
            toggle_report(bot, update, user, data)
        elif data['t'] in [QueryType.DisableDealReport, QueryType.EnableDealReport]:
            toggle_deal_report(bot, update, user, data)
        elif data['t'] in [QueryType.DisableHideGold, QueryType.EnableHideGold]:
            toggle_gold_hiding(bot, update, user, data)
        elif data['t'] in [QueryType.DisableSniping, QueryType.EnableSniping]:
            toggle_sniping(bot, update, user, data)
        elif data['t'] == QueryType.OtherReport.value:
            other_report(bot, update, user, data)
        elif data['t'] == QueryType.GlobalBuildTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            global_build_top(bot, update)
        elif data['t'] == QueryType.WeekBuildTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            week_build_top(bot, update)
        elif data['t'] == QueryType.SquadGlobalBuildTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            global_squad_build_top(bot, update)
        elif data['t'] == QueryType.SquadWeekBuildTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            week_squad_build_top(bot, update)
        elif data['t'] == QueryType.BattleGlobalTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            global_battle_top(bot, update)
        elif data['t'] == QueryType.BattleWeekTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            week_battle_top(bot, update)
        elif data['t'] == QueryType.Yes.value:
            leave_squad(bot, user, user.member, update.effective_message)
        elif data['t'] == QueryType.No.value:
            no_message(bot, update)
        elif data['t'] == QueryType.QuestFeedbackRequired:
            set_user_quest_location(bot, update, user, data)
        elif data['t'] == QueryType.ForayFeedbackRequired:
            set_user_foray_pledge(bot, update, user, data)

    except TelegramError as e:
        # Ignore Message is not modified errors
        if str(e) != "Message is not modified":
            raise e


def squad_invite_decline(bot, update, user, data):
    if update.callback_query.from_user.id != data['id']:
        update.callback_query.answer(text=MSG_GO_AWAY)
        return
    user = Session.query(User).filter_by(id=data['id']).first()
    bot.editMessageText(MSG_SQUAD_REQUEST_DECLINED.format('@' + user.username),
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
        bot.editMessageText(MSG_SQUAD_ADD_ACCEPTED.format('@' + user.username),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id)


def show_hero(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    update.callback_query.answer(text=MSG_CLEARED)
    back = data['b'] if 'b' in data else False

    # We need a profile first!
    if not user.character:
        text = MSG_NO_PROFILE_IN_BOT
        if user.api_token:
            text = MSG_API_TRY_AGAIN

        send_async(
            bot,
            chat_id=update.callback_query.message.chat.id,
            text=text,
            parse_mode=ParseMode.HTML
        )
        return

    bot.editMessageText(
        fill_char_template(
            MSG_PROFILE_SHOW_FORMAT,
            user,
            user.character,
            user.profession
        ),
        update.callback_query.message.chat.id,
        update.callback_query.message.message_id,
        reply_markup=generate_profile_buttons(user, back)
    )


def order_button(bot: Bot, update: Update, user: User, data, chat_data):
    order_text = chat_data['order']
    order_type = chat_data['order_type']
    order_pin = chat_data['pin'] if 'pin' in chat_data else True
    order_btn = chat_data['btn'] if 'btn' in chat_data else True
    logging.info("Order: text='%s', order_btn='%s', order_text IN CASTLE_LIST='%s'",
                 order_text, order_btn, (order_text in CASTLE_LIST))
    if not data['g']:
        if order_btn:
            order = Order()
            order.text = order_text
            order.chat_id = data['id']
            order.date = datetime.now()
            msg = send_async(bot, chat_id=order.chat_id, text=MSG_ORDER_CLEARED_BY_HEADER + MSG_EMPTY).result()
            if msg:
                order.confirmed_msg = msg.message_id
            else:
                order.confirmed_msg = 0
            Session.add(order)
            Session.commit()
            markup = generate_ok_markup(
                order.id, 0, order_text in CASTLE_LIST or order_text.startswith(TACTICTS_COMMAND_PREFIX), order_text)
            msg = send_order(bot, order.text, order_type, order.chat_id, markup).result().result()
        else:
            markup = None
            if order_text in CASTLE_LIST or order_text.startswith(TACTICTS_COMMAND_PREFIX):
                markup = generate_forward_markup(order_text, 0)
            msg = send_order(bot, order_text, order_type, data['id'], markup).result().result()
        if order_pin and msg:
            try:
                bot.request.post(bot.base_url + '/pinChatMessage', {'chat_id': data['id'],
                                                                    'message_id': msg.message_id,
                                                                    'disable_notification': False})
            except TelegramError as err:
                bot.logger.error(err.message)
    else:
        group = Session.query(OrderGroup).filter_by(id=data['id']).first()
        for item in group.items:
            if order_btn:
                order = Order()
                order.text = order_text
                order.chat_id = item.chat_id
                order.date = datetime.now()
                msg = send_async(
                    bot,
                    chat_id=order.chat_id,
                    text=MSG_ORDER_CLEARED_BY_HEADER +
                    MSG_EMPTY).result()
                if msg:
                    order.confirmed_msg = msg.message_id
                else:
                    order.confirmed_msg = 0
                Session.add(order)
                Session.commit()
                markup = generate_ok_markup(
                    order.id, 0, order_text in CASTLE_LIST or order_text.startswith(TACTICTS_COMMAND_PREFIX),
                    order_text)
                msg = send_order(bot, order.text, order_type, order.chat_id, markup).result().result()
            else:
                markup = None
                if order_text in CASTLE_LIST or order_text.startswith(TACTICTS_COMMAND_PREFIX):
                    markup = generate_forward_markup(order_text, 0)
                msg = send_order(bot, order_text, order_type, item.chat_id, markup).result().result()
            if order_pin and msg:
                try:
                    bot.request.post(bot.base_url + '/pinChatMessage',
                                     {'chat_id': item.chat_id, 'message_id': msg.message_id,
                                      'disable_notification': False})
                except TelegramError as err:
                    bot.logger.error(err.message)
    update.callback_query.answer(text=MSG_ORDER_SENT)


def delete_admin(bot, update, user, data):
    admin_user = Session.query(User).filter_by(id=data['uid']).first()
    if admin_user:
        del_adm(bot, data['gid'], admin_user)
    msg, inline_markup = generate_group_info(data['gid'])
    bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                        reply_markup=inline_markup)


def group_info(bot, update, user, data):
    msg, inline_markup = generate_group_info(data['id'])
    bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                        reply_markup=inline_markup)


def group_list(bot: Bot, update: Update, user: User, data):
    msg = MSG_GROUP_STATUS_CHOOSE_CHAT
    squads = Session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        inline_keys.append(InlineKeyboardButton(squad.squad_name,
                                                callback_data=json.dumps({'t': QueryType.GroupInfo.value,
                                                                          'id': squad.chat_id})))
    inline_markup = InlineKeyboardMarkup([[key] for key in inline_keys])
    bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                        reply_markup=inline_markup)


def no_message(bot, update):
    bot.editMessageText(MSG_SQUAD_LEAVE_DECLINE,
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id)


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
                chat_id=update.callback_query.message.chat.id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=markup)
            repo_list = ''


def toggle_sniping(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    if user.setting_automated_sniping:
        user.setting_automated_sniping = False
    else:
        user.setting_automated_sniping = True
    Session.add(user)
    Session.commit()
    send_settings(bot, update, user)


def toggle_gold_hiding(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    if user.setting_automated_hiding:
        user.setting_automated_hiding = False
    else:
        user.setting_automated_hiding = True
    Session.add(user)
    Session.commit()
    send_settings(bot, update, user)


def toggle_deal_report(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    if user.setting_automated_deal_report:
        user.setting_automated_deal_report = False
    else:
        user.setting_automated_deal_report = True
    Session.add(user)
    Session.commit()
    send_settings(bot, update, user)


def toggle_report(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    if user.setting_automated_report:
        user.setting_automated_report = False
    else:
        user.setting_automated_report = True
    Session.add(user)
    Session.commit()
    send_settings(bot, update, user)


def diable_api(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    if user.api_token:
        user.api_token = None

        user.is_api_profile_allowed = False
        user.is_api_stock_allowed = False
        user.is_api_trade_allowed = False

        user.api_request_id = None
        user.api_grant_operation = None

        # TODO: Do we need to reset settings?

        Session.add(user)
        Session.commit()
    send_settings(bot, update, user)


def group_delete(bot, update, user, data):
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
    bot.editMessageText(msg, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                        reply_markup=inline_markup)


def squad_list(bot, update):
    admin = Session.query(Admin).filter_by(user_id=update.callback_query.from_user.id).all()
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
    markup = generate_squad_list(squads)
    bot.editMessageText(MSG_SQUAD_LIST,
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=markup)


def trigger_order_button(bot: Bot, update: Update, user: User, data: dict, chat_data: dict):
    if 'btn' in chat_data:
        chat_data['btn'] = not chat_data['btn']
    else:
        chat_data['btn'] = False
    if data['g']:
        admin_user = Session.query(Admin).filter(Admin.user_id == update.callback_query.from_user.id).all()
        markup = generate_order_groups_markup(
            admin_user,
            chat_data['pin'] if 'pin' in chat_data else True,
            chat_data['btn'] if 'btn' in chat_data else True)
        bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    else:
        markup = generate_order_chats_markup(chat_data['pin'] if 'pin' in chat_data else True,
                                             chat_data['btn'] if 'btn' in chat_data else True)
        bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)


def trigger_order_pin(bot: Bot, update: Update, user: User, data: dict, chat_data: dict):
    if 'pin' in chat_data:
        chat_data['pin'] = not chat_data['pin']
    else:
        chat_data['pin'] = False
    if data['g']:
        admin_user = Session.query(Admin).filter(Admin.user_id == update.callback_query.from_user.id).all()
        markup = generate_order_groups_markup(
            admin_user,
            chat_data['pin'] if 'pin' in chat_data else True,
            chat_data['btn'] if 'btn' in chat_data else True)
        bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)
    else:
        markup = generate_order_chats_markup(chat_data['pin'] if 'pin' in chat_data else True,
                                             chat_data['btn'] if 'btn' in chat_data else True)
        bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)


def squad_request_decline(bot, update, user, data):
    member = Session.query(SquadMember).filter_by(user_id=data['id'], approved=False).first()
    if member:
        bot.editMessageText(MSG_SQUAD_REQUEST_DECLINED.format('@' + member.user.username),
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
        bot.editMessageText(MSG_SQUAD_REQUEST_ACCEPTED.format('@' + member.user.username),
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


def squad_request(bot, data, update, user):
    member = Session.query(SquadMember).filter_by(user_id=update.callback_query.from_user.id).first()
    if member is None:
        member = SquadMember()
        member.user_id = update.callback_query.from_user.id
        member.squad_id = data['id']
        Session.add(member)
        Session.commit()
        admins = Session.query(Admin).filter_by(admin_group=data['id']).all()
        usernames = ['@' + Session.query(User).filter_by(id=admin.user_id).first().username for admin in admins]
        bot.editMessageText(
            MSG_SQUAD_REQUESTED.format(
                member.squad.squad_name,
                WAITING_ROOM_LINK
            ),
            update.callback_query.message.chat.id,
            update.callback_query.message.message_id, parse_mode=ParseMode.HTML)
        admins = Session.query(Admin).filter_by(admin_group=member.squad.chat_id).all()
        for adm in admins:
            send_async(bot, chat_id=adm.user_id, text=MSG_SQUAD_REQUEST_NEW)
    else:
        markup = generate_leave_squad(user.id)
        bot.editMessageText(MSG_SQUAD_REQUEST_EXISTS,
                            update.callback_query.message.chat.id,
                            update.callback_query.message.message_id,
                            reply_markup=markup)


def squad_leave(bot, data, update, user):
    member = Session.query(SquadMember).filter_by(user_id=data['id']).first()
    leave_squad(bot, user, member, update.effective_message)


def list_members(bot, update, user, data):
    squad = Session.query(Squad).filter_by(chat_id=data['id']).first()
    markups = generate_squad_members(squad.members)
    for markup in markups:
        send_async(bot, chat_id=update.callback_query.message.chat.id,
                   text=squad.squad_name,
                   reply_markup=markup, parse_mode=ParseMode.HTML)


def show_skills(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    update.callback_query.answer(text=MSG_CLEARED)
    back = data['b'] if 'b' in data else False
    bot.editMessageText('{}\n{} {}'.format(user.profession.skillList, MSG_LAST_UPDATE, user.profession.date),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=generate_profile_buttons(user, back)
                        )


def show_equip(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    update.callback_query.answer(text=MSG_CLEARED)
    back = data['b'] if 'b' in data else False
    bot.editMessageText('{}\n\n{} {}'.format(user.equip.equip, MSG_LAST_UPDATE, user.equip.date),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=generate_profile_buttons(user, back)
                        )


def order_group_list(bot, update):
    bot.editMessageText(MSG_ORDER_GROUP_LIST,
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=generate_groups_manage())


def order_group_delete(bot, update, user, data):
    group = Session.query(OrderGroup).filter_by(id=data['id']).first()
    Session.delete(group)
    Session.commit()
    bot.editMessageText(MSG_ORDER_GROUP_LIST,
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=generate_groups_manage())


def order_group_add(bot: Bot, update: Update, user: User, data: dict, chat_data: dict):
    chat_data['wait_group_name'] = True
    send_async(bot, chat_id=update.callback_query.message.chat.id,
               text=MSG_ORDER_GROUP_NEW)


def order_group_tirgger_chat(bot, update, user, data):
    group = Session.query(OrderGroup).filter_by(id=data['id']).first()
    deleted = False
    for item in group.items:
        if item.chat_id == data['c']:
            Session.delete(item)
            Session.commit()
            deleted = True
    if not deleted:
        item = OrderGroupItem()
        item.group_id = group.id
        item.chat_id = data['c']
        Session.add(item)
        Session.commit()
    markup = generate_group_manage(data['id'])
    bot.editMessageText(MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=markup)


def order_group_manage(bot, update, user, data):
    group = Session.query(OrderGroup).filter_by(id=data['id']).first()
    markup = generate_group_manage(data['id'])
    bot.editMessageText(MSG_ORDER_GROUP_CONFIG_HEADER.format(group.name),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=markup)


def order_group(bot: Bot, update: Update, user: User, data: dict, chat_data: dict):
    chat_data['order_wait'] = False
    if 'txt' in data and len(data['txt']):
        chat_data['order_type'] = MessageType.TEXT
        if data['txt'] == Icons.LES.value:
            chat_data['order'] = Castle.LES.value
        elif data['txt'] == Icons.GORY.value:
            chat_data['order'] = Castle.GORY.value
        elif data['txt'] == Icons.SEA.value:
            chat_data['order'] = Castle.SEA.value
        else:
            chat_data['order'] = data['txt']
    admin_user = Session.query(Admin).filter(Admin.user_id == update.callback_query.from_user.id).all()
    markup = generate_order_groups_markup(admin_user, chat_data['pin'] if 'pin' in chat_data else True,
                                          chat_data['btn'] if 'btn' in chat_data else True)
    bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=markup)


def orders(bot: Bot, update: Update, user: User, data: dict, chat_data: dict):
    chat_data['order_wait'] = False
    if 'txt' in data and len(data['txt']):
        if data['txt'] == Icons.LES.value:
            chat_data['order'] = Castle.LES.value
        elif data['txt'] == Icons.GORY.value:
            chat_data['order'] = Castle.GORY.value
        elif data['txt'] == Icons.SEA.value:
            chat_data['order'] = Castle.SEA.value
        else:
            chat_data['order'] = data['txt']
    markup = generate_order_chats_markup(chat_data['pin'] if 'pin' in chat_data else True,
                                         chat_data['btn'] if 'btn' in chat_data else True)
    bot.editMessageText(MSG_ORDER_SEND_HEADER.format(chat_data['order']),
                        update.callback_query.message.chat.id,
                        update.callback_query.message.message_id,
                        reply_markup=markup)


def order_confirmed(bot: Bot, update: Update, user: User, data: dict, job_queue: JobQueue):
    order = Session.query(Order).filter_by(id=data['id']).first()
    if order is not None:
        squad = Session.query(Squad).filter_by(chat_id=order.chat_id).first()
        if squad is not None:
            squad_member = Session.query(SquadMember).filter_by(squad_id=squad.chat_id,
                                                                user_id=update.callback_query.from_user.id,
                                                                approved=True).first()
            if squad_member is not None:
                order_ok = Session.query(OrderCleared).filter_by(order_id=data['id'],
                                                                 user_id=squad_member.user_id).first()
                if order_ok is None and datetime.now() - order.date < timedelta(minutes=10):
                    order_ok = OrderCleared()
                    order_ok.order_id = data['id']
                    order_ok.user_id = update.callback_query.from_user.id
                    Session.add(order_ok)
                    Session.commit()
                    if order.confirmed_msg != 0:
                        if order.id not in order_updated or \
                                datetime.now() - order_updated[order.id] > timedelta(seconds=4):
                            order_updated[order.id] = datetime.now()
                            job_queue.run_once(update_confirmed, 5, order)
                    update.callback_query.answer(text=MSG_ORDER_CLEARED)
                else:
                    update.callback_query.answer(text=MSG_ORDER_CLEARED_ERROR)
            else:
                update.callback_query.answer(text=MSG_ORDER_CLEARED_ERROR)
        else:
            order_ok = Session.query(OrderCleared).filter_by(order_id=data['id'],
                                                             user_id=update.callback_query.from_user.id).first()
            if order_ok is None and datetime.now() - order.date < timedelta(minutes=10):
                order_ok = OrderCleared()
                order_ok.order_id = data['id']
                order_ok.user_id = update.callback_query.from_user.id
                Session.add(order_ok)
                Session.commit()
                if order.confirmed_msg != 0:
                    if order.id not in order_updated or \
                            datetime.now() - order_updated[order.id] > timedelta(seconds=4):
                        order_updated[order.id] = datetime.now()
                        job_queue.run_once(update_confirmed, 5, order)
                update.callback_query.answer(text=MSG_ORDER_CLEARED)
            else:
                update.callback_query.answer(text=MSG_ORDER_CLEARED_ERROR)


def show_stock(bot, update, user, data):
    user = Session.query(User).filter_by(id=data['id']).first()
    update.callback_query.answer(text=MSG_CLEARED)
    back = data['b'] if 'b' in data else False
    second_newest = Session.query(Stock).filter_by(
        user_id=update.callback_query.message.chat.id,
        stock_type=StockType.Stock.value
    ).order_by(Stock.date.desc()).limit(1).offset(1).one()
    stock_diff = stock_compare_text(second_newest.stock, user.stock.stock)

    stock = annotate_stock_with_price(bot, user.stock.stock)

    stock_text = "{}\n{}\n{}\n <i>{}: {}</i>".format(
        stock,
        MSG_CHANGES_SINCE_LAST_UPDATE,
        stock_diff,
        MSG_LAST_UPDATE,
        user.stock.date.strftime("%Y-%m-%d %H:%M:%S")
    )

    bot.editMessageText(
        stock_text,
        update.callback_query.message.chat.id,
        update.callback_query.message.message_id,
        reply_markup=generate_profile_buttons(user, back),
        parse_mode=ParseMode.HTML
    )


def set_user_quest_location(bot, update, user, data):
    user_quest = Session.query(UserQuest).filter_by(id=data['uq']).first()
    if user_quest and user_quest.user_id == update.callback_query.message.chat.id:
        location = Session.query(Location).filter_by(id=data['l']).first()
        user_quest.location = location
        Session.add(user_quest)
        Session.commit()

        bot.editMessageText(
            MSG_QUEST_OK.format(location.name),
            update.callback_query.message.chat.id,
            update.callback_query.message.message_id
        )


def set_user_foray_pledge(bot, update, user, data):
    user_quest = Session.query(UserQuest).filter_by(id=data['uq']).first()
    if user_quest and user_quest.user_id == update.callback_query.message.chat.id:
        user_quest.pledge = data['s']
        Session.add(user_quest)
        Session.commit()

        bot.editMessageText(
            MSG_FORAY_ACCEPTED_SAVED_PLEDGE if data['s'] else MSG_FORAY_ACCEPTED_SAVED,
            update.callback_query.message.chat.id,
            update.callback_query.message.message_id
        )


def inlinequery(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query
    results = []

    if query in CASTLE_LIST or query.startswith(TACTICTS_COMMAND_PREFIX):
        results = [
            InlineQueryResultArticle(id=0,
                                     title=("DEFEND " if Castle.BLUE.value == query
                                                         or query.startswith(TACTICTS_COMMAND_PREFIX)
                                            else "ATTACK ") + query,
                                     input_message_content=InputTextMessageContent(query))]
    elif query.startswith("withdraw ") or query.startswith ("deposit "):
        withdraw_requests = generate_gstock_requests(query)
        if withdraw_requests:
            for entry in withdraw_requests:
                results.append(InlineQueryResultArticle(id=uuid4(),
                                                        title=entry["label"],
                                                        input_message_content=InputTextMessageContent(entry["command"])))
    update.inline_query.answer(results)
