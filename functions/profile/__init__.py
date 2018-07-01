from config import CWBOT_ID, EXT_ID
from core.decorators import command_handler
from core.regexp import ACCESS_CODE
from core.state import get_game_state, GameState
from core.types import AdminType, Admin
from cwmq import Publisher, wrapper
from functions.common import stock_compare_text, stock_split, __ban_traitor

from functions.profile.util import *
from functions.profile.util import __send_user_with_settings
from functions.reply_markup import generate_user_markup

p = Publisher()

Session()


@command_handler(
    forward_from=CWBOT_ID,
)
def build_report_received(bot: Bot, update: Update, user: User):
    if datetime.now() - update.message.forward_date > timedelta(minutes=10):
        send_async(bot, chat_id=update.message.from_user.id, text=MSG_BUILD_REPORT_TOO_OLD)
        return
    report = re.search(BUILD_REPORT, update.message.text)

    if report and user.character:
        old_report = Session.query(BuildReport) \
            .filter(BuildReport.user_id == user.id,
                    BuildReport.date > update.message.forward_date - timedelta(minutes=5),
                    BuildReport.date < update.message.forward_date + timedelta(minutes=5)).first()
        if old_report is None:
            parse_build_reports(update.message.text, update.message.from_user.id, update.message.forward_date)
            user_builds = Session.query(BuildReport).filter_by(user_id=user.id).count()
            send_async(bot, chat_id=update.message.from_user.id, text=MSG_BUILD_REPORT_OK.format(user_builds))
        else:
            send_async(bot, chat_id=update.message.from_user.id, text=MSG_BUILD_REPORT_EXISTS)


@command_handler(
    forward_from=CWBOT_ID,
)
def repair_report_received(bot: Bot, update: Update, user: User):
    if datetime.now() - update.message.forward_date > timedelta(minutes=10):
        send_async(bot, chat_id=update.message.from_user.id, text=MSG_BUILD_REPORT_TOO_OLD)
        return
    report = re.search(REPAIR_REPORT, update.message.text)

    if report and user.character:
        old_report = Session.query(BuildReport) \
            .filter(BuildReport.user_id == user.id,
                    BuildReport.date > update.message.forward_date - timedelta(minutes=5),
                    BuildReport.date < update.message.forward_date + timedelta(minutes=5)).first()
        if old_report is None:
            parse_repair_reports(update.message.text, update.message.from_user.id, update.message.forward_date)
            user_builds = Session.query(BuildReport).filter_by(user_id=user.id).count()
            send_async(bot, chat_id=update.message.from_user.id, text=MSG_BUILD_REPORT_OK.format(user_builds))
        else:
            send_async(bot, chat_id=update.message.from_user.id, text=MSG_BUILD_REPORT_EXISTS)


@command_handler(
    forward_from=CWBOT_ID,
    allow_channel=True,
    allow_group=True,
    allow_private=True
)
def report_received(bot: Bot, update: Update, user: User):
    #logging.info("Handling report for %s", user.id)
    #if datetime.now() - update.message.forward_date > timedelta(minutes=1):
    #    send_async(bot, chat_id=update.message.chat.id, text=MSG_REPORT_OLD)
    #    return

    state = get_game_state()
    if user.is_api_stock_allowed and user.setting_automated_report and GameState.NO_REPORTS in state:
        text = MSG_NO_REPORT_PHASE_BEFORE_BATTLE if GameState.NIGHT in state else MSG_NO_REPORT_PHASE_AFTER_BATTLE
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=text,
            parse_mode=ParseMode.HTML)
        return

    parsed_report = parse_report_text(update.message.text)
    if parsed_report and user.character and parsed_report['name'] == user.character.name:
        date = update.message.forward_date
        if (update.message.forward_date.hour < 7):
            date = update.message.forward_date - timedelta(days=1)

        time_from = date.replace(hour=(int((update.message.forward_date.hour + 1) / 8)
                                       * 8 - 1 + 24) % 24, minute=0, second=0)

        date = update.message.forward_date
        if (update.message.forward_date.hour == 23):
            date = update.message.forward_date + timedelta(days=1)

        time_to = date.replace(hour=(int((update.message.forward_date.hour + 1) / 8 + 1) * 8 - 1) %
                               24, minute=0, second=0)

        report = Session.query(Report).filter(
            Report.date > time_from,
            Report.date < time_to,
            Report.user_id == update.message.from_user.id
        ).first()

        if report and report.castle != CASTLE:
            __ban_traitor(bot, update.message.from_user.id)
            return

        if not report or (report and report.preliminary_report):
            save_report(update.message.text, update.message.from_user.id, update.message.forward_date)
            if report and report.castle != CASTLE:
                __ban_traitor(bot, update.message.from_user.id)
            show_report(bot, update, user)
        else:
            send_async(bot, chat_id=update.message.from_user.id, text=MSG_REPORT_EXISTS)


@command_handler(
    forward_from=CWBOT_ID,
)
def char_update(bot: Bot, update: Update, user: User):
    logging.debug("Beginning char update")
    if update.message.date - update.message.forward_date > timedelta(minutes=1):
        send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_OLD)
        return

    state = get_game_state()
    if user.is_api_stock_allowed and user.setting_automated_report and GameState.NO_REPORTS in state:
        text = MSG_NO_REPORT_PHASE_BEFORE_BATTLE if GameState.NIGHT in state else MSG_NO_REPORT_PHASE_AFTER_BATTLE
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=text,
            parse_mode=ParseMode.HTML)
        return

    char = None
    if re.search(HERO, update.message.text):
        char = parse_hero(
            bot,
            update.message.text,
            update.message.from_user.id,
            update.message.forward_date,
        )

    if CASTLE:
        if char and (char.castle == CASTLE or update.message.from_user.id == EXT_ID):
            char.castle = CASTLE
            send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_SAVED.format(char.name),
                       parse_mode=ParseMode.HTML)
        else:
            send_async(bot, chat_id=update.message.chat.id,
                       text=MSG_PROFILE_CASTLE_MISTAKE, parse_mode=ParseMode.HTML)
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_SAVED.format(char.name),
                   parse_mode=ParseMode.HTML)
    if char and char.castle != CASTLE:
        __ban_traitor(bot, update.message.from_user.id)


@command_handler(
    forward_from=CWBOT_ID,
)
def profession_update(bot: Bot, update: Update, user: User):
    if update.message.date - update.message.forward_date > timedelta(minutes=1):
        send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_OLD)
    else:
        profession = None
        if re.search(PROFESSION, update.message.text):
            profession = parse_profession(update.message.text,
                                          update.message.from_user.id,
                                          update.message.forward_date,
                                          )
            if profession:
                send_async(
                    bot,
                    chat_id=update.message.chat.id,
                    text=MSG_SKILLS_SAVED.format(
                        profession.name),
                    parse_mode=ParseMode.HTML)


@command_handler()
def show_char(bot: Bot, update: Update, user: User):
    if user.is_api_profile_allowed and user.is_api_stock_allowed:
        try:
            wrapper.update_stock(user)
            wrapper.update_profile(user)
        except wrapper.APIInvalidTokenException as ex:
            logging.error("This should not happen!?! %s", ex)
        except wrapper.APIMissingAccessRightsException as ex:
            logging.warning("Missing permissions for User '%s': %s", user.id, ex)
            if str(ex) == "User has not given permission for stock":
                wrapper.request_stock_access(bot, user)
            elif str(ex) == "User has not given permission for profile":
                wrapper.request_profile_access(bot, user)
        except wrapper.APIMissingUserException:
            logging.error("No/Invalid user for create_want_to_uy specified")

    if user.character:
        char = user.character
        profession = user.profession
        if CASTLE:
            if char.castle == CASTLE or user.id == EXT_ID:
                char.castle = CASTLE
                text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char, profession)
                btns = generate_profile_buttons(user)
                send_async(bot, chat_id=update.message.chat.id, text=text,
                           reply_markup=btns, parse_mode=ParseMode.HTML)
        else:
            text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char, profession)
            btns = generate_profile_buttons(user)
            send_async(bot, chat_id=update.message.chat.id, text=text, reply_markup=btns, parse_mode=ParseMode.HTML)
    else:
        text = MSG_NO_PROFILE_IN_BOT
        btns = generate_profile_buttons(user)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=text,
            reply_markup=btns,
            parse_mode=ParseMode.HTML
        )


@command_handler()
def show_report(bot: Bot, update: Update, user: User):
    existing_report = get_latest_report(user.id)

    # Nothing to show
    if not existing_report:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=MSG_REPORT_MISSING,
            reply_markup=generate_user_markup(user_id=user.id),
            parse_mode=ParseMode.HTML,
        )
    else:
        text = format_report(existing_report)

        # Treat every report up to 30 min after battle as one relevant for report-diff / Get the first one after battle
        filter_from = existing_report.date.replace(minute=0, second=0, microsecond=0)

        # Get the oldest stock-report from after war for this comparison...
        before_war_stock, after_war_stock = get_stock_before_after_war(user)
        logging.debug("after_war_stock: %s", after_war_stock)
        logging.debug("Second before_war_stock stock: %s", before_war_stock)

        stock_diff = "<i>Missing before/after war data to generate comparison. Sorry.</i>"

        if before_war_stock and after_war_stock:
            resources_new, resources_old = stock_split(before_war_stock.stock, after_war_stock.stock)
            stock_diff = stock_compare_text(before_war_stock.stock, after_war_stock.stock)

        stock_text = MSG_USER_BATTLE_REPORT_STOCK.format(
            MSG_CHANGES_SINCE_LAST_UPDATE,
            stock_diff,
            before_war_stock.date.strftime("%Y-%m-%d %H:%M:%S") if before_war_stock else "Missing",
            after_war_stock.date.strftime("%Y-%m-%d %H:%M:%S") if after_war_stock else "Missing",
        )
        text += stock_text
        if user.character and user.character.characterClass == "Knight":
            text += TRIBUTE_NOTE

        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=text,
            reply_markup=generate_user_markup(user_id=user.id),
            parse_mode=ParseMode.HTML,
        )


@command_handler()
def revoke(bot: Bot, update: Update, user: User):
    user.api_token = None
    user.is_api_profile_allowed = False
    user.is_api_stock_allowed = False
    user.is_api_trade_allowed = False
    Session.add(user)
    Session.commit()

    send_async(
        bot,
        chat_id=user.id,
        text=MSG_API_ACCESS_RESET,
        reply_markup=generate_user_markup(user.id),
        parse_mode=ParseMode.HTML
    )


@command_handler(
    squad_only=True
)
def grant_access(bot: Bot, update: Update, user: User):
    reg_req = {
        "action": "createAuthCode",
        "payload": {
            "userId": update.message.chat.id
        }
    }
    p.publish(reg_req)
    send_async(
        bot,
        chat_id=user.id,
        text=MSG_API_INFO,
        parse_mode=ParseMode.HTML
    )


@command_handler()
def handle_access_token(bot: Bot, update: Update, user: User):
    """ Handle a forwarded access code to authorize API access by bot.
    Note: We do not send back a confirmation at this point. User should be notified after async answer from APMQ
    TODO: Maybe add some kind of timeout if API is not availiable? """

    # Extract token...
    code = re.search(ACCESS_CODE, update.message.text)
    if not code:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_API_INVALID_CODE, parse_mode=ParseMode.HTML)
        return

    # For what is this code. Send the right response
    if user.api_request_id and user.api_grant_operation:
        logging.debug("This is an ADDITIONAL operation")
        add_grant_req = {
            "action": "grantAdditionalOperation",
            "token": user.api_token,
            "payload": {
                "requestId": user.api_request_id,
                "authCode": code.group(2),
            }
        }
        p.publish(add_grant_req)
    else:
        grant_req = {
            "action": "grantToken",
            "payload": {
                "userId": update.message.chat.id,
                "authCode": code.group(2),
            }
        }
        p.publish(grant_req)


@command_handler()
def user_panel(bot: Bot, update: Update, user: User):
    user = Session.query(User).filter_by(id=update.message.from_user.id).first()

    welcome_text = MSG_START_KNOWN
    if user.is_squadmember:
        if user.api_token:
            welcome_text = MSG_START_MEMBER_SQUAD_REGISTERED.format(
                user.character.name if user.character else "Soldier!"
            )

            if user.setting_automated_sniping and user.sniping_suspended:
                welcome_text += "\n\n" + SNIPE_SUSPENDED_NOTICE
        else:
            welcome_text = MSG_START_MEMBER_SQUAD.format(user.character.name if user.character else "Soldier!")

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=generate_user_markup(user_id=update.message.from_user.id)
    )


@command_handler()
def settings(bot: Bot, update: Update, user: User):
    send_settings(bot, update, user)


@command_handler(
    min_permission=AdminType.GROUP,
)
def find_by_username(bot: Bot, update: Update, user: User):
    if update.message.chat.type == 'private':
        msg = update.message.text.split(' ', 1)[1]
        msg = msg.replace('@', '')
        if msg:
            account = Session.query(User).filter_by(username=msg).first()

            if account:
                admin = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
                global_adm = False
                for adm in admin:
                    if adm.admin_type <= AdminType.FULL.value:
                        global_adm = True
                        break

                if global_adm:
                    __send_user_with_settings(bot, update, account)
                    return
                else:
                    group_ids = []
                    for adm in admin:
                        group_ids.append(adm.admin_group)

                    if account.member.squad.chat_id in group_ids:
                        __send_user_with_settings(bot, update, account)
                        return

        send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_NOT_FOUND, parse_mode=ParseMode.HTML)


@command_handler(
    min_permission=AdminType.GROUP,
)
def find_by_character(bot: Bot, update: Update, user: User):
    if update.message.chat.type == 'private':
        msg = update.message.text.split(' ', 1)[1]
        msg = msg.replace('@', '')
        if msg:
            account = Session.query(Character).filter_by(name=msg).order_by(Character.date.desc()).first()
            if account:
                account = account.user

                admin = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
                global_adm = False
                for adm in admin:
                    if adm.admin_type <= AdminType.FULL.value:
                        global_adm = True
                        break

                if global_adm:
                    __send_user_with_settings(bot, update, account)
                    return
                else:
                    group_ids = []
                    for adm in admin:
                        group_ids.append(adm.admin_group)

                    if account.member.squad.chat_id in group_ids:
                        __send_user_with_settings(bot, update, account)
                        return

        send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_NOT_FOUND, parse_mode=ParseMode.HTML)


@command_handler(
    min_permission=AdminType.GROUP,
)
def find_by_id(bot: Bot, update: Update, user: User):
    if update.message.chat.type == 'private':
        msg = update.message.text.split(' ', 1)[1]
        msg = msg.replace('@', '')
        if msg:
            account = Session.query(User).filter_by(id=msg).first()

            if account:
                admin = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
                global_adm = False
                for adm in admin:
                    if adm.admin_type <= AdminType.FULL.value:
                        global_adm = True
                        break

                if global_adm:
                    __send_user_with_settings(bot, update, account)
                    return
                else:
                    group_ids = []
                    for adm in admin:
                        group_ids.append(adm.admin_group)

                    if account.member.squad.chat_id in group_ids:
                        __send_user_with_settings(bot, update, account)
                        return

        send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_NOT_FOUND, parse_mode=ParseMode.HTML)


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
