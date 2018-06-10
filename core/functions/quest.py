import json
import re
from enum import IntFlag, auto

from core.decorators import command_handler
from core.functions.inline_markup import QueryType
from core.texts import MSG_QUEST, MSG_QUEST_DUPLICATE, MSG_QUEST_ACCEPTED, MSG_FORAY_ACCEPTED, MSG_FORAY_PLEDGE
from core.types import (Item, Location, Quest, Session, User, UserQuest,
                        UserQuestItem)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update, Bot

Session()

class QuestType(IntFlag):
    NORMAL = auto()
    NORMAL_FAILED = auto()
    FORAY = auto()
    FORAY_STOP = auto()
    FORAY_PLEDGE = auto()
    ARENA = auto()


REGEX_GOLD_EXP = r"((?:You received: )(?:([0-9]+) exp and )([0-9]+) gold)"
REGEX_EARNED = r"(Earned: (?:(.+) (?:\(([0-9]+)\))))"
REGEX_FORAY_SUCCESS = r"((?:Received )(?:([0-9]+) gold and )([0-9]+) exp.)"
REGEX_FORAY_TRIED = r"((?:Received: )([0-9]+) exp.)"
REGEX_FORAY_PLEDGE = r"To accept their offer, you shall /pledge to protect. You have 3 minutes to decide."
REGEX_ARENA = r"((?:You received: )([0-9]+) exp.)"


def analyze_text(text):
    find_quest_gold_exp = re.findall(REGEX_GOLD_EXP, text)
    find_earned = re.findall(REGEX_EARNED, text)
    find_foray_success = re.findall(REGEX_FORAY_SUCCESS, text)
    find_foray_tried_to_stop = re.findall(REGEX_FORAY_TRIED, text)
    find_foray_pledge = re.findall(REGEX_FORAY_PLEDGE, text)
    find_arena = re.findall(REGEX_ARENA, text)

    text_stripped = re.sub(REGEX_GOLD_EXP, '', text)
    text_stripped = re.sub(REGEX_EARNED, '', text_stripped)
    text_stripped = re.sub(REGEX_FORAY_SUCCESS, '', text_stripped)
    text_stripped = re.sub(REGEX_FORAY_TRIED, '', text_stripped)
    text_stripped = re.sub(REGEX_ARENA, '', text_stripped)
    text_stripped = text_stripped.strip()

    if find_foray_success:
        items = {}
        for item in find_earned:
            items[item[1]] = item[2]
        return {
            'type': QuestType.FORAY,
            'items': items,
            'gold': find_quest_gold_exp[0][2] if find_quest_gold_exp else 0,
            'exp': find_quest_gold_exp[0][1] if find_quest_gold_exp else 0,
            'text': text_stripped,
        }
    if find_quest_gold_exp or find_earned:
        items = {}
        for item in find_earned:
            items[item[1]] = item[2]
        return {
            'type': QuestType.NORMAL,
            'items': items,
            'gold': find_quest_gold_exp[0][2] if find_quest_gold_exp else  0,
            'exp': find_quest_gold_exp[0][1] if find_quest_gold_exp else 0,
            'text': text_stripped,
        }
    elif find_foray_tried_to_stop:
        return {
            'type': QuestType.FORAY_STOP,
            'items': {},
            'gold': 0,
            'exp': 0,
            'text': text_stripped,
        }
    elif find_foray_pledge:
        return {
            'type': QuestType.FORAY_PLEDGE,
            'items': {},
            'gold': 0,
            'exp': 0,
            'text': text_stripped,
        }
    elif find_arena:
        return {
            'type': QuestType.ARENA,
            'items': {},
            'gold': 0,
            'exp': 0,
            'text': text_stripped,
        }
    else:
        return {
            'type': QuestType.NORMAL_FAILED,
            'items': {},
            'gold': 0,
            'exp': 0,
            'text': text_stripped,
        }


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

    uq = UserQuest()
    uq.user = user
    uq.forward_date = update.message.forward_date
    uq.exp = quest_data['exp']
    uq.gold = quest_data['gold']
    if quest_data['type'] == QuestType.FORAY_PLEDGE:
        uq.pledge = True
        uq.location = Session.query(Location).filter(Location.name == "🗡Foray").first()
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

    # We need details about the location of the quest if it's a normal one...
    # Note: Max. 64 bytes for callback data. Because of this there is no user_id. Instead we're getting that one in
    # callback handler via sql...
    if quest_data['type'] == QuestType.NORMAL:
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
        bot.sendMessage(
            chat_id=user.id,
            text=MSG_FORAY_ACCEPTED,
            parse_mode=ParseMode.HTML,
        )
    elif quest_data['type'] == QuestType.FORAY_STOP:
        bot.sendMessage(
            chat_id=user.id,
            text=MSG_FORAY_ACCEPTED,
            parse_mode=ParseMode.HTML,
        )
