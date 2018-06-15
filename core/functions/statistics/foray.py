import logging
import numpy
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plot

from sqlalchemy import func, tuple_, extract, distinct
from sqlalchemy.sql.functions import count
from telegram import Bot, ParseMode, Update

from config import QUEST_LOCATION_FORAY_ID, QUEST_LOCATION_DEFEND_ID, QUEST_LOCATION_ARENA_ID
from core.decorators import command_handler, user_allowed
from core.functions.reply_markup import generate_statistics_markup
from core.functions.statistics import get_relative_details_for_location
from core.texts import *
from core.types import (Character, Location, Profession, Session, User,
                        UserQuest, UserQuestItem)

plot.ioff()
Session()

def __get_additional_stats_foray(from_date, location, text, user):
    foray_stats_success = Session.query(
        UserQuest.successful,
        func.count(UserQuest.id).label("count"),
        func.sum(UserQuest.pledge).label("pledges")
    ).filter(
        UserQuest.successful == True,
        UserQuest.user_id == user.id,
        UserQuest.location_id == location.id,
        UserQuest.from_date > from_date
    ).first()
    foray_stats_failed = Session.query(
        UserQuest.successful,
        func.count(UserQuest.id).label("count"),
    ).filter(
        UserQuest.successful == False,
        UserQuest.user_id == user.id,
        UserQuest.location_id == location.id,
        UserQuest.from_date > from_date
    ).first()

    stat_count_failed = 0
    if foray_stats_failed:
        stat_count_failed = foray_stats_failed.count
    stat_count = 0
    stat_pledges = 0
    if foray_stats_success:
        stat_count = foray_stats_success.count
        stat_pledges = foray_stats_success.pledges
    overall_count = (stat_count_failed + stat_count)
    if not overall_count:
        success_rate = 100
    else:
        success_rate = stat_count / overall_count * 100
    if not stat_count:
        pledge_rate = 0
    else:
        pledge_rate = stat_pledges / stat_count * 100

    return MSG_QUEST_STAT_FORAY.format(success_rate, pledge_rate)


def __get_knight_pledgerate():
    stats_success = Session.query(
        extract('hour', UserQuest.forward_date).label('hour'),
        count(UserQuest.pledge).label("pledge_flag_counter")
    ).join(Location).filter(
        UserQuest.location_id == QUEST_LOCATION_FORAY_ID,
        UserQuest.pledge == True,
        UserQuest.user_id.in_(
            Session.query(User.id).join(Character).filter(Character.characterClass == "Knight").distinct()
        )
    ).group_by(
        'hour'
    ).order_by(UserQuest.successful).all()

    stats_fail = Session.query(
        extract('hour', UserQuest.forward_date).label('hour'),
        count(UserQuest.pledge).label("pledge_flag_counter")
    ).join(Location).filter(
        UserQuest.location_id == QUEST_LOCATION_FORAY_ID,
        UserQuest.pledge == False,
        UserQuest.user_id.in_(
            Session.query(User.id).join(Character).filter(Character.characterClass == "Knight").distinct()
        )
    ).group_by(
        'hour'
    ).order_by(UserQuest.successful).all()

    overall = {}
    for x in range(0, 24):
        overall[x] = {
            'all': 0,
            'pledges': 0,
        }
    for hourly_data in stats_fail:
        overall[hourly_data.hour]['all'] += hourly_data.pledge_flag_counter
    for hourly_data in stats_success:
        overall[hourly_data.hour]['all'] += hourly_data.pledge_flag_counter
        overall[hourly_data.hour]['pledges'] += hourly_data.pledge_flag_counter


    y = []
    x = []
    for hour, values in overall.items():
        x.append(hour)
        y.append(100 / values['all'] * values['pledges'] if values['pledges'] else 0)

    return x, y



def send_graph(bot: Bot, user: User):
    logging.debug("Quest statistics.py")

    fig, ax = plot.subplots(figsize=(20, 15))
    ind = numpy.arange(0 + 1)
    width = 0.25

    x, y, labels = __get_overall_successrate()
    ax.set_xlabel("Hour of the day in UTC timezone")
    plot.plot(x, y, color='firebrick')
    ax.set_ylabel('Foray success rate', color='firebrick')
    ax.tick_params('y', colors='firebrick')
    ax.set_title('Foray success by hour and pledge-rate')
    ax.set_xticks([x for x in range(0, 24)])

    for i, txt in enumerate(labels):
        ax.annotate(txt, (x[i], y[i]))

    ax.grid(True)

    ax2 = ax.twinx()
    pledge_x, pledge_y = __get_knight_pledgerate()
    ax2.bar(pledge_x, pledge_y, 1, alpha=0.3, color='slategrey')
    ax2.set_ylabel("Pledge rate", color='slategrey')
    ax2.tick_params('y', colors='slategrey')


    # add some text for labels, title and axes ticks


    filename = str(datetime.now()).replace(':', '').replace(' ', '').replace('-', '') + '.png'
    with open(filename, 'wb') as file:
        plot.savefig(file, format='png')

    with open(filename, 'rb') as file:
        bot.sendPhoto(
            user.id,
            file,
            MSG_FORAY_INTRO,
            parse_mode=ParseMode.MARKDOWN,
        )

    plot.clf()
    os.remove(filename)


def __get_overall_successrate():
    stats = Session.query(
        extract('hour', UserQuest.forward_date).label('hour'),
        UserQuest.successful.label("success"),
        count(UserQuest.successful).label("success_flag_counter")
    ).join(Location).filter(
        UserQuest.location_id == QUEST_LOCATION_FORAY_ID
    ).group_by(
        'hour',
        UserQuest.successful
    ).order_by(UserQuest.successful).all()
    overall = {}
    for x in range(0, 24):
        overall[x] = {
            'all': 0,
            'successful': 0,
        }
    for hourly_data in stats:
        overall[hourly_data.hour]['all'] += hourly_data.success_flag_counter
        if hourly_data.success:
            overall[hourly_data.hour]['successful'] += hourly_data.success_flag_counter

    y = []
    x = []
    labels = []
    for hour, values in overall.items():
        x.append(hour)
        y.append(100 / values['all'] * values['successful'] if values['successful'] else 0)
        labels.append(values['all'])
    return x, y, labels


@command_handler()
def foray_statistic(bot: Bot, update: Update, user: User):
    logging.info("User '%s' called quest_statistic", user.id)
    send_graph(bot, user)
