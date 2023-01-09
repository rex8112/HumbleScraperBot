from peewee import *


db = SqliteDatabase('humble.db')


class BaseModel(Model):
    class Meta:
        database = db


class HumbleMonth(BaseModel):
    id = AutoField()
    month = IntegerField()
    year = IntegerField()


class HumbleGame(BaseModel):
    id = AutoField()
    name = TextField()
    description = TextField()
    image_url = TextField()
    month = ForeignKeyField(HumbleMonth, backref='games')


class User(BaseModel):
    id = BigIntegerField(unique=True, primary_key=True)
    private = BooleanField(default=False)


class SubbedUserMonth(BaseModel):
    user = ForeignKeyField(User)
    month = ForeignKeyField(HumbleMonth)


class RedeemedUserGame(BaseModel):
    user = ForeignKeyField(User)
    month = ForeignKeyField(HumbleGame)
    gifted = BooleanField(default=False)

