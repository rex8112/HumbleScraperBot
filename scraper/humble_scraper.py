import asyncio

import aiohttp
import re
from datetime import datetime
from dateutil.relativedelta import *
from typing import Optional


class HumbleScraper:
    BASE_URL = 'https://www.humblebundle.com/'
    FIRST_HUMBLE = datetime(month=10, year=2015, day=1)

    def __init__(self):
        self.session = aiohttp.ClientSession(self.BASE_URL)
        self.months: list['HumbleChoiceMonth'] = []

    @staticmethod
    def get_current_month_year() -> tuple[str, int]:
        today = datetime.now()
        return today.strftime('%B').lower(), today.year

    async def scrape(self, month: str, year: int, enforce_old=False) -> Optional['HumbleChoiceMonth']:
        if (year == 2019 and month != 'december') or year < 2019 or enforce_old:
            url = f'/monthly/p/{month}_{year}_monthly'
        else:
            url = f'/membership/{month}-{year}'
        response = await self.session.get(url)
        if response.status == 404:
            return None
        html = await response.text()
        if url.endswith('_monthly'):
            regex = r'(?:"human_name": "(.*?)",)'
        else:
            regex = r'(?:"title": "(.*?)", "carousel)'
        results = re.findall(regex, html)

        humble_month = HumbleChoiceMonth(month, year, str(response.url))
        self.months.append(humble_month)
        for name in results:
            humble_month.add_game(name)
        return humble_month if humble_month.games else None

    async def initial_scrape(self):
        self.months.clear()
        date = self.FIRST_HUMBLE
        tasks = []
        while date <= datetime.now():
            month, year = date.strftime('%B').lower(), date.year
            tasks.append(self.scrape(month, year))
            if month == 'december' and year == 2019:
                tasks.append(self.scrape(month, year, enforce_old=True))
            date = date + relativedelta(months=1)
        all_results = []
        results = await asyncio.gather(*tasks)
        for result in results:
            if result is None:
                continue
            all_results.append(result)
        return all_results


class HumbleChoiceMonth:
    def __init__(self, month: str, year: int, url: str):
        self.month = month
        self.year = year
        self.url = url
        self.games = []

    def __eq__(self, o: object):
        if isinstance(o, HumbleChoiceMonth):
            return self.url == o.url
        else:
            return NotImplemented

    def __repr__(self):
        return f'<HumbleChoiceMonth: {self.month} of {self.year}>'

    def add_game(self, name: str):
        self.games.append(HumbleChoiceGame(name, self))


class HumbleChoiceGame:
    def __init__(self, name: str, month: 'HumbleChoiceMonth'):
        self.name = name
        self.month = month

    def __eq__(self, o: object):
        if isinstance(o, HumbleChoiceGame):
            return self.name == o.name and self.month == o.month
        else:
            return NotImplemented

    def __repr__(self):
        return f'<HumbleChoiceGame: {self.name}>'
