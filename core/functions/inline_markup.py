import json
import logging
from datetime import datetime, timedelta
from enum import IntFlag, auto

from sqlalchemy import func, tuple_
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import CASTLE
from core.enums import Castle
from core.texts import (BTN_ACCEPT, BTN_ALL_TIME, BTN_DECLINE, BTN_EQUIPMENT,
                        BTN_HERO, BTN_LEAVE, BTN_NO, BTN_PROFESSIONS,
                        BTN_SETTING_API_DISABLE,
                        BTN_SETTING_DISABLE_DEAL_REPORT,
                        BTN_SETTING_DISABLE_REPORT,
                        BTN_SETTING_ENABLE_DEAL_REPORT,
                        BTN_SETTING_ENABLE_REPORT, BTN_SQUAD_ALL_TIME,
                        BTN_SQUAD_WEEK, BTN_STOCK, BTN_WEEK, BTN_YES, MSG_BACK,
                        MSG_GROUP_STATUS, MSG_GROUP_STATUS_ADMIN_FORMAT,
                        MSG_GROUP_STATUS_DEL_ADMIN, MSG_OFF, MSG_ON,
                        MSG_ORDER_ACCEPT, MSG_ORDER_BUTTON, MSG_ORDER_FORWARD,
                        MSG_ORDER_GROUP_ADD, MSG_ORDER_GROUP_DEL,
                        MSG_ORDER_NO_BUTTON, MSG_ORDER_NO_PIN, MSG_ORDER_PIN,
                        MSG_ORDER_TO_SQUADS, MSG_SQUAD_GREEN_INLINE_BUTTON,
                        MSG_SQUAD_RED_INLINE_BUTTON, MSG_SYMBOL_OFF,
                        MSG_SYMBOL_ON, BTN_SETTING_ENABLE_SNIPING, BTN_SETTING_DISABLE_SNIPING,
                        BTN_SETTING_DISABLE_HIDE_GOLD, BTN_SETTING_ENABLE_HIDE_GOLD)
from core.types import (Admin, AdminType, Character, Group, OrderGroup, Squad,
                        User, Session)

Session()

class QueryType(IntFlag):
    GroupList = auto()
    GroupInfo = auto()
    DelAdm = auto()
    Order = auto()
    OrderOk = auto()
    Orders = auto()
    OrderGroup = auto()
    OrderGroupManage = auto()
    OrderGroupTriggerChat = auto()
    OrderGroupAdd = auto()
    OrderGroupDelete = auto()
    OrderGroupList = auto()
    ShowStock = auto()
    ShowEquip = auto()
    ShowHero = auto()
    MemberList = auto()
    LeaveSquad = auto()
    RequestSquad = auto()
    RequestSquadAccept = auto()
    RequestSquadDecline = auto()
    InviteSquadAccept = auto()
    InviteSquadDecline = auto()
    TriggerOrderPin = auto()
    SquadList = auto()
    GroupDelete = auto()
    TriggerOrderButton = auto()
    OtherReport = auto()
    GlobalBuildTop = auto()
    WeekBuildTop = auto()
    SquadGlobalBuildTop = auto()
    SquadWeekBuildTop = auto()
    BattleGlobalTop = auto()
    BattleWeekTop = auto()
    Forward = auto()
    ShowSkills = auto()

    DisableAPIAccess = auto()
    DisableAutomatedReport = auto()
    EnableAutomatedReport = auto()

    DisableDealReport = auto()
    EnableDealReport = auto()

    QuestFeedbackRequired = auto()
    ForayFeedbackRequired = auto()

    DisableSniping = auto()
    EnableSniping = auto()

    DisableHideGold = auto()
    EnableHideGold = auto()

    Yes = auto()
    No = auto()


def generate_group_info(group_id):
    group = Session.query(Group).filter(Group.id == group_id).first()
    admins = Session.query(Admin).filter(Admin.admin_group == group_id).all()
    adm_msg = ''
    adm_del_keys = []
    for adm in admins:
        user = Session.query(User).filter_by(id=adm.user_id).first()
        adm_msg += MSG_GROUP_STATUS_ADMIN_FORMAT.\
            format(user.id, user.username or '', user.first_name or '', user.last_name or '')
        adm_del_keys.append([InlineKeyboardButton(MSG_GROUP_STATUS_DEL_ADMIN.
                                                  format(user.first_name or '', user.last_name or ''),
                                                  callback_data=json.dumps(
                                                      {'t': QueryType.DelAdm.value, 'uid': user.id,
                                                       'gid': group_id}))])
    msg = MSG_GROUP_STATUS.format(group.title,
                                  adm_msg,
                                  MSG_ON if group.welcome_enabled else MSG_OFF,
                                  MSG_ON if group.allow_trigger_all else MSG_OFF,
                                  MSG_ON if len(group.squad) and group.squad[0].thorns_enabled else MSG_OFF)
    adm_del_keys.append([InlineKeyboardButton(MSG_ORDER_GROUP_DEL, callback_data=json.dumps(
        {'t': QueryType.GroupDelete.value, 'gid': group_id}))])
    adm_del_keys.append([InlineKeyboardButton(MSG_BACK, callback_data=json.dumps(
        {'t': QueryType.GroupList.value}))])
    inline_markup = InlineKeyboardMarkup(adm_del_keys)
    return msg, inline_markup


def generate_flag_orders():
    flag_btns = [InlineKeyboardButton(Castle.BLACK.value, callback_data=json.dumps(
        {'t': QueryType.OrderGroup.value, 'txt': Castle.BLACK.value})),
        InlineKeyboardButton(Castle.WHITE.value, callback_data=json.dumps(
            {'t': QueryType.OrderGroup.value, 'txt': Castle.WHITE.value})),
        InlineKeyboardButton(Castle.BLUE.value, callback_data=json.dumps(
            {'t': QueryType.OrderGroup.value, 'txt': Castle.BLUE.value})),
        InlineKeyboardButton(Castle.YELLOW.value, callback_data=json.dumps(
            {'t': QueryType.OrderGroup.value, 'txt': Castle.YELLOW.value})),
        InlineKeyboardButton(Castle.RED.value, callback_data=json.dumps(
            {'t': QueryType.OrderGroup.value, 'txt': Castle.RED.value})),
        InlineKeyboardButton(Castle.DUSK.value, callback_data=json.dumps(
            {'t': QueryType.OrderGroup.value, 'txt': Castle.DUSK.value})),
        InlineKeyboardButton(Castle.MINT.value, callback_data=json.dumps(
            {'t': QueryType.OrderGroup.value, 'txt': Castle.MINT.value})),
        # InlineKeyboardButton(Castle.GORY.value, callback_data=json.dumps(
        #     {'t': QueryType.OrderGroup.value, 'txt': Icons.GORY.value})),
        # InlineKeyboardButton(Castle.LES.value, callback_data=json.dumps(
        #     {'t': QueryType.OrderGroup.value, 'txt': Icons.LES.value})),
        # InlineKeyboardButton(Castle.SEA.value, callback_data=json.dumps(
        #     {'t': QueryType.OrderGroup.value, 'txt': Icons.SEA.value}))
    ]
    btns = []
    i = 0
    for btn in flag_btns:
        if CASTLE:
            if btn.text == CASTLE:
                continue
        if i % 3 == 0:
            btns.append([])
        btns[-1].append(btn)
        i += 1

    if CASTLE:
        btns.append([])
        for btn in flag_btns:
            if btn.text == CASTLE:
                btns[-1].append(btn)

    inline_markup = InlineKeyboardMarkup(btns)
    return inline_markup


def generate_order_chats_markup(pin=True, btn=True):
    squads = Session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        inline_keys.append([InlineKeyboardButton(squad.squad_name, callback_data=json.dumps(
            {'t': QueryType.Order.value, 'g': False, 'id': squad.chat_id}))])
    inline_keys.append([InlineKeyboardButton(MSG_ORDER_PIN if pin else MSG_ORDER_NO_PIN, callback_data=json.dumps(
        {'t': QueryType.TriggerOrderPin.value, 'g': False}))])
    inline_keys.append([InlineKeyboardButton(MSG_ORDER_BUTTON if btn else MSG_ORDER_NO_BUTTON, callback_data=json.dumps(
        {'t': QueryType.TriggerOrderButton.value, 'g': False}))])
    inline_markup = InlineKeyboardMarkup(inline_keys)
    return inline_markup


def generate_order_groups_markup(admin_user: list=None, pin: bool=True, btn=True):
    if admin_user:
        group_adm = True
        for adm in admin_user:
            if adm.admin_type < AdminType.GROUP.value:
                group_adm = False
                break
        if group_adm:
            inline_keys = []
            for adm in admin_user:
                group = Session.query(Group).filter_by(id=adm.admin_group, bot_in_group=True).first()
                if group:
                    inline_keys.append([InlineKeyboardButton(group.title, callback_data=json.dumps(
                        {'t': QueryType.Order.value, 'g': False, 'id': group.id}))])
            inline_keys.append(
                [InlineKeyboardButton(MSG_ORDER_PIN if pin else MSG_ORDER_NO_PIN, callback_data=json.dumps(
                    {'t': QueryType.TriggerOrderPin.value, 'g': True}))])
            inline_keys.append(
                [InlineKeyboardButton(MSG_ORDER_BUTTON if btn else MSG_ORDER_NO_BUTTON, callback_data=json.dumps(
                    {'t': QueryType.TriggerOrderButton.value, 'g': True}))])
            inline_markup = InlineKeyboardMarkup(inline_keys)
            return inline_markup
        else:
            groups = Session.query(OrderGroup).all()
            inline_keys = []
            for group in groups:
                inline_keys.append([InlineKeyboardButton(group.name, callback_data=json.dumps(
                    {'t': QueryType.Order.value, 'g': True, 'id': group.id}))])
            inline_keys.append([InlineKeyboardButton(MSG_ORDER_TO_SQUADS, callback_data=json.dumps(
                {'t': QueryType.Orders.value}))])
            inline_keys.append([InlineKeyboardButton(MSG_ORDER_PIN if pin else MSG_ORDER_NO_PIN,
                                                     callback_data=json.dumps(
                                                         {'t': QueryType.TriggerOrderPin.value, 'g': True}))])
            inline_keys.append([InlineKeyboardButton(MSG_ORDER_BUTTON if btn else MSG_ORDER_NO_BUTTON,
                                                     callback_data=json.dumps(
                                                         {'t': QueryType.TriggerOrderButton.value, 'g': True}))])
            inline_markup = InlineKeyboardMarkup(inline_keys)
            return inline_markup


def generate_ok_markup(order_id, count, forward=False, order=''):

    buttons = [[InlineKeyboardButton(MSG_ORDER_ACCEPT.format(count),
                                     callback_data=json.dumps(
        {'t': QueryType.OrderOk.value, 'id': order_id}))]]
    if forward:
        buttons.append([InlineKeyboardButton(text=MSG_ORDER_FORWARD, switch_inline_query=order)])
    inline_markup = InlineKeyboardMarkup(buttons)
    return inline_markup


def generate_forward_markup(order_id, count):
    inline_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=MSG_ORDER_FORWARD, switch_inline_query=order_id)]])
    return inline_markup


def generate_groups_manage():
    groups = Session.query(OrderGroup).all()
    inline_keys = []
    for group in groups:
        inline_keys.append([InlineKeyboardButton(group.name, callback_data=json.dumps(
            {'t': QueryType.OrderGroupManage.value, 'id': group.id}))])
    inline_keys.append([InlineKeyboardButton(MSG_ORDER_GROUP_ADD, callback_data=json.dumps(
        {'t': QueryType.OrderGroupAdd.value}))])
    return InlineKeyboardMarkup(inline_keys)


def generate_group_manage(group_id):
    squads = Session.query(Squad).all()
    inline_keys = []
    for squad in squads:
        in_group = False
        for item in squad.chat.group_items:
            if item.group_id == group_id:
                in_group = True
                break
        inline_keys.append([InlineKeyboardButton((MSG_SYMBOL_ON if in_group else MSG_SYMBOL_OFF) +
                                                 squad.squad_name, callback_data=json.dumps(
            {'t': QueryType.OrderGroupTriggerChat.value, 'id': group_id, 'c': squad.chat_id}))])
    inline_keys.append([InlineKeyboardButton(MSG_ORDER_GROUP_DEL, callback_data=json.dumps(
        {'t': QueryType.OrderGroupDelete.value, 'id': group_id}))])
    inline_keys.append([InlineKeyboardButton(MSG_BACK, callback_data=json.dumps(
        {'t': QueryType.OrderGroupList.value}))])
    return InlineKeyboardMarkup(inline_keys)


def generate_profile_buttons(user, back_key=False):
    inline_keys = [[InlineKeyboardButton(BTN_HERO, callback_data=json.dumps(
        {'t': QueryType.ShowHero.value, 'id': user.id, 'b': back_key}))]]
    if user.stock:
        inline_keys.append([InlineKeyboardButton(BTN_STOCK, callback_data=json.dumps(
            {'t': QueryType.ShowStock.value, 'id': user.id, 'b': back_key}))])
    if user.equip:
        inline_keys.append([InlineKeyboardButton(BTN_EQUIPMENT, callback_data=json.dumps(
            {'t': QueryType.ShowEquip.value, 'id': user.id, 'b': back_key}))])
    if user.profession:
        inline_keys.append([InlineKeyboardButton(BTN_PROFESSIONS, callback_data=json.dumps(
            {'t': QueryType.ShowSkills.value, 'id': user.id, 'b': back_key}))])
    if back_key:
        inline_keys.append(
            [InlineKeyboardButton(MSG_BACK,
                                  callback_data=json.dumps(
                                      {'t': QueryType.MemberList.value, 'id': user.member.squad_id}
                                  ))])
    return InlineKeyboardMarkup(inline_keys)


def generate_settings_buttons(user, back_key=False):
    inline_keys = []
    if user.api_token:
        inline_keys.append(
            [
                InlineKeyboardButton(BTN_SETTING_API_DISABLE, callback_data=json.dumps(
                    {'t': QueryType.DisableAPIAccess, 'id': user.id, 'b': back_key}
                ))
            ]
        )
    if user.is_squadmember and user.is_api_stock_allowed and user.is_api_profile_allowed and user.api_token:
        if user.setting_automated_report:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_DISABLE_REPORT, callback_data=json.dumps(
                        {'t': QueryType.DisableAutomatedReport, 'id': user.id, 'b': back_key}
                    ))
                ]
            )
        else:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_ENABLE_REPORT, callback_data=json.dumps(
                        {'t': QueryType.EnableAutomatedReport, 'id': user.id, 'b': back_key}
                    ))
                ]
            )
        if user.setting_automated_deal_report:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_DISABLE_DEAL_REPORT, callback_data=json.dumps(
                        {'t': QueryType.DisableDealReport, 'id': user.id, 'b': back_key}
                    ))
                ]
            )
        else:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_ENABLE_DEAL_REPORT, callback_data=json.dumps(
                        {'t': QueryType.EnableDealReport, 'id': user.id, 'b': back_key}
                    ))
                ]
            )
    if user.is_squadmember and user.is_api_trade_allowed and user.api_token:
        if user.setting_automated_sniping:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_DISABLE_SNIPING, callback_data=json.dumps(
                        {'t': QueryType.DisableSniping, 'id': user.id, 'b': back_key}
                    ))
                ]
            )
        else:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_ENABLE_SNIPING, callback_data=json.dumps(
                        {'t': QueryType.EnableSniping, 'id': user.id, 'b': back_key}
                    ))
                ]
            )
    if user.is_tester and user.is_api_trade_allowed and user.api_token:
        if user.setting_automated_hiding:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_DISABLE_HIDE_GOLD, callback_data=json.dumps(
                        {'t': QueryType.DisableHideGold, 'id': user.id, 'b': back_key}
                    ))
                ]
            )
        else:
            inline_keys.append(
                [
                    InlineKeyboardButton(BTN_SETTING_ENABLE_HIDE_GOLD, callback_data=json.dumps(
                        {'t': QueryType.EnableHideGold, 'id': user.id, 'b': back_key}
                    ))
                ]
            )
    if inline_keys:
        return InlineKeyboardMarkup(inline_keys)
    return None


def generate_squad_list_key(squad):
    attack = 0
    defence = 0
    level = 0
    members = squad.members
    user_ids = []
    for member in members:
        user_ids.append(member.user_id)
    actual_profiles = Session.query(Character.user_id, func.max(Character.date)).\
        filter(Character.user_id.in_(user_ids)).\
        group_by(Character.user_id).all()
    characters = Session.query(Character).filter(tuple_(Character.user_id, Character.date)
                                                 .in_([(a[0], a[1]) for a in actual_profiles])).all()
    for character in characters:
        attack += character.attack
        defence += character.defence
        level += character.level
    return [InlineKeyboardButton(
        '{} : {}⚔ {}🛡 {}👥 {}🏅'.format(
            squad.squad_name,
            attack,
            defence,
            len(members),
            int(level / (len(members) or 1))
        ),
        callback_data=json.dumps({'t': QueryType.MemberList.value, 'id': squad.chat_id}))]


def generate_yes_no(user_id):
    inline_keys = [InlineKeyboardButton(BTN_YES,
                                        callback_data=json.dumps(
                                            {'t': QueryType.Yes.value, 'id': user_id})),
                   InlineKeyboardButton(BTN_NO,
                                        callback_data=json.dumps(
                                            {'t': QueryType.No.value, 'id': user_id}))]
    return InlineKeyboardMarkup([inline_keys])


def generate_squad_list(squads):
    inline_keys = []
    for squad in squads:
        inline_keys.append(generate_squad_list_key(squad))
    return InlineKeyboardMarkup(inline_keys)


def generate_leave_squad(user_id):
    inline_keys = [[InlineKeyboardButton(BTN_LEAVE,
                                         callback_data=json.dumps({'t': QueryType.LeaveSquad.value,
                                                                   'id': user_id}))]]
    return InlineKeyboardMarkup(inline_keys)


def generate_squad_request():
    inline_keys = []
    squads = Session.query(Squad).filter_by(hiring=True).all()
    for squad in squads:
        inline_keys.append([InlineKeyboardButton(squad.squad_name,
                                                 callback_data=json.dumps(
                                                     {'t': QueryType.RequestSquad.value, 'id': squad.chat_id}))])
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


def generate_squad_members(members):
    inline_keys = []
    inline_list = []
    user_ids = []
    limit = 50
    count = 0
    limit = limit if len(members) > limit else len(members)
    for member in members:
        user_ids.append(member.user_id)
    actual_profiles = Session.query(Character.user_id, func.max(Character.date)). \
        filter(Character.user_id.in_(user_ids)). \
        group_by(Character.user_id).all()
    characters = Session.query(Character).filter(tuple_(Character.user_id, Character.date)
                                                 .in_([(a[0], a[1]) for a in actual_profiles]))\
        .order_by(Character.level.desc()).all()
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
        inline_keys.append(
            [InlineKeyboardButton('{}{}: {}⚔ {}🛡 {}🏅'.
                                  format(status_emoji,
                                         character.name,
                                         character.attack,
                                         character.defence,
                                         character.level),
                                  callback_data=json.dumps(
                                      {'t': QueryType.ShowHero.value,
                                       'id': character.user_id,
                                       'b': True}
                                  ))])

        count = count + 1
        if count >= limit:
            count = 0
            inline_keys.append(
                [InlineKeyboardButton(MSG_BACK,
                                      callback_data=json.dumps(
                                          {'t': QueryType.SquadList.value}
                                      ))])
            inline_list.append(InlineKeyboardMarkup(inline_keys))
            inline_keys = []

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


def generate_fire_up(members):
    inline_keys = []
    inline_list = []
    limit = 50
    count = 0
    limit = limit if len(members) > limit else len(members)
    logging.debug("generate_fire_up - limit: %s", limit)
    for member in members:
        inline_keys.append([InlineKeyboardButton('🔥{}: {}⚔ {}🛡'.format(member.user, member.user.character.attack,
                                                                         member.user.character.defence),
                                                 callback_data=json.dumps(
                                                     {'t': QueryType.LeaveSquad.value, 'id': member.user_id}))])
        count = count + 1
        if count >= limit:
            count = 0
            inline_list.append(InlineKeyboardMarkup(inline_keys))
            inline_keys = []

    return inline_list


def generate_build_top():
    inline_keys = [[InlineKeyboardButton(BTN_WEEK,
                                         callback_data=json.dumps(
                                             {'t': QueryType.WeekBuildTop.value})),
                    InlineKeyboardButton(BTN_ALL_TIME,
                                         callback_data=json.dumps(
                                             {'t': QueryType.GlobalBuildTop.value}))],
                   [InlineKeyboardButton(BTN_SQUAD_WEEK,
                                         callback_data=json.dumps(
                                             {'t': QueryType.SquadWeekBuildTop.value})),
                    InlineKeyboardButton(BTN_SQUAD_ALL_TIME,
                                         callback_data=json.dumps(
                                             {'t': QueryType.SquadGlobalBuildTop.value}))]]
    return InlineKeyboardMarkup(inline_keys)


def generate_battle_top():
    inline_keys = [[InlineKeyboardButton(BTN_WEEK,
                                         callback_data=json.dumps(
                                             {'t': QueryType.BattleWeekTop.value})),
                    InlineKeyboardButton(BTN_ALL_TIME,
                                         callback_data=json.dumps(
                                             {'t': QueryType.BattleGlobalTop.value}))]]
    return InlineKeyboardMarkup(inline_keys)
