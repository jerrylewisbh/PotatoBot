import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.types import Ban, Session, UserExchangeOrder, UserStockHideSetting

Session()

banned_users = Session.query(Ban).filter(Ban.to_date > datetime.now()).all()
for banned_user in banned_users:
    print("Reban for: {}".format(banned_user.user.id))

    # Disable API settings but keep his api credentials until user revokes them herself/himself.
    banned_user.user.setting_automated_sniping = False
    banned_user.user.setting_automated_hiding = False
    banned_user.user.setting_automated_report = False
    banned_user.user.setting_automated_deal_report = False

    # Remove all his settings...
    Session.query(UserExchangeOrder).filter(UserExchangeOrder.user_id == banned_user.user.id).delete()
    Session.query(UserStockHideSetting).filter(UserStockHideSetting.user_id == banned_user.user.id).delete()

    Session.add(banned_user.user)
    Session.commit()
