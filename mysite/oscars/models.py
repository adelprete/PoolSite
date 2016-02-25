from django.utils import timezone
import datetime
from django.db import models
from django.core.urlresolvers import reverse
from datetime import timedelta
from mysite.base import models as bmodels
from mysite.oscars import helpers as ohelpers


class OscarCeremony(bmodels.Definition):
    """
    The Oscar Ceremony model is mainly used to form a relationship between oscar pools and the ceremony that are for.
    """
    date = models.DateTimeField(help_text="Date and time of ceremony")

class OscarPool(bmodels.Pool):
    """
    This Class is for every Oscar Pool.  It has relationships with its ballots and ceremony.
    """
    entry_deadline = models.DateTimeField(null=True,blank=True,help_text="Last date pool members can submit there ballots")
    oscar_ceremony = models.ForeignKey('oscars.OscarCeremony',null=True)
    how_to_win = models.CharField(max_length=40, choices={('points','By Accumulated Points'),('correct','By Number of Correct Picks')})
    up_to_date = models.BooleanField()

    @property
    def is_past_due(self):
        if timezone.now() > self.oscar_ceremony.date:
            return True
        return False

    def allow_new_picksheets(self):
        if datetime.timedelta(0) > (self.entry_deadline.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return False
        return True

    @property
    def can_display_winners(self):
        if timezone.now() > (self.oscar_ceremony.date + timedelta(hours=4)):
            return True
        return False

    def __unicode__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse("oscar_home",kwargs={'id':self.id})

    def save(self):
        if not self.admin_note:
            self.admin_note = ohelpers.WELCOME_MESSAGE
        super(OscarPool, self).save()
        saved = True

class Response(models.Model):
    ballot = models.ForeignKey('oscars.Ballot')
    category = models.ForeignKey('oscars.CustomCategory')
    predicted_winner = models.ForeignKey('oscars.Nominee')
    points = models.IntegerField(default=0)
    correct = models.NullBooleanField()

    class Meta:
        ordering = ['category__base_category__priority']

class Ballot(models.Model):

    pool = models.ForeignKey('oscars.OscarPool')
    name = models.CharField("Name of Ballot",max_length=30)
    play_off_guess = models.IntegerField("How many awards in will we have to go until they try to 'Play off' a winner's award speech?",help_text="This will be used only as a tie breaker.",null=True,blank=True);
    member = models.ForeignKey('auth.User')
    total_points = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    last_save_date = models.DateTimeField()

    def __unicode__(self):
        return "%s -- %s" % (self.member,self.name)

    def get_absolute_url(self):
        return reverse("oscar_ballot",kwargs={'id':self.pool.id,'ballot_id':self.id})

    def save(self,update_last_save=False):
        if update_last_save == True:
            self.last_save_date = timezone.now()
        super(Ballot, self).save()
        saved = True

class CustomCategory(bmodels.Definition):

    pool = models.ForeignKey('oscars.OscarPool')
    points = models.IntegerField()
    base_category = models.ForeignKey('oscars.BaseCategory',blank=True,null=True)

    class Meta:
        ordering = ['base_category__priority']


class BaseCategory(bmodels.Definition):

    ceremony = models.ForeignKey('oscars.OscarCeremony')
    nominee = models.ManyToManyField('oscars.Nominee',blank=True,help_text="Enter a year and save to see Nominees for that year only")
    winner = models.ForeignKey('oscars.Nominee',related_name="winner_set",blank=True,null=True)
    year = models.IntegerField(help_text="Year of the Award Ceremony")
    points = models.IntegerField(help_text="Default points")
    priority = models.IntegerField()

    def __unicode__(self):
        return "%s - %s" % (self.name,self.year)

    def update_ballot_points(self):

        custom_categories = CustomCategory.objects.filter(base_category=self)
        for cat in custom_categories:
            for response in cat.response_set.all():
                if response.predicted_winner == self.winner:
                    response.points = cat.points
                    response.correct = True
                    response.save()
                else:
                    response.points = 0
                    response.correct = False
                    response.save()

        return

    def save(self,*args,**kwargs):
        self.update_ballot_points()
        for pool in self.ceremony.oscarpool_set.all():
            pool.up_to_date = False
            pool.save()
        super(BaseCategory,self).save(*args,**kwargs)

    class Meta:
        ordering = ['priority']


class Nominee(bmodels.Definition):
    secondary_name = models.CharField(max_length=150,blank=False,null=True)
    year = models.IntegerField()

    def __unicode__(self):
        if self.name == self.secondary_name:
            return "%s" % (self.secondary_name)
        elif self.name:
            return "%s  - %s" % (self.name,self.secondary_name)
