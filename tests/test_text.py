import os
import sys
import unittest
from xml.parsers import expat

from markdown import markdown

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core import texts

""" 
Test the HTML and Markdown Texsts if they are valid to avoid regressions... 
Texsts are currently mixed. So we test everything as HTML and Markdown. Markdown-Texsts using <commandParameter> as 
text parts will be blacklisted 
"""

# Blacklist of texts containing placeholders
BLACKLIST_PLACEHOLDERS = [
    "HIDE_WELCOME",
    "MSG_HELP_GLOBAL_ADMIN",
    "MSG_HELP_GROUP_ADMIN",
    "SNIPE_WELCOME",
]

def get_texts():
    for variable_name in dir(texts):
        if not variable_name.startswith("__"):
            the_text = getattr(texts, variable_name)
            yield (variable_name, the_text)

class TestRegex(unittest.TestCase):
    def test_html(self):
        failed_validations = ""
        for variable_name, text in get_texts():
            if variable_name in BLACKLIST_PLACEHOLDERS:
                continue
            parser = expat.ParserCreate()
            #print("Checking XML/HTML for: {}".format(variable_name))
            try:
                parser.Parse("<test>{}</test>".format(text))
            except expat.ExpatError as ex:
                failed_validations += "{} raised ExpatError. Not valid XML/HTML!\n".format(variable_name)

        if failed_validations:
            self.fail(failed_validations)

    def test_markdown(self):
        failed_validations = ""
        for variable_name, text in get_texts():
            # print("Checking XML/HTML for: {}".format(variable_name))
            #try:
            #    parser.Parse("<test>{}</test>".format(text))
            #except expat.ExpatError as ex:
            #    failed_validations += "{} raised ExpatError. Not valid XML/HTML!\n".format(variable_name)
            markdown(text)

        if failed_validations:
            self.fail(failed_validations)


if __name__ == '__main__':
    # Force TZ!
    import os
    os.environ['TZ'] = 'UTC'

    unittest.main()
