import os
import sys
import unittest

from tests.fixtures import *

from core.functions.quest.parse import QuestType, analyze_text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestTime(unittest.TestCase):
    def test_quest_identification(self):
        for successful in QUESTS_SUCCESSFUL:
            self.assertEqual(analyze_text(successful)["type"], QuestType.NORMAL)

    def test_quest_fail_identification(self):
        for successful in QUESTS_FAILED:
            self.assertEqual(analyze_text(successful)["type"], QuestType.UNKNOWN)

    def test_foray_clueless_identification(self):
        a = analyze_text(FORAY_CLUELESS)
        self.assertEqual(a["type"], QuestType.FORAY)
        self.assertEqual(a["gold"], 33)
        self.assertEqual(a["exp"], 12)
        self.assertEqual(a["items"], {})

        a = analyze_text(FORAY_CLUELESS_LOOT)
        self.assertEqual(a["type"], QuestType.FORAY)
        self.assertEqual(a["gold"], 31)
        self.assertEqual(a["exp"], 92)
        self.assertNotEqual(a["items"], {})

    def test_go_success_identification(self):
        a = analyze_text(GO)
        self.assertEqual(a["type"], QuestType.STOP)
        self.assertEqual(a["gold"], 10)
        self.assertEqual(a["exp"], 39)
        self.assertEqual(a["items"], {})

    def test_go_fail_identification(self):
        a = analyze_text(GO_FAILED)
        self.assertEqual(a["type"], QuestType.STOP_FAIL)
        self.assertEqual(a["gold"], 0)
        self.assertEqual(a["exp"], 2)
        self.assertEqual(a["items"], {})

    def test_foray_stop_fail_identification(self):
        a = analyze_text(FORAY_TRIED_STOPPING)
        self.assertEqual(a["type"], QuestType.FORAY_FAILED)
        self.assertEqual(a["gold"], 0)
        self.assertEqual(a["exp"], 73)
        self.assertEqual(a["items"], {})

    def test_foray_stopped(self):
        a = analyze_text(FORAY_NEARLY_BEAT)
        self.assertEqual(a["type"], QuestType.FORAY_FAILED)
        self.assertEqual(a["gold"], -6)
        self.assertEqual(a["exp"], 0)
        self.assertEqual(a["items"], {})

    def test_foray_pledge(self):
        self.assertEqual(analyze_text(FORAY_PLEDGE)["type"], QuestType.FORAY_PLEDGE)


if __name__ == '__main__':
    unittest.main()
