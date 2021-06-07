import datetime
import json

from rescueupdate import RESCUETIME_STATS_FOLDER


"""
Deadline hour is for when you want a 24-hour period that does not begin at midnight.
For example, if deadline_hour = 18
    If it's 9PM (21h), you will get data starting from 6PM today through 6PM the next day. (3 hours of data)
    If it's 5PM (17h), you will get data starting from 6PM yesterday to 6PM today. (23 hours of data)
"""

def dt_to_str(dt):
    return datetime.datetime.strftime(dt, "%Y%m%d")


def open_json_files(type="activities", deadline_hour=0):
    today = datetime.datetime.today()
    # If deadline hour is not midnight, we might need two files (today and yesterday)
    files_needed = [dt_to_str(today)]
    if today.hour < deadline_hour:
        files_needed.append(dt_to_str(today - datetime.timedelta(days=1)))
    base_folder = f"{RESCUETIME_STATS_FOLDER}{today.year}"
    files_needed = [f"{base_folder}/{file}_{type}.json" for file in files_needed]
    data = []
    for index, file in enumerate(files_needed):
        try:
            with open(file, 'r') as f:
                f = json.load(f)
                if (index == 0 and today.hour >= deadline_hour) or index == 1:
                    data += [x for x in f if x[1] >= deadline_hour]
                elif index == 0 and today.hour < deadline_hour:
                    data += [x for x in f if x[1] < deadline_hour]
        except FileNotFoundError:
            data = []
    return data


def get_activity(activity_name, deadline_hour=0):
    activities = open_json_files(deadline_hour=deadline_hour)
    try:
        return [x for x in activities if activity_name.lower() == x[4].lower()]
    except IndexError:
        return []


def get_productivity(productivity_scores, deadline_hour=0):
    if isinstance(productivity_scores, int):
        productivity_scores = [productivity_scores]
    productivity_file = open_json_files("productivity", deadline_hour=deadline_hour)
    try:
        return [x for x in productivity_file if x[4] in productivity_scores]
    except IndexError:
        return []


def get_activity_time(activity_name, deadline_hour=0):
    try:
        return sum([x[2] for x in get_activity(activity_name, deadline_hour)])
    except IndexError:
        return 0


def get_productivity_time(productivity_scores, deadline_hour=0):
    try:
        return sum([x[2] for x in get_productivity(productivity_scores, deadline_hour)])
    except IndexError:
        return 0


def get_total_time(deadline_hour=0):
    return get_productivity_time(productivity_scores=[-2, -1, 0, 1, 2], deadline_hour=deadline_hour)
