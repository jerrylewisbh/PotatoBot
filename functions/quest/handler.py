import logging

from sqlalchemy import collate
from sqlalchemy.exc import SQLAlchemyError
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup

from config import QUEST_LOCATION_FORAY_ID, QUEST_LOCATION_DEFEND_ID, QUEST_LOCATION_ARENA_ID, CWBOT_ID
from core.bot import MQBot
from core.decorators import command_handler
from core.handler.callback import CallbackAction, get_callback_action
from core.handler.callback.util import create_callback
from core.state import get_game_state, GameState
from core.texts import MSG_QUEST_DUPLICATE, MSG_QUEST, MSG_FORAY_FAILED, MSG_FORAY_PLEDGE, BTN_PLEDGE_YES, \
    BTN_PLEDGE_NO, MSG_FORAY_ACCEPTED, MSG_ARENA_ACCEPTED, MSG_ARENA_FAILED, MSG_QUEST_OK, \
    MSG_FORAY_ACCEPTED_SAVED_PLEDGE, MSG_FORAY_ACCEPTED_SAVED
from core.types import User, UserQuest, Session, Quest, Item, UserQuestItem, Location
from functions.quest import QuestType
from functions.quest.parse import analyze_text

Session()

def __save_user_quest(user: User, update: Update, quest_data):
    uq = UserQuest()
    uq.user = user
    uq.forward_date = update.message.forward_date
    uq.exp = quest_data['exp']
    uq.gold = quest_data['gold']

    # Set Daytime (remove additional time-markers)
    daytime = get_game_state(update.message.forward_date)
    daytime &= ~GameState.HOWLING_WIND
    daytime &= ~GameState.NO_REPORTS
    daytime &= ~GameState.BATTLE_SILENCE
    uq.daytime = daytime.value

    uq.successful = quest_data['success']
    if quest_data['type'] in [QuestType.FORAY, QuestType.FORAY_FAILED]:
        uq.location_id = QUEST_LOCATION_FORAY_ID
    elif quest_data['type'] in [QuestType.STOP, QuestType.STOP_FAIL]:
        uq.location_id = QUEST_LOCATION_DEFEND_ID
    elif quest_data['type'] in [QuestType.ARENA, QuestType.ARENA_FAIL]:
        uq.location_id = QUEST_LOCATION_ARENA_ID

    uq.level = user.character.level if user.character else 0  # If we don't have a profile yet just assume "0" level

    if QuestType.NORMAL:
        # Only store quest texts for normal ones...
        quest = Session.query(Quest).filter_by(text=quest_data['text']).first()
        if quest:
            uq.quest = quest
        else:
            q = Quest()
            q.text = quest_data['text']
            Session.add(q)
            uq.quest = q

    for name, count in quest_data['items'].items():
        item = Session.query(Item).filter(
            Item.name == collate(name, 'utf8mb4_unicode_520_ci')
        ).first()
        if not item:
            item = Item()
            item.name = name
            try:
                Session.add(item)
                Session.commit()
            except SQLAlchemyError as err:
                logging.error(str(err))
                Session.rollback()

        uqi = UserQuestItem(count=count, item_id=item.id)
        uq.items.append(uqi)

    try:
        Session.add(uq)
        Session.commit()
    except Exception as ex:
        logging.exception("Could not insert quest into DB. Rollaback!")
        try:
            Session.rollback()
        except Exception:
            logging.exception("Additional error during rollback!")

    return uq


@command_handler(
    forward_from=CWBOT_ID
)
def parse_quest(bot: MQBot, update: Update, user: User):
    logging.info("Parsing quest for user_id='%s'", user.id)
    quest_data = analyze_text(update.message.text)

    user = Session.query(User).filter_by(id=update.message.from_user.id).first()

    existing_user_quest = Session.query(UserQuest).filter_by(
        forward_date=update.message.forward_date,
        user_id=user.id
    ).first()

    if existing_user_quest:
        bot.sendMessage(
            chat_id=user.id,
            text=MSG_QUEST_DUPLICATE,
            parse_mode=ParseMode.HTML,
        )
        return

    # We need details about the location of the quest if it's a normal one...
    # Note: Max. 64 bytes for callback data. Because of this there is no user_id. Instead we're getting that one in
    # callback handler via sql...
    if quest_data['type'] == QuestType.NORMAL:
        uq = __save_user_quest(user, update, quest_data)

        inline_keys = []
        for location in Session.query(Location).filter(Location.selectable.is_(True)).all():
            inline_keys.append(
                [
                    InlineKeyboardButton(
                        location.name,
                        callback_data=create_callback(
                            CallbackAction.QUEST_LOCATION,
                            user.id,
                            user_quest_id=uq.id,
                            location_id=location.id,
                        )
                    )
                ]
            )
        inline_keyboard = InlineKeyboardMarkup(inline_keys)

        bot.sendMessage(
            chat_id=user.id,
            text=MSG_QUEST.format(quest_data["text"] if quest_data and quest_data["text"] else ""),
            parse_mode=ParseMode.HTML,
            reply_markup=inline_keyboard
        )
    elif quest_data['type'] == QuestType.FORAY_FAILED:
        uq = __save_user_quest(user, update, quest_data)

        bot.sendMessage(
            chat_id=user.id,
            text=MSG_FORAY_FAILED,
            parse_mode=ParseMode.HTML,
        )
    elif quest_data['type'] == QuestType.FORAY_PLEDGE:
        bot.sendMessage(
            chat_id=user.id,
            text=MSG_FORAY_PLEDGE,
            parse_mode=ParseMode.HTML,
        )
    elif quest_data['type'] == QuestType.FORAY:
        uq = __save_user_quest(user, update, quest_data)

        if user.character and user.character.characterClass == "Knight":
            inline_keys = [
                [
                    InlineKeyboardButton(
                        BTN_PLEDGE_YES,
                        callback_data=create_callback(
                            CallbackAction.FORAY_PLEDGE,
                            user.id,
                            user_quest_id=uq.id,
                            pledge=True,
                        )
                    )
                ],
                [
                    InlineKeyboardButton(
                        BTN_PLEDGE_NO,
                        callback_data=create_callback(
                            CallbackAction.FORAY_PLEDGE,
                            user.id,
                            user_quest_id=uq.id,
                            pledge=False,
                        )
                    )
                ]
            ]
            inline_keyboard = InlineKeyboardMarkup(inline_keys)
            bot.sendMessage(
                chat_id=user.id,
                text=MSG_FORAY_PLEDGE,
                parse_mode=ParseMode.HTML,
                reply_markup=inline_keyboard
            )
        else:
            bot.sendMessage(
                chat_id=user.id,
                text=MSG_FORAY_ACCEPTED,
                parse_mode=ParseMode.HTML
            )
    elif quest_data['type'] in [QuestType.ARENA, QuestType.ARENA_FAIL]:
        uq = __save_user_quest(user, update, quest_data)

        bot.sendMessage(
            chat_id=user.id,
            text=MSG_ARENA_ACCEPTED if quest_data['type'] == QuestType.ARENA else MSG_ARENA_FAILED,
            parse_mode=ParseMode.HTML,
        )
    elif quest_data['type'] == QuestType.STOP:
        uq = __save_user_quest(user, update, quest_data)

        bot.sendMessage(
            chat_id=user.id,
            text=MSG_FORAY_ACCEPTED,
            parse_mode=ParseMode.HTML,
        )
    elif quest_data['type'] == QuestType.STOP_FAIL:
        uq = __save_user_quest(user, update, quest_data)

        bot.sendMessage(
            chat_id=user.id,
            text=MSG_FORAY_FAILED,
            parse_mode=ParseMode.HTML,
        )


@command_handler()
def set_user_quest_location(bot, update, user):
    action = get_callback_action(update.callback_query.data, user.id)
    if not action:
        logging.warning("set_user_foray_pledge got no valid action!")
        return

    user_quest = Session.query(UserQuest).filter_by(id=action.data['user_quest_id']).first()
    if user_quest and user_quest.user_id == update.callback_query.message.chat.id:
        location = Session.query(Location).filter_by(id=action.data['location_id']).first()
        user_quest.location = location
        try:
            Session.add(user_quest)
            Session.commit()
        except SQLAlchemyError as err:
            logging.error(str(err))
            Session.rollback()

        bot.editMessageText(
            MSG_QUEST_OK.format(location.name),
            update.callback_query.message.chat.id,
            update.callback_query.message.message_id
        )


@command_handler()
def set_user_foray_pledge(bot, update, user):
    action = get_callback_action(update.callback_query.data, user.id)
    if not action:
        logging.warning("set_user_foray_pledge got no valid action!")
        return

    user_quest = Session.query(UserQuest).filter_by(id=action.data['user_quest_id']).first()
    if user_quest and user_quest.user_id == update.callback_query.message.chat.id:
        user_quest.pledge = action.data['pledge']

        try:
            Session.add(user_quest)
            Session.commit()
        except SQLAlchemyError as err:
            logging.error(str(err))
            Session.rollback()

        bot.editMessageText(
            MSG_FORAY_ACCEPTED_SAVED_PLEDGE if action.data['pledge'] else MSG_FORAY_ACCEPTED_SAVED,
            update.callback_query.message.chat.id,
            update.callback_query.message.message_id
        )
