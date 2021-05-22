import datetime
import json
import os
import sys
import time
from enum import Enum

try:
    from rescuetime import Rescuetime, APIKEY
except ModuleNotFoundError:
    from .rescuetime import Rescuetime, APIKEY


DASHBOARD_STATS_FOLDER = os.path.dirname(os.path.abspath(__file__)) +  "/dashboard_stats/rescuetime/"
todays_date = datetime.datetime.today()


"""For handling dates"""


class With(Enum):
    """Whether to write a date with or without dash separators (e.g. 2020/01/01 vs 20200101"""
    NO_DASHES = 0
    DASHES = 1


def convert_date_to_str(with_dashes, date):
    if with_dashes == With.DASHES:
        return datetime.datetime.strftime(date, '%Y-%m-%d')
    elif with_dashes == With.NO_DASHES:
        return datetime.datetime.strftime(date, '%Y%m%d')


def date_range(start_date, end_date):
    days_between_dates = (end_date - start_date).days
    for days in range(days_between_dates+1):
        yield (start_date + datetime.timedelta(days=days))


def file_is_up_to_date(date, file):
    minimum_update_time = date + datetime.timedelta(days=1, hours=2)
    try:
        if datetime.datetime.fromtimestamp(
                os.path.getmtime(file)) > minimum_update_time:
            return True
        else:
            return False
    except FileNotFoundError:
        return False
    pass


class RescueDashboard():
    def __init__(self, api_key):
        super.__init__(api_key)
        self.origin = DASHBOARD_STATS_FOLDER
        self.rescuetime = Rescuetime()
        self.start_date = datetime.datetime(2016, 1, 1)

    def _get_record_from_date(self, date: datetime.datetime) -> str:
        date_str = convert_date_to_str(With.NO_DASHES, date)
        return f"{origin}{date.year}/{date_str}_"

    def activities_file_for_date(self, date):
        return self._get_record_from_date(date) + "activities.json"

    def productivity_file_for_date(self, date):
        return self._get_record_from_date(date) + "productivity.json"

    def activities_file_is_up_to_date(self, date):
        return file_is_up_to_date(file, self.activities_file_for_date(date))

    def productivity_file_is_up_to_date(self, date):
        return file_is_up_to_date(file, self.productivity_file_for_date(date))

    def get_activity_data(self, date):
        date = convert_date_to_str(With.DASHES, date)
        subcategories = self.rescuetime.get_hourly_subcategories(date)
        categories = self.rescuetime.get_hourly_categories(date)
        activities = self.rescuetime.get_hourly_activities(date)
        activity_data = subcategories + categories + activities
        return activity_data

    def get_productivity_data(self, date):
        date = convert_date_to_str(With.DASHES, date)
        productivity = self.rescuetime.get_hourly_productivity(date)
        get_hour_from_string = lambda datestring: datetime.datetime.strptime(
            datestring, '%Y-%m-%dT%H:%M:%S').hour
        for hourly_data in productivity:
            datestring_row = 0
            hourly_data[datestring_row] = get_hour_from_string(
                hourly_data[datestring_row])
            hourly_data.insert(0, date)  # Insert proper date format
        return productivity

    @staticmethod
    def dump_json_to_file(file, data):
        try:
            with open(file, 'w') as f:
                json.dumps(data)
        except:
            pass

    def update_activities_file(self, date):
        self.dump_json_to_file(file=self.activities_file_for_date(date),
                               data=self.get_activity_data(date))

    def update_productivity_file(self, date, data):
        self.dump_json_to_file(file=self.productivity_file_for_date(date),
                               data=self.get_productivity_data(date))

    def update_data(self):
        for date in date_range(self.start_date, todays_date):
            if not self.activities_file_is_up_to_date(date):
                self.update_activities_file(date)
            if not self.productivity_file_is_up_to_date(date):
                self.update_productivity_file(date)


def update(rescue_key=APIKEY,
           rescuetime_folder=DASHBOARD_STATS_FOLDER,
           show_messages=False):
    rescuetime = Rescuetime(rescue_key)

    if show_messages: print('called!')
    start_date = datetime.datetime(2016, 1, 1)
    today = datetime.datetime.today()
    while start_date <= today:
        skip_activities = False
        skip_productivity = False
        start_date_str = datetime.datetime.strftime(start_date, '%Y%m%d')
        if show_messages: print(start_date_str)
        file = rescuetime_folder + '{}/{}_'.format(start_date.year,
                                                   start_date_str)
        update_before = start_date + datetime.timedelta(days=1, hours=2)
        activities_file = file + 'activities.json'
        productivity_file = file + 'productivity.json'
        try:
            if datetime.datetime.fromtimestamp(os.path.getmtime(
                    activities_file)) > update_before:  ##### FIX THIS FILE
                # STUFF
                skip_activities = True
        except FileNotFoundError:
            pass
        try:
            if datetime.datetime.fromtimestamp(
                    os.path.getmtime(productivity_file)) > update_before:
                skip_productivity = True
        except FileNotFoundError:
            pass
        try:
            if not skip_activities:
                time.sleep(1)
                activities = rescuetime.get_hourly_subcategories(
                    str(start_date.date()))
                time.sleep(1)
                for x in rescuetime.get_hourly_categories(
                        str(start_date.date())):
                    activities.append(x)
                time.sleep(1)
                for y in rescuetime.get_hourly_activities(
                        str(start_date.date())):
                    activities.append(y)
                with open(activities_file, 'w') as f:
                    json.dump(activities, f)
            if not skip_productivity:
                time.sleep(1)
                productivity = rescuetime.get_hourly_productivity(
                    str(start_date.date()))
                for row in productivity:
                    split = datetime.datetime.strptime(row[0],
                                                       '%Y-%m-%dT%H:%M:%S')
                    row[0] = split.hour
                    row.insert(0, str(split.date()))
                with open(productivity_file, 'w') as f:
                    json.dump(productivity, f)
        except json.decoder.JSONDecodeError:
            continue
        start_date += datetime.timedelta(days=1)


if __name__ == "__main__":
    rescuetime = Rescuetime()

    rescuetime_folder = DASHBOARD_STATS_FOLDER

    print('called!')
    start_date = datetime.datetime(2016, 1, 1)
    today = datetime.datetime.today()
    while start_date <= today:
        skip_activities = False
        skip_productivity = False
        start_date_str = datetime.datetime.strftime(start_date, '%Y%m%d')
        print(start_date_str)
        file = rescuetime_folder + '{}/{}_'.format(start_date.year,
                                                   start_date_str)
        update_before = start_date + datetime.timedelta(days=1, hours=2)
        activities_file = file + 'activities.json'
        productivity_file = file + 'productivity.json'
        try:
            if datetime.datetime.fromtimestamp(
                    os.path.getmtime(activities_file)) > update_before:  ##### FIX THIS FILE STUFF
                skip_activities = True
        except FileNotFoundError:
            pass
        try:
            if datetime.datetime.fromtimestamp(os.path.getmtime(productivity_file)) > update_before:
                skip_productivity = True
        except FileNotFoundError:
            pass
        try:
            if not skip_activities:
                time.sleep(1)
                activities = rescuetime.get_hourly_subcategories(str(start_date.date()))
                time.sleep(1)
                for x in rescuetime.get_hourly_categories(str(start_date.date())):
                    activities.append(x)
                time.sleep(1)
                for y in rescuetime.get_hourly_activities(str(start_date.date())):
                    activities.append(y)
                with open(activities_file, 'w') as f:
                    json.dump(activities, f)
            if not skip_productivity:
                time.sleep(1)
                productivity = rescuetime.get_hourly_productivity(str(start_date.date()))
                for row in productivity:
                    # Convert hour to integer
                    split = datetime.datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S')
                    row[0] = split.hour
                    row.insert(0, str(split.date()))
                with open(productivity_file, 'w') as f:
                    json.dump(productivity, f)
        except json.decoder.JSONDecodeError:
            continue
        start_date += datetime.timedelta(days=1)

    sys.exit(1)
