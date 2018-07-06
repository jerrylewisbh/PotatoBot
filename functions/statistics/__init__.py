import io
import pandas
from datetime import timedelta

import numpy
import matplotlib.pyplot as plot
from sqlalchemy import func, tuple_
from telegram import Update, ParseMode

from config import QUEST_LOCATION_ARENA_ID, QUEST_LOCATION_FORAY_ID, QUEST_LOCATION_DEFEND_ID
from core.bot import MQBot
from core.decorators import command_handler
from core.state import GameState
from core.texts import *
from core.types import *
from core.utils import send_async
from functions.reply_markup import generate_statistics_markup

Session()

plot.ioff()


@command_handler()
def statistic_about(bot: MQBot, update: Update, user: User):
    markup = generate_statistics_markup()
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=MSG_STATISTICS_ABOUT,
        reply_markup=markup
    )


def get_relative_details_for_location(user: User, from_date: datetime, location: Location):
    text = ""
    base_stats = Session.query(
        func.count(UserQuest.id).label('count'),
        func.sum(UserQuest.exp).label("exp_sum"),
        func.avg(UserQuest.exp).label("exp_avg"),
        func.sum(UserQuest.gold).label("gold_sum"),
        func.avg(UserQuest.gold).label("gold_avg")
    ).filter(
        UserQuest.user_id == user.id,
        UserQuest.location_id == location.id,
        UserQuest.from_date > from_date
    ).first()

    item_stats = Session.query(
        func.sum(UserQuestItem.count).label('item_sum'),
        func.avg(UserQuestItem.count).label('item_avg')
    ).join(UserQuest).filter(
        UserQuest.user_id == user.id,
        UserQuest.location == location,
        UserQuest.from_date > from_date
    ).first()

    if location.id != QUEST_LOCATION_ARENA_ID:
        text += MSG_QUEST_STAT_LOCATION.format(
            location.name,
            base_stats.count if base_stats.count else 0,
            base_stats.exp_avg if base_stats.exp_avg else 0,
            base_stats.gold_avg if base_stats.gold_avg else 0,
            item_stats.item_avg if item_stats.item_avg else 0,
            base_stats.exp_sum if base_stats.exp_sum else 0,
            base_stats.gold_sum if base_stats.gold_sum else 0,
            item_stats.item_sum if item_stats.item_sum else 0,
        )
    else:
        text += MSG_QUEST_STAT_NO_LOOT.format(
            location.name,
            base_stats.count if base_stats.count else 0,
            base_stats.exp_avg if base_stats.exp_avg else 0,
            base_stats.gold_avg if base_stats.gold_avg else 0,
            base_stats.exp_sum if base_stats.exp_sum else 0,
            base_stats.gold_sum if base_stats.gold_sum else 0,
        )

    # Additional stats for foray...
    if location.id == QUEST_LOCATION_FORAY_ID:
        text += __get_additional_stats_foray(from_date, location, text, user)
    elif location.id in [QUEST_LOCATION_DEFEND_ID, QUEST_LOCATION_ARENA_ID]:
        text += __get_additional_stats_basic(from_date, location, user)

    return text


def get_relative_details(user: User, from_date: datetime):
    locations = Session.query(Location).all()
    text = ""
    for location in locations:
        text += get_relative_details_for_location(user, from_date, location)

    return text


def __get_additional_stats_foray(from_date, location, text, user):
    foray_stats_success = Session.query(
        UserQuest.successful,
        func.count(UserQuest.id).label("count"),
        func.sum(UserQuest.pledge).label("pledges")
    ).filter(
        UserQuest.successful.is_(True),
        UserQuest.user_id == user.id,
        UserQuest.location_id == location.id,
        UserQuest.from_date > from_date
    ).first()
    foray_stats_failed = Session.query(
        UserQuest.successful,
        func.count(UserQuest.id).label("count"),
    ).filter(
        UserQuest.successful.is_(False),
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


def __get_additional_stats_basic(from_date, location, user):
    stop_stats_success = Session.query(
        UserQuest.successful,
        func.count(UserQuest.id).label("count"),
    ).filter(
        UserQuest.successful.is_(True),
        UserQuest.user_id == user.id,
        UserQuest.location_id == location.id,
        UserQuest.from_date > from_date
    ).first()
    stop_stats_failed = Session.query(
        UserQuest.successful,
        func.count(UserQuest.id).label("count"),
    ).filter(
        UserQuest.successful.is_(False),
        UserQuest.user_id == user.id,
        UserQuest.location_id == location.id,
        UserQuest.from_date > from_date
    ).first()
    stat_count_failed = 0
    if stop_stats_failed:
        stat_count_failed = stop_stats_failed.count
    stat_count = 0
    if stop_stats_success:
        stat_count = stop_stats_success.count
    overall_count = (stat_count_failed + stat_count)
    if not overall_count:
        success_rate = 100
    else:
        success_rate = stat_count / overall_count * 100

    return MSG_QUEST_BASIC_STAT.format(success_rate)


@command_handler()
def quest_statistic(bot: MQBot, update: Update, user: User):
    logging.info("User '%s' called quest_statistic", user.id)

    text = MSG_QUEST_7_DAYS
    text += get_relative_details(user, datetime.utcnow() - timedelta(days=7))
    text += MSG_QUEST_OVERALL
    text += get_relative_details(user, datetime.utcnow() - timedelta(weeks=300))

    bot.sendMessage(
        chat_id=user.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=generate_statistics_markup(),
    )


def __get_item_statistics_by_location(location: Location):
    text = "*{}:*".format(location.name)

    # Overall statistics
    overall_count = Session.query(func.count(UserQuest.id)).filter(
        UserQuest.location_id == location.id
    ).scalar()

    item_loot_overall = Session.query(
        func.sum(UserQuestItem.count).label("sum"),
        func.count(UserQuestItem.count).label("count")
    ).filter(
        UserQuest.location_id == location.id
    ).join(UserQuest).first()

    text += """
Overall chance for loot: {:.2f}%
Average loot: {:.2f}
    """.format(
        item_loot_overall.count / overall_count * 100,
        (item_loot_overall.sum / item_loot_overall.count) if item_loot_overall.count else 0,
    )

    # Item Statistics
    item_drops = Session.query(
        Item
    ).filter(
        UserQuestItem.user_quest_id.in_(
            Session.query(UserQuest.id).filter(UserQuest.location_id == location.id)
        )
    ).join(UserQuestItem).join(UserQuest).distinct().order_by(Item.id).all()

    daytimes = (
        GameState.MORNING,
        GameState.DAY,
        GameState.EVENING,
        GameState.NIGHT
    )

    for item in item_drops:
        text += "{}:\n".format(item.name)
        stats = Session.query(
            UserQuest.daytime.label("daytime"),
            func.sum(UserQuestItem.count).label("sum"),
        ).filter(
            UserQuest.location_id == location.id,
            UserQuestItem.item_id == item.id
        ).join(UserQuestItem).group_by(UserQuest.daytime).all()

        for daytime in daytimes:
            text += "{}:\n".format(daytime.name)

    return text


@command_handler()
def item_statistic(bot: MQBot, update: Update, user: User):
    logging.info("User '%s' called item_statistic", user.id)

    text = MSG_ITEM_STAT

    for location in Session.query(Location).all():
        text += __get_item_statistics_by_location(location)

    bot.sendMessage(
        chat_id=user.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=generate_statistics_markup(),
    )


@command_handler()
def skill_statistic(bot: MQBot, update: Update, user: User):
    my_class = Session.query(Profession).filter_by(
        user_id=update.message.from_user.id).order_by(
        Profession.date.desc()).first()
    if not my_class:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_NO_CLASS)
        return

    recent_classes = Session.query(Profession.user_id, func.max(Profession.date)). \
        group_by(Profession.user_id)

    classes = Session.query(Profession).filter(
        tuple_(Profession.user_id, Profession.date).in_([(a[0], a[1]) for a in recent_classes])
    )
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
    df = pandas.DataFrame(my_skills)
    categories = list(df)
    N = len(categories)
    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * numpy.pi for n in range(N)]
    # angles += angles[:1]

    # Initialise the spider plot
    ax = plot.subplot(111, polar=True)

    # If you want the first axis to be on top:
    ax.set_theta_offset(numpy.pi / 2)
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

    with io.BytesIO() as f:
        plot.savefig(f, format='png')
        f.seek(0)
        bot.send_photo(
            chat_id=update.message.chat.id,
            photo=f,
            caption=MSG_PLOT_DESCRIPTION_SKILL
        )

    plot.clf()


@command_handler()
def exp_statistic(bot: MQBot, update: Update, user: User):
    profiles = Session.query(Character).filter_by(user_id=update.message.from_user.id) \
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

    with io.BytesIO() as f:
        plot.savefig(f, format='png')
        f.seek(0)
        bot.send_photo(
            chat_id=update.message.chat.id,
            photo=f,
            caption=MSG_PLOT_DESCRIPTION.format(int(day_exp), delta_exp, text)
        )

    plot.clf()
