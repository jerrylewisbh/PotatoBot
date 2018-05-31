# -*- coding: utf-8 -*-
from datetime import time

from core.battle import (fresh_profiles, ready_to_battle,
                         ready_to_battle_result, refresh_api_users,
                         report_after_battle)
from core.texts import (MSG_MAIN_READY_TO_BATTLE_30,
                        MSG_MAIN_READY_TO_BATTLE_45, MSG_MAIN_SEND_REPORTS)
from telegram.ext import Updater


def add_war_warning_messages(updater: Updater):
    # 45 Min reminders
    updater.job_queue.run_daily(ready_to_battle, time(hour=6, minute=45), context=MSG_MAIN_READY_TO_BATTLE_45)
    updater.job_queue.run_daily(ready_to_battle, time(hour=14, minute=45), context=MSG_MAIN_READY_TO_BATTLE_45)
    updater.job_queue.run_daily(ready_to_battle, time(hour=22, minute=45), context=MSG_MAIN_READY_TO_BATTLE_45)

    # 30 Min reminders
    updater.job_queue.run_daily(ready_to_battle, time(hour=6, minute=30), context=MSG_MAIN_READY_TO_BATTLE_30)
    updater.job_queue.run_daily(ready_to_battle, time(hour=14, minute=30), context=MSG_MAIN_READY_TO_BATTLE_30)
    updater.job_queue.run_daily(ready_to_battle, time(hour=22, minute=30), context=MSG_MAIN_READY_TO_BATTLE_30)

    # Send Reports
    updater.job_queue.run_daily(ready_to_battle, time(hour=7, minute=3), context=MSG_MAIN_SEND_REPORTS)
    updater.job_queue.run_daily(ready_to_battle, time(hour=15, minute=3), context=MSG_MAIN_SEND_REPORTS)
    updater.job_queue.run_daily(ready_to_battle, time(hour=23, minute=3), context=MSG_MAIN_SEND_REPORTS)

    # Battle results for government chat...
    updater.job_queue.run_daily(ready_to_battle_result, time(hour=8, minute=0))
    updater.job_queue.run_daily(ready_to_battle_result, time(hour=16, minute=0))
    updater.job_queue.run_daily(ready_to_battle_result, time(hour=0, minute=0))

    # Profiles...
    updater.job_queue.run_daily(fresh_profiles, time(hour=6, minute=40))
    updater.job_queue.run_daily(fresh_profiles, time(hour=14, minute=40))
    updater.job_queue.run_daily(fresh_profiles, time(hour=22, minute=40))


def add_pre_war_messages(updater: Updater):
    updater.job_queue.run_daily(callback=refresh_api_users, time=time(hour=6, minute=57))
    updater.job_queue.run_daily(callback=refresh_api_users, time=time(hour=14, minute=57))
    updater.job_queue.run_daily(callback=refresh_api_users, time=time(hour=22, minute=57))


def add_after_war_messages(updater: Updater):
    updater.job_queue.run_daily(callback=refresh_api_users, time=time(hour=7, minute=3))
    updater.job_queue.run_daily(callback=refresh_api_users, time=time(hour=15, minute=3))
    updater.job_queue.run_daily(callback=refresh_api_users, time=time(hour=23, minute=3))


def add_battle_report_messages(updater: Updater):
    updater.job_queue.run_daily(callback=report_after_battle, time=time(hour=7, minute=5))
    updater.job_queue.run_daily(callback=report_after_battle, time=time(hour=15, minute=5))
    updater.job_queue.run_daily(callback=report_after_battle, time=time(hour=23, minute=5))
