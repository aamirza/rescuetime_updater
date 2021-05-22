import requests
import datetime


APIKEY = ""  # Insert your Rescuetime API key here.


class Rescuetime:
    def __init__(self, api_key=APIKEY):
        self.apiKey = api_key
        self.url = "https://www.rescuetime.com/anapi/data"
        self.highlight_url = "https://www.rescuetime.com/anapi/highlights_feed"

    def get_productivity(self, date_start, interval='day', date_end=''):
        if date_end == '':
            date_end = date_start
        params = {
            'pv': 'rank',
            'rs': interval,
            'rb': date_start,
            're': date_end,
            'rk': 'productivity',
            'key': self.apiKey,
            'format': 'json'
        }
        return self.call_api(params)

    def get_hourly_productivity(self, date, hour=''):
        params = {
            'pv': 'interval',
            'rs': 'hour',
            'rb': date,
            're': date,
            'rk': 'productivity',
            'key': self.apiKey,
            'format': 'json'
        }
        response = self.call_api(params)
        if hour != '':
            if hour < 10:
                hour = "0{}".format(hour)
            hour = str(hour)
            datestring = "{}T{}:00:00".format(date, hour)
            relevant = []
            for row in response:
                if row[0] != datestring:
                    continue
                if row[0] == datestring:
                    relevant.append(row)
            response = relevant
        return response

    def get_activities(self, date_start, date_end=''):
        if date_end == '':
            date_end = date_start
        params = {
            'pv': 'rank',
            'rs': 'day',
            'rb': date_start,
            're': date_end,
            'rk': 'activities',
            'key': self.apiKey,
            'format': 'json'
        }
        return self.call_api(params)

    def get_hourly_activities(self, date):
        params = {
            'pv': 'interval',
            'rs': 'hour',
            'rb': date,
            're': date,
            'rk': 'activities',
            'key': self.apiKey,
            'format': 'json'
        }
        response = self.call_api(params)
        for row in response:
            split = datetime.datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S')
            row[0] = split.hour
            row.insert(0, str(split.date()))
        return response


    def get_categories(self, date_start, date_end=''):
        if date_end == '':
            date_end = date_start
        params = {
            'pv': 'rank',
            'rs': 'day',
            'rb': date_start,
            're': date_end,
            'rk': 'overview',
            'key': self.apiKey,
            'format': 'json'
        }
        return self.call_api(params)

    def get_hourly_categories(self, date):
        params = {
            'pv': 'interval',
            'rs': 'hour',
            'rb': date,
            're': date,
            'rk': 'overview',
            'key': self.apiKey,
            'format': 'json'
        }
        response = self.call_api(params)
        for row in response:
            split = datetime.datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S')
            row[0] = split.hour
            row.insert(0, str(split.date()))
        return response


    def get_subcategories(self, date_start, date_end=''):
        if date_end == '':
            date_end = date_start
        params = {
            'pv': 'rank',
            'rs': 'day',
            'rb': date_start,
            're': date_end,
            'rk': 'category',
            'key': self.apiKey,
            'format': 'json'
        }
        return self.call_api(params)

    def get_hourly_subcategories(self, date):
        params = {
            'pv': 'interval',
            'rs': 'hour',
            'rb': date,
            're': date,
            'rk': 'category',
            'key': self.apiKey,
            'format': 'json'
        }
        response = self.call_api(params)
        for row in response:
            split = datetime.datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S')
            row[0] = split.hour
            row.insert(0, str(split.date()))
        return response

    def get_efficiency(self, date):
        prod = self.get_productivity(date)
        very_dist = 0
        dist = 0
        neutral = 0
        pro = 0
        very_pro = 0
        for rank in prod:
            if rank[3] == -2:
                very_dist = rank[1]
            elif rank[3] == -1:
                dist = rank[1]
            elif rank[3] == 0:
                neutral = rank[1]
            elif rank[3] == 1:
                pro = rank[1]
            elif rank[3] == 2:
                very_pro = rank[1]
        all_time = very_pro + pro + neutral + dist + very_dist
        efficiency = round(((very_pro + pro*0.75 + neutral*0.5 + dist*0.25 + very_dist*0)/all_time)*100, 2)
        return efficiency

    def get_highlights(self):
        params = {
            'key': self.apiKey
        }
        return requests.get(url=self.highlight_url, params=params).json()

    def call_api(self, values, url=''):
        if not url:
            url = self.url
        response = requests.get(url, params=values)
        result = response.json()
        return result['rows']
