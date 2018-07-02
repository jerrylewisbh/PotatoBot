import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions.common import disable_api_functions
from core.types import Ban, Session

Session()

banned_users = Session.query(Ban).filter(Ban.to_date > datetime.now()).all()
for banned_user in banned_users:
    print("Reban for: {}".format(banned_user.user.id))

    # Disable API settings but keep his api credentials until user revokes them herself/himself.
    disable_api_functions(banned_user.user)
