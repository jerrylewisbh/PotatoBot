from telegram import Update, Bot

from core.functions.reply_markup import generate_statistics_markup
from core.texts import MSG_STATISTICS_ABOUT
from core.types import user_allowed, Character
from core.utils import send_async

import matplotlib.pyplot as plot

from datetime import datetime, time, timedelta

import os


@user_allowed
def statistic_about(bot: Bot, update: Update, session):
    markup = generate_statistics_markup()
    send_async(bot,
               chat_id=update.message.chat.id,
               text=MSG_STATISTICS_ABOUT,
               reply_markup=markup)


@user_allowed
def exp_statistic(bot: Bot, update: Update, session):
    profiles = session.query(Character).filter_by(user_id=update.message.from_user.id)\
        .order_by(Character.date).all()
    plot.switch_backend('ps')
    plot.xlabel('Дата')
    plot.ylabel('Опыт')
    x = [profile.date for profile in profiles]
    y = [profile.exp for profile in profiles]
    x.append(datetime.now())
    y.append(y[-1])
    plot.plot(x, y)
    plot.gcf().autofmt_xdate()
    filename = str(datetime.now()).replace(':', '').replace(' ', '').replace('-', '') + '.png'
    with open(filename, 'wb') as file:
        plot.savefig(file, format='png')

    now_date = x[-1]
    prev_date = x[0]
    now_exp = y[-1]
    prev_exp = y[0]
    for date, exp in zip(reversed(x), reversed(y)):
        if date <= datetime.now() - timedelta(days=3):
            prev_date = date
            prev_exp = exp
            break
    delta = now_date - prev_date
    if not delta.days:
        day_exp = now_exp - prev_exp
    else:
        interval = delta.days * 86400 + delta.seconds
        day_exp = (now_exp - prev_exp) * 86400 / interval

    with open(filename, 'rb') as file:
        bot.sendPhoto(update.message.chat.id, file, 'В среднем {} опыта в день'
                      .format(int(day_exp)))
    plot.clf()
    os.remove(filename)
