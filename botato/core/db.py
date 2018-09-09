import logging
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from telegram import Update

from config import DB
from core.enums import AdminType
from core.model import User, Ban, Item, Log, Base

ENGINE = create_engine(DB,
                       echo=False,
                       pool_size=200,
                       max_overflow=50,
                       isolation_level="READ UNCOMMITTED")

Base.metadata.create_all(ENGINE)

Session = scoped_session(sessionmaker(bind=ENGINE))
Session()


def check_permission(user: User, update: Update, min_permission: AdminType):
    """ Check for a users permission... """

    if min_permission == AdminType.NOT_ADMIN:
        return True

    for permission_set in user.permissions:
        # Super admins...
        if permission_set.admin_type in [AdminType.SUPER, AdminType.FULL]:
            return True
        # Group admins: Allow if message is for their group OR if it is in private chat with bot...
        elif permission_set.admin_type <= AdminType.GROUP and (
                permission_set.group_id == update.effective_message.chat.id or
                    update.effective_message.chat.id == update.effective_user.id):
            return True
        else:
            logging.debug("[Permissions] update.effective_message.chat.id: %s", update.effective_message.chat.id)
            logging.debug("[Permissions] update.effective_user.id: %s", update.effective_user.id)
            logging.debug("[Permissions] permission_set.group_id: %s", permission_set.group_id)
            logging.debug("[Permissions] min_permission: %s", min_permission)

    return False


def check_admin(update, adm_type, allowed_types=()):
    allowed = False
    if adm_type == AdminType.NOT_ADMIN:
        allowed = True


def check_ban(update):
    ban = Session().query(Ban).filter_by(user_id=update.message.from_user.id
                                         if update.message else update.callback_query.from_user.id).first()
    if ban is None or ban.to_date < datetime.now():
        return True
    else:
        return False


def new_item(name: str, tradable: bool):
    if name:
        # Create items we do not yet know in the database....
        item = Item()
        item.name = name
        item.tradable = tradable
        Session.add(item)
        Session.commit()

        logging.warning("New item '%s' discovered! You might need to adjust trade/weight options!", name)

        return item
    return None


def log(user_id, chat_id, func_name, args):
    if user_id:
        log_item = Log()
        log_item.date = datetime.now()
        log_item.user_id = user_id
        log_item.chat_id = chat_id
        log_item.func_name = func_name
        log_item.args = args
        s = Session()
        s.add(log_item)
        s.commit()
        # Session.remove()
