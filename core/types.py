# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, UnicodeText, BigInteger
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlalchemy.pool import Pool
import logging
from enum import Enum


class AdminType(Enum):
    FULL = 1
    GROUP = 2


engine = create_engine('mysql+pymysql://mint_bot:VF;F8A{pWtW[X4sWC8du=N]u@fdev.me/mint_castle?charset=utf8mb4',
                       echo=False, pool_size=20, max_overflow=10)
logger = logging.getLogger('sqlalchemy.engine')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


@event.listens_for(Pool, "connect")
def set_unicode(dbapi_conn, conn_record):
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'")
    except Exception as e:
        logger.error(e)


class Group(Base):
    __tablename__ = 'groups'

    id = Column(BigInteger, primary_key=True)
    username = Column(UnicodeText(250))
    title = Column(UnicodeText(250))
    welcome_enabled = Column(Boolean, default=False)
    allow_trigger_all = Column(Boolean, default=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(UnicodeText(250))
    first_name = Column(UnicodeText(250))
    last_name = Column(UnicodeText(250))
    date_added = Column(DateTime, default=datetime.now())

    def __repr__(self):
        user = ''
        if self.first_name:
            user += self.first_name + ' '
        if self.last_name:
            user += self.last_name + ' '
        if self.username:
            user += '(@' + self.username + ')'


class WelcomeMsg(Base):
    __tablename__ = 'welcomes'

    chat_id = Column(BigInteger, primary_key=True)
    message = Column(UnicodeText(2500))


class Wellcomed(Base):
    __tablename__ = 'wellcomed'

    user_id = Column(BigInteger, ForeignKey(User.id), primary_key=True)
    chat_id = Column(BigInteger, ForeignKey(WelcomeMsg.chat_id), primary_key=True)


class Trigger(Base):
    __tablename__ = 'triggers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    trigger = Column(UnicodeText(2500))
    message = Column(UnicodeText(2500))


class Admin(Base):
    __tablename__ = 'admins'

    user_id = Column(BigInteger, ForeignKey(User.id), primary_key=True)
    admin_type = Column(Integer)
    admin_group = Column(BigInteger, primary_key=True, default=0)


def admin(adm_type=AdminType.FULL):
    def decorate(func):
        def wrapper(bot, update, *args, **kwargs):
            adms = session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
            allowed = False
            for adm in adms:
                if adm is not None and adm.admin_type <= adm_type.value and \
                                adm.admin_group in [0, update.message.chat.id]:
                    allowed = True
                    break
            if allowed:
                func(bot, update, *args, **kwargs)
        return wrapper
    return decorate


Base.metadata.create_all(engine)
