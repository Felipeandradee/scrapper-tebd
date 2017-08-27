from peewee import *


db = MySQLDatabase('tebd', user='root', passwd='')


class Congress(Model):

    name = CharField()
    submissionDeadline = DateField()
    reviewDeadline = DateField()

    class Meta:
        database = db


class Paper(Model):

    title = CharField()
    abstract = CharField()
    finalScore = FloatField()
    accepted = BooleanField()

    class Meta:
        database = db