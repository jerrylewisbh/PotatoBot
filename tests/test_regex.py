import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions.profile import parse_hero_text, parse_report_text
from functions.profile import user_panel

class TestRegex(unittest.TestCase):
    def test_report_parsing(self):
        """ Test if Report can be parsed """

        test = """🥔[GO]Kroket van Potet ⚔:12 🛡:34 Lvl: 56
Your result on the battlefield:
🔥Exp: 123
💰Gold: 456"""

        parsed_data = parse_report_text(test)
        self.assertNotEqual(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['name'], "[GO]Kroket van Potet")
        self.assertEqual(parsed_data['attack'], 12)
        self.assertEqual(parsed_data['defence'], 34)
        self.assertEqual(parsed_data['guild'], "[GO]")
        self.assertEqual(parsed_data['ribbon'], None)
        self.assertEqual(parsed_data['level'], 56)
        self.assertEqual(parsed_data['exp'], 123)
        self.assertEqual(parsed_data['gold'], 456)
        self.assertEqual(parsed_data['stock'], 0)

    def test_report_parsing_ribbon(self):
        """ Test if Report can be parsed """
        test = """🥔[GO]🎗Kroket van Potet ⚔:12 🛡:34 Lvl: 56
Your result on the battlefield:
🔥Exp: 123
💰Gold: 456"""

        parsed_data = parse_report_text(test)
        self.assertNotEqual(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['name'], "[GO]Kroket van Potet")
        self.assertEqual(parsed_data['attack'], 12)
        self.assertEqual(parsed_data['guild'], "[GO]")
        self.assertEqual(parsed_data['ribbon'], "🎗")
        self.assertEqual(parsed_data['defence'], 34)
        self.assertEqual(parsed_data['level'], 56)
        self.assertEqual(parsed_data['exp'], 123)
        self.assertEqual(parsed_data['gold'], 456)
        self.assertEqual(parsed_data['stock'], 0)

    def test_report_parsing_ribbon_guildless(self):
        """ Test if Report can be parsed """
        test = """🥔🎗Kroket van Potet ⚔:12 🛡:34 Lvl: 56
Your result on the battlefield:
🔥Exp: 123
💰Gold: 456"""

        parsed_data = parse_report_text(test)
        self.assertNotEqual(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['name'], "Kroket van Potet")
        self.assertEqual(parsed_data['attack'], 12)
        self.assertEqual(parsed_data['guild'], "")
        self.assertEqual(parsed_data['ribbon'], "🎗")
        self.assertEqual(parsed_data['defence'], 34)
        self.assertEqual(parsed_data['level'], 56)
        self.assertEqual(parsed_data['exp'], 123)
        self.assertEqual(parsed_data['gold'], 456)
        self.assertEqual(parsed_data['stock'], 0)

    def test_report_parsing_guildless(self):
        """ Test if Report can be parsed """
        test = """🥔Kroket van Potet ⚔:12 🛡:34 Lvl: 56
Your result on the battlefield:
🔥Exp: 123
💰Gold: 456"""

        parsed_data = parse_report_text(test)
        self.assertNotEqual(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['name'], "Kroket van Potet")
        self.assertEqual(parsed_data['attack'], 12)
        self.assertEqual(parsed_data['guild'], "")
        self.assertEqual(parsed_data['ribbon'], None)
        self.assertEqual(parsed_data['defence'], 34)
        self.assertEqual(parsed_data['level'], 56)
        self.assertEqual(parsed_data['exp'], 123)
        self.assertEqual(parsed_data['gold'], 456)
        self.assertEqual(parsed_data['stock'], 0)

    def test_hero_parsing_ribbon(self):
        test = """🥔🎗Fozzie
🏅Level: 23
⚔Atk: 73 🛡Def: 64
🔥Exp: 11451/13123
🔋Stamina: 1/6
💰27 👝2 💎12
📚Expertise: 📕
🏛Class info: /class



🎽Equipment +38⚔+46🛡:
Rapier +27⚔
Mithril dagger +7⚔
Mithril helmet +12🛡
Mithril gauntlets +8🛡
Mithril armor +3⚔ +17🛡
Mithril boots +8🛡
Royal Guard Cape +1⚔ +1🛡

🎒Bag: 13/15 /inv
📦Warehouse: 635 /stock"""

        parsed_data = parse_hero_text(test)
        self.assertNotEqual(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['castle_name'], "Potato")
        self.assertEqual(parsed_data['name'], "Fozzie")
        self.assertEqual(parsed_data['attack'], 73)
        self.assertEqual(parsed_data['guild'], "")
        self.assertEqual(parsed_data['ribbon'], "🎗")
        self.assertEqual(parsed_data['defence'], 64)
        self.assertEqual(parsed_data['level'], 23)
        self.assertEqual(parsed_data['exp'], 11451)
        self.assertEqual(parsed_data['gold'], 27)
        self.assertEqual(parsed_data['stamina'], 1)
        self.assertEqual(parsed_data['max_stamina'], 6)
        self.assertEqual(parsed_data['pouches'], 2)
        self.assertEqual(parsed_data['exp_needed'], 13123)
        # self.assertEqual(parsed_data['expertise'], "📕")
        self.assertEqual(parsed_data['diamonds'], 12)
        self.assertIsNotNone(parsed_data['equipment'])

    def test_hero_parsing_missings(self):
        test = """🥔Fozzie
🏅Level: 23
⚔Atk: 73 🛡Def: 64
🔥Exp: 11451/13123
🔋Stamina: 1/6
💰27
📚Expertise: 📕
🏛Class info: /class



🎽Equipment +38⚔+46🛡:
Rapier +27⚔
Mithril dagger +7⚔
Mithril helmet +12🛡
Mithril gauntlets +8🛡
Mithril armor +3⚔ +17🛡
Mithril boots +8🛡
Royal Guard Cape +1⚔ +1🛡

🎒Bag: 13/15 /inv
📦Warehouse: 635 /stock"""

        parsed_data = parse_hero_text(test)
        self.assertNotEqual(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['castle_name'], "Potato")
        self.assertEqual(parsed_data['name'], "Fozzie")
        self.assertEqual(parsed_data['attack'], 73)
        self.assertEqual(parsed_data['guild'], "")
        self.assertEqual(parsed_data['ribbon'], None)
        self.assertEqual(parsed_data['defence'], 64)
        self.assertEqual(parsed_data['level'], 23)
        self.assertEqual(parsed_data['exp'], 11451)
        self.assertEqual(parsed_data['gold'], 27)
        self.assertEqual(parsed_data['stamina'], 1)
        self.assertEqual(parsed_data['max_stamina'], 6)
        self.assertEqual(parsed_data['pouches'], 0)
        self.assertEqual(parsed_data['exp_needed'], 13123)
        # self.assertEqual(parsed_data['expertise'], "📕")
        self.assertEqual(parsed_data['diamonds'], 0)
        self.assertIsNotNone(parsed_data['equipment'])

    def test_hero_parsing_full(self):
        test = """🥔Fozzie
🏅Level: 23
⚔Atk: 73 🛡Def: 64
🔥Exp: 11451/13123
🔋Stamina: 1/6
💰27 👝2 💎12
📚Expertise: 📕
🏛Class info: /class



🎽Equipment +38⚔+46🛡:
Rapier +27⚔
Mithril dagger +7⚔
Mithril helmet +12🛡
Mithril gauntlets +8🛡
Mithril armor +3⚔ +17🛡
Mithril boots +8🛡
Royal Guard Cape +1⚔ +1🛡

🎒Bag: 13/15 /inv
📦Warehouse: 635 /stock"""

        parsed_data = parse_hero_text(test)
        self.assertNotEqual(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['castle_name'], "Potato")
        self.assertEqual(parsed_data['name'], "Fozzie")
        self.assertEqual(parsed_data['attack'], 73)
        self.assertEqual(parsed_data['guild'], "")
        self.assertEqual(parsed_data['ribbon'], None)
        self.assertEqual(parsed_data['defence'], 64)
        self.assertEqual(parsed_data['level'], 23)
        self.assertEqual(parsed_data['exp'], 11451)
        self.assertEqual(parsed_data['gold'], 27)
        self.assertEqual(parsed_data['stamina'], 1)
        self.assertEqual(parsed_data['max_stamina'], 6)
        self.assertEqual(parsed_data['pouches'], 2)
        self.assertEqual(parsed_data['exp_needed'], 13123)
        # self.assertEqual(parsed_data['expertise'], "📕")
        self.assertEqual(parsed_data['diamonds'], 12)
        self.assertIsNotNone(parsed_data['equipment'])

    def test_hero_parsing_next(self):
        test = """🥔[AVE]Lauri van Potet
🏅Level: 36
⚔️Atk: 154 🛡Def: 91
🔥Exp: 121913/122982
🔋Stamina: 0/16
💰36 👝301
📚Expertise: 📕📗📘
🏛Class info: /class


🎽Equipment +59⚔️+50🛡
Champion Sword +31⚔️
Hunter dagger +10⚔️
Hunter Helmet +5⚔️ +11🛡
Order Gauntlets +2⚔️ +10🛡
Hunter Armor +8⚔️ +18🛡
Order Boots +2⚔️ +10🛡
Royal Guard Cape +1⚔️ +1🛡

🎒Bag: 14/15 /inv
📦Warehouse: 163 /stock"""

        parsed_data = parse_hero_text(test)
        self.assertNotEqual(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['castle_name'], "Potato")
        self.assertEqual(parsed_data['name'], "[AVE]Lauri van Potet")
        self.assertEqual(parsed_data['attack'], 154)
        self.assertEqual(parsed_data['guild'], "[AVE]")
        self.assertEqual(parsed_data['ribbon'], None)
        self.assertEqual(parsed_data['defence'], 91)
        self.assertEqual(parsed_data['level'], 36)
        self.assertEqual(parsed_data['exp'], 121913)
        self.assertEqual(parsed_data['gold'], 36)
        self.assertEqual(parsed_data['stamina'], 0)
        self.assertEqual(parsed_data['max_stamina'], 16)
        self.assertEqual(parsed_data['pouches'], 301)
        self.assertEqual(parsed_data['exp_needed'], 122982)
        # self.assertEqual(parsed_data['expertise'], "📕")
        self.assertEqual(parsed_data['diamonds'], 0)
        self.assertIsNotNone(parsed_data['equipment'])

    def test_hero_parsing_pet(self):
        test = """🦈[R1]Maling
🏅Level: 45
⚔️Atk: 166 🛡Def: 141
🔥Exp: 303151/320501
🔋Stamina: 8/9
💰83 👝74 💎169
📚Expertise: 📕📗📘📙
🏛Class info: /class



Pet:
🐷 shoat Rogue (5 lvl) 😁 /pet

🎽Equipment +59⚔️+48🛡
⚡️+3 Rapier +30⚔️
⚡️+3 Mithril dagger +10⚔️
Hunter Helmet +5⚔️ +11🛡
Hunter Gloves +3⚔️ +8🛡
Hunter Armor +8⚔️ +18🛡
Order Boots +2⚔️ +10🛡
Royal Guard Cape +1⚔️ +1🛡

🎒Bag: 7/15 /inv
📦Warehouse: 580 /stock"""

        parsed_data = parse_hero_text(test)
        self.assertNotEqual(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🦈")
        self.assertEqual(parsed_data['castle_name'], "Sharkteeth")
        self.assertEqual(parsed_data['name'], "[R1]Maling")
        self.assertEqual(parsed_data['attack'], 166)
        self.assertEqual(parsed_data['guild'], "[R1]")
        self.assertEqual(parsed_data['ribbon'], None)
        self.assertEqual(parsed_data['defence'], 141)
        self.assertEqual(parsed_data['level'], 45)
        self.assertEqual(parsed_data['exp'], 303151)
        self.assertEqual(parsed_data['gold'], 83)
        self.assertEqual(parsed_data['stamina'], 8)
        self.assertEqual(parsed_data['max_stamina'], 9)
        self.assertEqual(parsed_data['pouches'], 74)
        self.assertEqual(parsed_data['exp_needed'], 320501)
        # self.assertEqual(parsed_data['expertise'], "📕")
        self.assertEqual(parsed_data['diamonds'], 169)
        self.assertIsNotNone(parsed_data['equipment'])




if __name__ == '__main__':
    # Force TZ!
    import os

    os.environ['TZ'] = 'UTC'

    unittest.main()
