import logging
import os
import numpy

from datetime import datetime, time, timedelta
from math import pi

import matplotlib.pyplot as plot
import pandas as pd
from sqlalchemy import func, tuple_
from telegram import Bot, Update

from core.decorators import user_allowed
from core.functions.reply_markup import generate_statistics_markup
from core.texts import (MSG_DATE_FORMAT, MSG_DAY_PLURAL1, MSG_DAY_PLURAL2,
                        MSG_DAY_SINGLE, MSG_NO_CLASS, MSG_PLOT_DESCRIPTION,
                        MSG_PLOT_DESCRIPTION_SKILL, MSG_STATISTICS_ABOUT,
                        PLOT_X_LABEL, PLOT_Y_LABEL)

from core.types import Character, Profession, UserQuest, Location, Session
from core.utils import send_async

Session()

@user_allowed
def statistic_about(bot: Bot, update: Update):
    markup = generate_statistics_markup()
    send_async(bot,
               chat_id=update.message.chat.id,
               text=MSG_STATISTICS_ABOUT,
               reply_markup=markup)

@user_allowed
def quest_statistic(bot: Bot, update: Update, session):
    logging.debug("Quest statistics")

    # Render for every level we know...
    max_level = session.query(func.max(UserQuest.level)).first()
    if not max_level:
        return


    fig, ax = plot.subplots(figsize=(20, 15))
    ind = numpy.arange(max_level[0] + 1)
    width = 0.25

    bars = []
    logging.warning("Getting stats for")
    stats = session.query(
        UserQuest.level, func.avg(UserQuest.exp), func.stddev(UserQuest.exp)
    ).join(Location).filter(UserQuest.location_id == 13).order_by(UserQuest.level).group_by(UserQuest.level).all()

    values = []
    stddev = []
    for stat in stats:
        while len(values) < stat[0]:
            #logging.warning("Filling up list...")
            values.append(float('nan'))
            stddev.append(float('nan'))
        values.append(int(stat[1]))
        stddev.append(int(stat[2]))
    while len(values) <= max_level[0]:
        values.append(float('nan'))
        stddev.append(float('nan'))

    values = numpy.array(values).astype(numpy.double)
    mask = numpy.isfinite(tuple(values))

    logging.warning(values)
    logging.warning(len(values))
    logging.warning(stddev)
    logging.warning(len(stddev))

    b = ax.plot(
        ind[mask],
        values[mask],
        width,
        color='gold',
        linestyle='-', marker='o'
        #yerr=tuple(stddev)
    )
    bars.append(b)

    # add some text for labels, title and axes ticks
    ax.set_ylabel('XP')
    ax.set_title('Experience in Forest')
    ax.set_xticks(ind + (width * 4) / 2)
    ax.set_xticklabels(range(1, max_level[0]+1))


    #[autolabel(ax, bar) for bar in bars]

    filename = str(datetime.now()).replace(':', '').replace(' ', '').replace('-', '') + '.png'
    with open(filename, 'wb') as file:
        plot.savefig(file, format='png')

    with open(filename, 'rb') as file:
        bot.sendPhoto(update.message.chat.id, file, "Forest!")

    plot.clf()
    os.remove(filename)


@user_allowed
def quest_statistic_line_one(bot: Bot, update: Update, session):
    logging.debug("Quest statistics")

    # Render for every level we know...
    max_level = session.query(func.max(UserQuest.level)).first()
    if not max_level:
        return

    times = (
        (2, 'Morning', 'gold'),
        (4, 'Day', 'goldenrod'),
        (8, 'Evening', 'orange'),
        (16, 'Night', 'silver'),
    )

    fig, ax = plot.subplots(figsize=(20, 15))
    ind = numpy.arange(max_level[0] + 1)
    width = 0.25

    bars = []
    for counter, daytime in enumerate(times, start=1):
        logging.warning("Getting stats for %s", daytime)
        stats = session.query(
            UserQuest.level, func.avg(UserQuest.exp), func.stddev(UserQuest.exp)
        ).join(Location).filter(UserQuest.location_id == 13, UserQuest.daytime == daytime[0]).order_by(UserQuest.level).group_by(UserQuest.level).all()

        values = []
        stddev = []
        for stat in stats:
            while len(values) < stat[0]:
                #logging.warning("Filling up list...")
                values.append(float('nan'))
                stddev.append(float('nan'))
            values.append(int(stat[1]))
            stddev.append(int(stat[2]))
        while len(values) <= max_level[0]:
            values.append(float('nan'))
            stddev.append(float('nan'))

        values = numpy.array(values).astype(numpy.double)
        mask = numpy.isfinite(tuple(values))

        logging.warning(values)
        logging.warning(len(values))
        logging.warning(stddev)
        logging.warning(len(stddev))

        b = ax.plot(
            ind[mask],
            values[mask],
            width,
            color=daytime[2],
            linestyle='-', marker='o'
            #yerr=tuple(stddev)
        )
        bars.append(b)

    # add some text for labels, title and axes ticks
    ax.set_ylabel('XP')
    ax.set_title('Experience in Forest')
    ax.set_xticks(ind + (width * 4) / 2)
    ax.set_xticklabels(range(1, max_level[0]+1))

    ax.legend(
        [rect for rect in bars],
        [daytime[1] for daytime in times],
    )
    #[autolabel(ax, bar) for bar in bars]

    filename = str(datetime.now()).replace(':', '').replace(' ', '').replace('-', '') + '.png'
    with open(filename, 'wb') as file:
        plot.savefig(file, format='png')

    with open(filename, 'rb') as file:
        bot.sendPhoto(update.message.chat.id, file, "Forest!")

    plot.clf()
    os.remove(filename)


@user_allowed
def quest_statistic_split(bot: Bot, update: Update, session):
    logging.debug("Quest statistics")

    # Render for every level we know...
    max_level = session.query(func.max(UserQuest.level)).first()
    if not max_level:
        return

    times = (
        (2, 'Morning', 'gold'),
        (4, 'Day', 'goldenrod'),
        (8, 'Evening', 'orange'),
        (16, 'Night', 'silver'),
    )

    fig, ax = plot.subplots(figsize=(20, 15))
    ind = numpy.arange(max_level[0] + 1)
    width = 0.25

    bars = []
    for counter, daytime in enumerate(times, start=1):
        logging.warning("Getting stats for %s", daytime)
        stats = session.query(
            UserQuest.level, func.avg(UserQuest.exp), func.stddev(UserQuest.exp)
        ).join(Location).filter(UserQuest.location_id == 13, UserQuest.daytime == daytime[0]).order_by(UserQuest.level).group_by(UserQuest.level).all()

        values = []
        stddev = []
        for stat in stats:
            while len(values) < stat[0]:
                #logging.warning("Filling up list...")
                values.append(0)
                stddev.append(0)
            values.append(int(stat[1]))
            stddev.append(int(stat[2]))
        while len(values) <= max_level[0]:
            values.append(0)
            stddev.append(0)

        logging.warning(values)
        logging.warning(len(values))
        logging.warning(stddev)
        logging.warning(len(stddev))

        b = ax.bar(
            ind + (width*counter),
            tuple(values),
            width,
            color=daytime[2],
            yerr=tuple(stddev)
        )
        bars.append(b)

    # add some text for labels, title and axes ticks
    ax.set_ylabel('XP')
    ax.set_title('Experience in Forest')
    ax.set_xticks(ind + (width * 4) / 2)
    ax.set_xticklabels(range(1, max_level[0]+1))

    ax.legend(
        [rect for rect in bars],
        [daytime[1] for daytime in times],
    )
    [autolabel(ax, bar) for bar in bars]

    filename = str(datetime.now()).replace(':', '').replace(' ', '').replace('-', '') + '.png'
    with open(filename, 'wb') as file:
        plot.savefig(file, format='png')

    with open(filename, 'rb') as file:
        bot.sendPhoto(update.message.chat.id, file, "Forest!")

    plot.clf()
    os.remove(filename)

@user_allowed
def quest_statistic_one(bot: Bot, update: Update, session):
    logging.debug("Quest statistics")

    # Render for every level we know...
    max_level = session.query(func.max(UserQuest.level)).first()
    if not max_level:
        return

    fig, ax = plot.subplots(figsize=(20, 15))
    ind = numpy.arange(max_level[0] + 1)
    width = 0.5

    logging.warning("Getting stats")
    stats = session.query(
        UserQuest.level, func.avg(UserQuest.exp), func.stddev(UserQuest.exp)
    ).join(Location).filter(UserQuest.location_id == 13).order_by(UserQuest.level).group_by(UserQuest.level).all()

    values = []
    stddev = []
    for stat in stats:
        while len(values) < stat[0]:
            #logging.warning("Filling up list...")
            values.append(0)
            stddev.append(0)
        values.append(int(stat[1]))
        stddev.append(int(stat[2]))
    while len(values) <= max_level[0]:
        values.append(0)
        stddev.append(0)

    logging.warning(values)
    logging.warning(len(values))
    logging.warning(stddev)
    logging.warning(len(stddev))

    b = ax.bar(
        ind + (width),
        tuple(values),
        width,
        color='gold',
        yerr=tuple(stddev)
    )

    # add some text for labels, title and axes ticks
    ax.set_ylabel('XP')
    ax.set_title('Experience in Forest')
    ax.set_xticks(ind + (width * 4) / 2)
    ax.set_xticklabels(range(1, max_level[0]+1))

    """ax.legend(
        [rect for rect in bars],
        [daytime[1] for daytime in times],
    )
    [autolabel(ax, bar) for bar in bars]"""

    filename = str(datetime.now()).replace(':', '').replace(' ', '').replace('-', '') + '.png'
    with open(filename, 'wb') as file:
        plot.savefig(file, format='png')

    with open(filename, 'rb') as file:
        bot.sendPhoto(update.message.chat.id, file, "Forest!")

    plot.clf()
    os.remove(filename)

def autolabel(ax, rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        if int(height) > 0:
            ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom')


@user_allowed
def skill_statistic(bot: Bot, update: Update):
    my_class = Session.query(Profession).filter_by(
        user_id=update.message.from_user.id).order_by(
        Profession.date.desc()).first()
    if not my_class:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_NO_CLASS)
        return

    recent_classes = Session.query(Profession.user_id, func.max(Profession.date)). \
        group_by(Profession.user_id)

    classes = Session.query(Profession).filter(tuple_(Profession.user_id, Profession.date)
                                               .in_([(a[0], a[1]) for a in recent_classes]))\

    recent_classes = recent_classes.all()

    classes = classes.all()

    my_skills = dict()
    max_value = -1

    strings = my_class.skillList.splitlines()
    for string in strings:
        skill_name = string.split(": ")[1]
        skill_value = int(string.split(": ")[0])
        my_skills[skill_name] = [skill_value, 0, 0, 0, 0]

    for class_data in classes:
        strings = class_data.skillList.splitlines()
        for string in strings:
            skill_name = string.split(": ")[1]
            skill_value = int(string.split(": ")[0])
            if skill_name not in my_skills:
                continue
            my_skills[skill_name][1] += skill_value
            max_value = max(max_value, skill_value)
            my_skills[skill_name][2] += 1

            if class_data.name == my_class.name:
                my_skills[skill_name][3] += skill_value
                my_skills[skill_name][4] += 1

    for skill in my_skills:
        my_skills[skill][1] /= my_skills[skill][2]
        my_skills[skill][3] /= my_skills[skill][4]
        del my_skills[skill][2]
        del my_skills[skill][3]

    # Set data
    df = pd.DataFrame(my_skills)
    categories = list(df)
    N = len(categories)
    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    #angles += angles[:1]

    # Initialise the spider plot
    ax = plot.subplot(111, polar=True)

    # If you want the first axis to be on top:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # Draw one axe per variable + add labels labels yet
    plot.xticks(angles, categories)

    # Draw ylabels
    ax.set_rlabel_position(0)
    plot.yticks(range(1, max_value), [str(i) for i in range(1, max_value)], color="grey", size=7)
    plot.ylim(0, max_value + 1)

    # ------- PART 2: Add plots

    # Plot each individual = each line of the data
    # I don't do a loop, because plotting more than 3 groups makes the chart unreadable

    # Ind1
    values = df.loc[0].values.flatten().tolist()

    ax.plot(angles, values, linewidth=1, linestyle='solid', label="You")
    ax.fill(angles, values, 'b', alpha=0.1)

    # Ind2
    values = df.loc[1].values.flatten().tolist()
    ax.plot(angles, values, linewidth=1, linestyle='solid', label="Castle")
    ax.fill(angles, values, 'r', alpha=0.1)

    # Ind2
    values = df.loc[2].values.flatten().tolist()
    ax.plot(angles, values, linewidth=1, linestyle='solid', label="Class")
    ax.fill(angles, values, 'g', alpha=0.1)

    # Add legend
    plot.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    filename = str(datetime.now()).replace(':', '').replace(' ', '').replace('-', '') + '.png'
    with open(filename, 'wb') as file:
        plot.savefig(file, format='png')

    with open(filename, 'rb') as file:
        bot.sendPhoto(update.message.chat.id, file, MSG_PLOT_DESCRIPTION_SKILL)
    plot.clf()
    os.remove(filename)


@user_allowed
def exp_statistic(bot: Bot, update: Update):
    profiles = Session.query(Character).filter_by(user_id=update.message.from_user.id)\
        .order_by(Character.date).all()
    plot.switch_backend('ps')
    plot.xlabel(PLOT_X_LABEL)
    plot.ylabel(PLOT_Y_LABEL)
    x = [profile.date for profile in profiles]
    y = [profile.exp for profile in profiles]
    need_exp = profiles[-1].needExp
    x.append(datetime.now())
    y.append(y[-1])
    plot.plot(x, y)
    plot.gcf().autofmt_xdate()
    filename = str(datetime.now()).replace(':', '').replace(' ', '').replace('-', '') + '.png'
    with open(filename, 'wb') as file:
        plot.savefig(file, format='png')

    now_date = x[-2]
    prev_date = x[0]
    now_exp = y[-2]
    prev_exp = y[0]
    for date, exp in zip(x[-3::-1], y[-3::-1]):
        if date <= now_date - timedelta(days=3):
            prev_date = date
            prev_exp = exp
            break

    delta = now_date - prev_date
    interval = (delta.days * 86400 + delta.seconds) or 1
    day_exp = (now_exp - prev_exp) * 86400 / interval
    delta_exp = need_exp - now_exp

    text = ''
    if day_exp:
        delta_days = round(delta_exp / day_exp) or 1
        days_text = MSG_DAY_SINGLE
        if delta_days == 1:
            days_text = MSG_DAY_SINGLE
        elif (delta_days % 10 == 0) or (delta_days % 10 >= 5) or ((delta_days % 100) in (11, 12, 13, 14)):
            days_text = MSG_DAY_PLURAL2
        elif (delta_days % 10) in (2, 3, 4):
            days_text = MSG_DAY_PLURAL1

        text = (MSG_DATE_FORMAT.format(delta_days, days_text))

    with open(filename, 'rb') as file:
        bot.sendPhoto(update.message.chat.id, file, MSG_PLOT_DESCRIPTION
                      .format(int(day_exp), delta_exp, text))
    plot.clf()
    os.remove(filename)
