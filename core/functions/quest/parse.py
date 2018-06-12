import re
from enum import IntFlag, auto

# Gold / Exp
REGEX_GOLD_EXP = r"((?:You received: )(?:([0-9]+) exp and )([0-9]+) gold)"
REGEX_EARNED = r"(Earned: (?:(.+) (?:\(([0-9]+)\))))"

# Foray - Sucess exp/gold is in changed order to normal quests...
REGEX_FORAY_SUCCESS = r"((?:Received )(?:([0-9]+) gold and )([0-9]+) exp.)"
REGEX_FORAY_NEARLY_BEAT = 'noticed you and nearly beat you to death. You crawled back home to a nice warm bath.'
REGEX_FORAY_TRIED_STOPPING = r"tried stopping you, but you were stronger. You have satisfied your lust for violence"
REGEX_FORAY_PLEDGE = r"To accept their offer, you shall /pledge to protect. You have 3 minutes to decide."
REGEX_LOST = '((?:Lost: )(-[0-9]+) gold)'

# Stopping forays
REGEX_GO = r"As he was crawling away, you picked up some of the gold he left behind."
REGEX_GO_FAILED = r"Sadly, he was too strong. Your body hurts"

REGEX_FORAY_GO_FAILED_REWARD = r"((?:Received: )([0-9]+) exp.)"

REGEX_ARENA = r"((?:You received: )([0-9]+) exp.)"


class QuestType(IntFlag):
    NORMAL = auto()
    NORMAL_FAILED = auto()

    FORAY = auto()
    FORAY_FAILED = auto()
    FORAY_PLEDGE = auto()

    STOP = auto()
    STOP_FAIL = auto()

    ARENA = auto()
    ARENA_FAIL = auto()

    UNKNOWN = auto()


def analyze_text(text):
    # Normal quests
    find_quest_gold_exp = re.findall(REGEX_GOLD_EXP, text)
    text_stripped = re.sub(REGEX_GOLD_EXP, '', text)

    find_earned = re.findall(REGEX_EARNED, text)
    text_stripped = re.sub(REGEX_EARNED, '', text_stripped)

    # Foray
    find_foray_success = re.findall(REGEX_FORAY_SUCCESS, text)
    text_stripped = re.sub(REGEX_FORAY_SUCCESS, '', text_stripped)

    find_foray_tried_stopping = re.findall(REGEX_FORAY_TRIED_STOPPING, text)
    text_stripped = re.sub(REGEX_FORAY_TRIED_STOPPING, '', text_stripped)

    find_foray_stopped = re.findall(REGEX_FORAY_NEARLY_BEAT, text)
    text_stripped = re.sub(REGEX_FORAY_NEARLY_BEAT, '', text_stripped)

    find_foray_go_failed_reward = re.findall(REGEX_FORAY_GO_FAILED_REWARD, text)
    text_stripped = re.sub(REGEX_FORAY_GO_FAILED_REWARD, '', text_stripped)

    find_foray_lost = re.findall(REGEX_LOST, text)
    text_stripped = re.sub(REGEX_LOST, '', text_stripped)

    find_foray_pledge = re.findall(REGEX_FORAY_PLEDGE, text)

    # Stopping forays
    find_go = re.findall(REGEX_GO, text)
    find_go_failed = re.findall(REGEX_GO_FAILED, text)

    text_stripped = re.sub(REGEX_GO, '', text_stripped)

    # Arena
    find_arena = re.findall(REGEX_ARENA, text)
    text_stripped = re.sub(REGEX_ARENA, '', text_stripped)

    text_stripped = text_stripped.strip()

    if find_go:
        return {
            'type': QuestType.STOP,
            'success': True,
            'items': {},
            'gold': int(find_foray_success[0][1]) if find_foray_success else 0,
            'exp': int(find_foray_success[0][2]) if find_foray_success else 0,
            'text': text_stripped,
        }
    elif find_go_failed:
        return {
            'type': QuestType.STOP_FAIL,
            'success': False,
            'items': {},
            'gold': 0,
            'exp': int(find_foray_go_failed_reward[0][1]) if find_foray_go_failed_reward else 0,
            'text': text_stripped,
        }
    elif find_foray_success:
        items = {}
        for item in find_earned:
            items[item[1]] = item[2]
        return {
            'type': QuestType.FORAY,
            'success': True,
            'items': items,
            'gold': int(find_foray_success[0][1]) if find_foray_success else 0,
            'exp': int(find_foray_success[0][2]) if find_foray_success else 0,
            'text': text_stripped,
        }
    elif find_quest_gold_exp or find_earned:
        items = {}
        for item in find_earned:
            items[item[1]] = item[2]
        return {
            'type': QuestType.NORMAL,
            'success': True,
            'items': items,
            'gold': find_quest_gold_exp[0][2] if find_quest_gold_exp else 0,
            'exp': find_quest_gold_exp[0][1] if find_quest_gold_exp else 0,
            'text': text_stripped,
        }
    elif find_foray_tried_stopping:
        return {
            'type': QuestType.FORAY_FAILED,
            'success': False,
            'items': {},
            'gold': 0,
            'exp': int(find_foray_go_failed_reward[0][1]) if find_foray_go_failed_reward else 0,
            'text': text_stripped,
        }
    elif find_foray_stopped:
        return {
            'type': QuestType.FORAY_FAILED,
            'success': False,
            'items': {},
            'gold': int(find_foray_lost[0][1]) if find_foray_lost else 0,
            'exp': 0,
            'text': text_stripped,
        }
    elif find_foray_pledge:
        return {
            'type': QuestType.FORAY_PLEDGE,
            'success': True,
            'items': {},
            'gold': 0,
            'exp': 0,
            'text': text_stripped,
        }
    elif find_arena:
        return {
            'type': QuestType.ARENA,
            # TODO!!!
            'items': {},
            'gold': 0,
            'exp': 0,
            'text': text_stripped,
        }
    else:
        return {
            'type': QuestType.UNKNOWN,
            'items': {},
            'gold': 0,
            'exp': 0,
            'text': text_stripped,
        }
