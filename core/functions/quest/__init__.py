import json
import re
from enum import IntFlag, auto

from core.decorators import command_handler
from core.functions.inline_markup import QueryType
from core.functions.quest.parse import QuestType, analyze_text
from core.texts import MSG_QUEST, MSG_QUEST_DUPLICATE, MSG_QUEST_ACCEPTED, MSG_FORAY_ACCEPTED, MSG_FORAY_PLEDGE, \
    BTN_PLEDGE_YES, BTN_PLEDGE_NO
from core.types import (Item, Location, Quest, Session, User, UserQuest,
                        UserQuestItem)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update, Bot

Session()

def save_user_quest(user: User, update: Update, quest_data):
    uq = UserQuest()
    uq.user = user
    uq.forward_date = update.message.forward_date
    uq.exp = quest_data['exp']
    uq.gold = quest_data['gold']
    if quest_data['type'] == QuestType.FORAY:
        uq.location = Session.query(Location).filter(Location.name == "🗡Foray").first()
    if quest_data['type'] in [QuestType.FORAY_FAILED, QuestType.STOP_FAIL]:
        uq.successful = False
    else:
        uq.successful = True
    uq.level = user.character.level if user.character else 0  # If we don't have a profile yet just assume "0" level

    quest = Session.query(Quest).filter_by(text=quest_data['text']).first()
    if quest:
        uq.quest = quest
    else:
        q = Quest()
        q.text = quest_data['text']
        Session.add(q)
        uq.quest = q

    for name, count in quest_data['items'].items():
        item = Session.query(Item).filter_by(name=name).first()
        if not item:
            item = Item()
            item.name = name
            Session.add(item)
            Session.commit()

        uqi = UserQuestItem(count=count, item_id=item.id)
        uq.items.append(uqi)

    Session.add(uq)
    Session.commit()

    return uq

@command_handler()
def parse_quest(bot: Bot, update: Update, user: User):
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
        uq = save_user_quest(user, update, quest_data)

        inline_keys = []
        for location in Session.query(Location).filter(Location.selectable == True).all():
            inline_keys.append(
                [
                    InlineKeyboardButton(location.name, callback_data=json.dumps(
                        {
                            't': QueryType.QuestFeedbackRequired,
                            'l': location.id,
                            'uq': uq.id
                        }
                    ))
                ]
            )
        inline_keyboard = InlineKeyboardMarkup(inline_keys)

        bot.sendMessage(
            chat_id=user.id,
            text=MSG_QUEST,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_keyboard
        )
    elif quest_data['type'] == QuestType.FORAY_PLEDGE:
        bot.sendMessage(
            chat_id=user.id,
            text=MSG_FORAY_PLEDGE,
            parse_mode=ParseMode.HTML,
        )
    elif quest_data['type'] == QuestType.FORAY:
        uq = save_user_quest(user, update, quest_data)

        if user.character and user.character.characterClass == "Knight":
            inline_keys = [
                [InlineKeyboardButton(BTN_PLEDGE_YES, callback_data=json.dumps({
                    't': QueryType.ForayFeedbackRequired,
                    's': True,
                    'uq': uq.id
                }))],
                [InlineKeyboardButton(BTN_PLEDGE_NO, callback_data=json.dumps({
                    't': QueryType.ForayFeedbackRequired,
                    's': False,
                    'uq': uq.id
                }))],
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
    elif quest_data['type'] == QuestType.STOP:
        uq = save_user_quest(user, update, quest_data)

        bot.sendMessage(
            chat_id=user.id,
            text=MSG_FORAY_ACCEPTED,
            parse_mode=ParseMode.HTML,
        )
    elif quest_data['type'] == QuestType.STOP:
        uq = save_user_quest(user, update, quest_data)

        bot.sendMessage(
            chat_id=user.id,
            text=MSG_FORAY_ACCEPTED,
            parse_mode=ParseMode.HTML,
        )