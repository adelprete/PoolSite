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

class Team(models.Model):
    city = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    conference = models.CharField(max_length=30,choices=nflbhelpers.CONFERENCES)
    image_src = models.ImageField(upload_to = 'nflbase/teams/',blank=True, null=True)

    def __unicode__(self):
        return "%s %s" % (self.city,self.name)






