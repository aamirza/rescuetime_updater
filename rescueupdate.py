import datetime
import json
import os
from enum import Enum

try:
    from rescuetime import Rescuetime
except ImportError:
    from .rescuetime import Rescuetime


RESCUETIME_STATS_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/dashboard_stats/rescuetime/"


class With(Enum):
    """Whether to write a date with or without dash separators  (e.g.
    2020-01-01 vs 20200101)"""
    # Used Enum instead of Boolean in case new date styles need to be added
    NO_DASHES = 0
    DASHES = 1


def convert_date_to_str(with_dashes, date):
    if with_dashes == With.DASHES:
        return datetime.datetime.strftime(date, '%Y-%m-%d')
    elif with_dashes == With.NO_DASHES:
        return datetime.datetime.strftime(date, '%Y%m%d')


def date_range(start_date, end_date, *, inclusive=True):
    inclusive_day = 1 if inclusive else 0
    days_between_dates = (end_date - start_date).days + inclusive_day
    for days in range(days_between_dates):
        yield start_date + datetime.timedelta(days=days)


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


class RescueDashboard():
    def __init__(self):
        self.rescuetime_folder = RESCUETIME_STATS_FOLDER
        self.rescuetime = Rescuetime()
        self.start_date = datetime.datetime(2016, 1, 1)

    def _get_record_from_date(self, date: datetime.datetime) -> str:
        date_str = convert_date_to_str(With.NO_DASHES, date)
        return f"{self.rescuetime_folder}{date.year}/{date_str}_"

    def activities_file_for_date(self, date):
        return self._get_record_from_date(date) + "activities.json"

    def productivity_file_for_date(self, date):
        return self._get_record_from_date(date) + "productivity.json"

    def activities_file_is_up_to_date(self, date):
        return file_is_up_to_date(date, self.activities_file_for_date(date))

    def productivity_file_is_up_to_date(self, date):
        return file_is_up_to_date(date, self.productivity_file_for_date(date))

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
            datestring_index = 0
            hourly_data[datestring_index] = get_hour_from_string(
                hourly_data[datestring_index])
            hourly_data.insert(0, date)  # Insert proper date format
        return productivity

    @staticmethod
    def dump_json_to_file(file, data):
        with open(file, 'w') as f:
            json.dump(data, f)

    def update_activities_file(self, date):
        self.dump_json_to_file(file=self.activities_file_for_date(date),
                               data=self.get_activity_data(date))

    def update_productivity_file(self, date):
        self.dump_json_to_file(file=self.productivity_file_for_date(date),
                               data=self.get_productivity_data(date))

    def update_data(self):
        for date in date_range(self.start_date, datetime.datetime.today()):
            if not self.activities_file_is_up_to_date(date):
                self.update_activities_file(date)
            if not self.productivity_file_is_up_to_date(date):
                self.update_productivity_file(date)


def main():
    dashboard = RescueDashboard()
    dashboard.update_data()


if __name__ == "__main__":
    main()
