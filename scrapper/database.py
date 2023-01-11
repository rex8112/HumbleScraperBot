from peewee import *


db = SqliteDatabase('humble.db')


def initialize_database():
    tables = [HumbleMonth, HumbleGame, RedeemedUserGame, SubbedUserMonth, User]
    db.create_tables(tables)


class BaseModel(Model):
    class Meta:
        database = db


class HumbleMonth(BaseModel):
    id = AutoField()
    month = IntegerField()
    year = IntegerField()
    url = TextField(unique=True, index=True)


class HumbleGame(BaseModel):
    id = AutoField()
    name = TextField()
    description = TextField(default='')
    image_url = TextField(default='')
    month = ForeignKeyField(HumbleMonth, backref='games')


class User(BaseModel):
    id = BigIntegerField(unique=True, primary_key=True)
    private = BooleanField(default=False)

    def add_sub_month(self, month: 'HumbleMonth') -> 'SubbedUserMonth':
        conn = SubbedUserMonth(user=self, month=month)
        conn.save()
        return conn

    def add_redeemed_game(self, game: 'HumbleGame', gift=False) -> 'RedeemedUserGame':
        conn = RedeemedUserGame(user=self, game=game, gifted=gift)
        conn.save()
        return conn

    def get_games(self):
        query = (HumbleGame
                 .select(HumbleGame)
                 .join(HumbleMonth)
                 .join(SubbedUserMonth)
                 .join(User)
                 .where(User.id == self.id))
        return query


class SubbedUserMonth(BaseModel):
    user = ForeignKeyField(User)
    month = ForeignKeyField(HumbleMonth)


class RedeemedUserGame(BaseModel):
    user = ForeignKeyField(User)
    game = ForeignKeyField(HumbleGame)
    gifted = BooleanField(default=False)

