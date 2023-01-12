from datetime import datetime
from typing import Optional

import peewee

from scrapper.database import HumbleMonth, db, HumbleGame


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
                try:
                    self._db_entry = HumbleMonth.get(HumbleMonth.url == self.url)
                except peewee.DoesNotExist:
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

    @staticmethod
    def get_all() -> dict[str, 'HumbleChoiceMonth']:
        d = {}
        for entry in HumbleMonth.select():
            m = HumbleChoiceMonth.from_database(entry)
            d[m.url] = m
        return d


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
            try:
                self._db_entry = HumbleGame.get(HumbleGame.month == self.month.id and HumbleGame.name == self.name)
            except peewee.DoesNotExist:
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
