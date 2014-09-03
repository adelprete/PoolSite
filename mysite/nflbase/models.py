import datetime
from django.db import models
from mysite.base import models as bmodels
from mysite.nflbase import helpers as nflbhelpers

class Season(bmodels.Definition):
    start_date = models.DateTimeField()
    start_date2 = models.DateTimeField(help_text="This is when the Week 2 starts")
    display_winners = models.BooleanField("Display the winners for all the pools for this season",default=False)

    week3 = models.DateTimeField()
    week4 = models.DateTimeField()
    week5 = models.DateTimeField()
    week6 = models.DateTimeField()
    week7 = models.DateTimeField()
    week8 = models.DateTimeField()
    week9 = models.DateTimeField()
    week10 = models.DateTimeField()
    week11 = models.DateTimeField()
    week12 = models.DateTimeField()
    week13 = models.DateTimeField()
    week14 = models.DateTimeField()
    week15 = models.DateTimeField()
    week16 = models.DateTimeField()
    week17 = models.DateTimeField()

    def __unicode__(self):
        return "%s" % (self.name)

    def get_current_week(self):

        if datetime.timedelta(0) > (self.week17.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week17'
        if datetime.timedelta(0) > (self.week16.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week16'
        if datetime.timedelta(0) > (self.week15.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week15'
        if datetime.timedelta(0) > (self.week14.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week14'
        if datetime.timedelta(0) > (self.week13.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week13'
        if datetime.timedelta(0) > (self.week12.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week12'
        if datetime.timedelta(0) > (self.week11.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week11'
        if datetime.timedelta(0) > (self.week10.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week10'
        if datetime.timedelta(0) > (self.week9.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week9'
        if datetime.timedelta(0) > (self.week8.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week8'
        if datetime.timedelta(0) > (self.week7.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week7'
        if datetime.timedelta(0) > (self.week6.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week6'
        if datetime.timedelta(0) > (self.week5.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week5'
        if datetime.timedelta(0) > (self.week4.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week4'
        if datetime.timedelta(0) > (self.week3.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week3'
        if datetime.timedelta(0) > (self.start_date2.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week2'
        if datetime.timedelta(0) > (self.start_date.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return 'week1'
        return None

class Team(models.Model):
    city = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    conference = models.CharField(max_length=30,choices=nflbhelpers.CONFERENCES)
    image_src = models.ImageField(upload_to = 'nflbase/teams/',blank=True, null=True)

    def __unicode__(self):
        return "%s %s" % (self.city,self.name)






