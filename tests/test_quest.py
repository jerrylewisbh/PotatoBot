import re
import os
import sys
import unittest

from enum import IntFlag, auto

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.fixtures import *
from core.functions.quest import *


class TestTime(unittest.TestCase):
    def test_quest_identification(self):
        """ Try to identify quests """

        for successful in QUESTS_SUCCESSFUL:
            self.assertEqual(analyze_text(successful)["type"], QuestType.NORMAL)

    def test_quest_fail_identification(self):
        """ Try to identify quests """

        for successful in QUESTS_FAILED:
            self.assertEqual(analyze_text(successful)["type"], QuestType.NORMAL_FAILED)

    def test_foray_clueless_identification(self):
        """ Try to identify quests """

        self.assertEqual(analyze_text(FORAY_CLUELESS)["type"], QuestType.FORAY)

    def test_foray_stop_success_identification(self):
        """ Try to identify quests """

        self.assertEqual(analyze_text(FORAY_GO_SUCCESS)["type"], QuestType.FORAY)

    def test_foray_stop_fail_identification(self):
        """ Try to identify quests """

        self.assertEqual(analyze_text(FORAY_TRIED_STOPPING)["type"], QuestType.FORAY_STOP)
        self.assertEqual(analyze_text(FORAY_TRIED_STOPPING_YOU)["type"], QuestType.FORAY_STOP)


if __name__ == '__main__':
    unittest.main()
