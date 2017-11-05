from peewee import *


db = MySQLDatabase('congress', user='root', passwd='')


class Congress(Model):
    idCongress = PrimaryKeyField()
    name = CharField()
    submissionDeadline = DateField()
    reviewDeadline = DateField()

    class Meta:
        database = db


class Paper(Model):
    paperId = PrimaryKeyField()
    title = CharField()
    abstract = CharField()
    finalScore = FloatField()
    accepted = BooleanField()

    class Meta:
        database = db


class Congress_Paper(Model):
    idCongress = IntegerField()
    idPaper = IntegerField()
    # idPaper = IntegerField()

    class Meta:
        primary_key = False
        database = db


class Autor(Model):

    idParticipant = IntegerField()
    idPaper = IntegerField()

    class Meta:
        database = db
        primary_key = False


class Participant(Model):
    registrationId = IntegerField()

    class Meta:
        database = db


class Review(Model):
    idReview = PrimaryKeyField()
    idPaper = IntegerField()
    comment = CharField()
    score = FloatField()

    class Meta:
        database = db


class Reviser(Model):
    idReview =IntegerField()
    idParticipant=IntegerField()

    class Meta:
        database = db
