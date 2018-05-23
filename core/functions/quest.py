import re
import json
import logging

from enum import auto, IntFlag

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from core.functions.inline_markup import QueryType
from core.texts import MSG_QUEST, MSG_QUEST_DUPLICATE
from core.types import Session, User, UserQuest, Quest, Item, Location, UserQuestItem

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


class QuestType(IntFlag):
    NORMAL = auto()
    NORMAL_FAILED = auto()
    FORAY = auto()
    FORAY_STOP = auto()
    ARENA = auto()


REGEX_GOLD_EXP = r"((?:You received: )(?:([0-9]+) exp and )([0-9]+) gold)"
REGEX_EARNED = r"(Earned: (?:(.+) (?:\(([0-9]+)\))))"
REGEX_FORAY_SUCCESS = r"((?:Received )(?:([0-9]+) gold and )([0-9]+) exp.)"
REGEX_FORAY_TRIED = r"((?:Received: )([0-9]+) exp.)"
REGEX_ARENA = r"((?:You received: )([0-9]+) exp.)"

def analyze_text(text):
    find_quest_gold_exp = re.findall(REGEX_GOLD_EXP, text)
    find_quest_earned = re.findall(REGEX_EARNED, text)
    find_foray_success = re.findall(REGEX_FORAY_SUCCESS, text)
    find_foray_tried_to_stop = re.findall(REGEX_FORAY_TRIED, text)
    find_arena = re.findall(REGEX_ARENA, text)

    text_stripped = re.sub(REGEX_GOLD_EXP, '', text)
    text_stripped = re.sub(REGEX_EARNED, '', text_stripped)
    text_stripped = re.sub(REGEX_FORAY_SUCCESS, '', text_stripped)
    text_stripped = re.sub(REGEX_FORAY_TRIED, '', text_stripped)
    text_stripped = re.sub(REGEX_ARENA, '', text_stripped)
    text_stripped = text_stripped.strip()

    if  find_quest_gold_exp or find_quest_earned:
        items = {}
        for item in find_quest_earned:
            items[item[1]] = item[2]
        return {
            'type': QuestType.NORMAL,
            'items': items,
            'gold': find_quest_gold_exp[0][1],
            'exp':  find_quest_gold_exp[0][2],
            'text': text_stripped,
        }
    elif find_foray_success:
        return QuestType.FORAY
    elif find_foray_tried_to_stop:
        return QuestType.FORAY_STOP
    elif find_arena:
        return QuestType.ARENA
    else:
        return {
            'type': QuestType.NORMAL_FAILED,
            'items': {},
            'gold': 0,
            'exp':  0,
            'text': text_stripped,
        }


def parse_quest(bot, update):
    data = analyze_text(update.message.text)

    session = Session()
    user = session.query(User).filter_by(id=update.message.from_user.id).first()

    existing_user_quest = session.query(UserQuest).filter_by(
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
    uq.exp = data['exp']
    uq.gold = data['gold']
    uq.level = user.character.level

    quest = session.query(Quest).filter_by(text=data['text']).first()
    if quest:
        uq.quest = quest
    else:
        q = Quest()
        q.text = data['text']
        session.add(q)
        uq.quest = q

    for name, count in data['items'].items():
        item = session.query(Item).filter_by(name=name).first()
        if not item:
            item = Item()
            item.name = name
            session.add(item)
            session.commit()

        uqi = UserQuestItem(count=count, item_id=item.id)
        uq.items.append(uqi)

    session.add(uq)
    session.commit()

    # We need details about the location of the quest if it's a normal one...
    # Note: Max. 64 bytes for callback data. Because of this there is no user_id. Instead we're getting that one in
    # callback handler via sql...
    if data['type'] == QuestType.NORMAL:
        inline_keys = []
        for location in session.query(Location).all():
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
            text=MSG_QUEST.format(data['text']),
            parse_mode=ParseMode.HTML,
            reply_markup=inline_keyboard
        )
