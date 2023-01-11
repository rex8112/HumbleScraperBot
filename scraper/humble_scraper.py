import asyncio

import aiohttp
import re
from datetime import datetime
from dateutil.relativedelta import *
from typing import Optional, TYPE_CHECKING, Union

from .database import HumbleMonth, HumbleGame, db

if TYPE_CHECKING:
    from peewee import Query


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


def month_to_str(month: int):
    if isinstance(month, str):
        return month
    return datetime(2023, month, 1).strftime('%B').lower()


def month_to_int(month: str):
    if isinstance(month, int):
        return month
    return datetime.strptime(month, '%B').month


class HumbleChoiceMonth:
    def __init__(self, month: str, year: int, url: str):
        self.month = month
        self.year = year
        self.url = url
        self.games: list['HumbleChoiceGame'] = []
        self._db_entry: Optional['HumbleMonth'] = None

    def __eq__(self, o: object):
        if isinstance(o, HumbleChoiceMonth):
            return self.url == o.url
        else:
            return NotImplemented

    def __repr__(self):
        return f'<HumbleChoiceMonth: {self.month} of {self.year}>'

    def add_game(self, game: 'HumbleChoiceGame'):
        self.games.append(game)

    @property
    def id(self):
        return self._db_entry.id if self._db_entry else None

    @property
    def db_entry(self):
        return self._db_entry

    def save(self):
        with db.atomic():
            if self._db_entry is None:
                self._db_entry = HumbleMonth(month=month_to_int(self.month), year=self.year, url=self.url)
                self._db_entry.save()
            else:
                self._db_entry.update(month=month_to_int(self.month), year=self.year, url=self.url)
                self._db_entry.save()
            for game in self.games:
                game.save()

    @classmethod
    def from_database(cls, entry: HumbleMonth):
        month = cls(month_to_str(entry.month), entry.year, entry.url)
        month._db_entry = entry
        for game in entry.games:
            month.add_game(HumbleChoiceGame.from_database(game, month))
        return month


class HumbleChoiceGame:
    def __init__(self, name: str, month: 'HumbleChoiceMonth'):
        self.name = name
        self.month = month
        self._db_entry: Optional['HumbleGame'] = None

    def __eq__(self, o: object):
        if isinstance(o, HumbleChoiceGame):
            return self.name == o.name and self.month == o.month
        else:
            return NotImplemented

    def __repr__(self):
        return f'<HumbleChoiceGame: {self.name}>'

    @property
    def id(self):
        return self._db_entry.id if self._db_entry else None

    def save(self):
        if self.month.db_entry is None:
            raise ValueError('Month must be saved.')
        if self._db_entry is None:
            self._db_entry = HumbleGame(name=self.name, month=self.month.db_entry)
            self._db_entry.save()
        else:
            self._db_entry.update(name=self.name, month=self.month.db_entry)
            self._db_entry.save()

    @classmethod
    def from_database(cls, entry: HumbleGame, month: 'HumbleChoiceMonth'):
        game = cls(entry.name, month)
        game._db_entry = entry
        return game
