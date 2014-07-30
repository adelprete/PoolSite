import datetime
from django.utils import timezone
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from mysite.amazingrace import helpers as ahelpers

from mysite.base import models as bmodels

class AmazingRaceSeason(bmodels.Definition):
    start_date = models.DateTimeField()
    display_winners = models.BooleanField("Display the winners for all the pools for this season",default=False)

    def __unicode__(self):
        return "%s" % (self.name)

class AmazingRacePool(bmodels.Pool):
    entry_deadline = models.DateTimeField()
    season = models.ForeignKey('amazingrace.AmazingRaceSeason')

    completing_leg = models.BooleanField("Team completes a leg",default=True)
    first_in_detour = models.BooleanField("Team is the first to complete the Detour/Roadblock",default=True)
    used_obstacle = models.BooleanField("Team used an Obstacle on another team(UTurn,Yield,etc)",default=True)
    first_place = models.BooleanField("Team are first to arrive at the pit stop",default=True)
    first_team_out = models.BooleanField("Team was the first to be eliminated",default=True)

    @property
    def is_past_due(self):
        if timezone.now() > self.season.start_date:
            return True
        return False

    def allow_new_picksheets(self):
        if datetime.timedelta(0) > (self.entry_deadline.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return False
        if settings.AMAZING_RACE_PICKSHEETS_OPEN == False:
            return False
        return True

    def get_absolute_url(self):
        return reverse("amazingrace_home",kwargs={'id':self.id})

    def save(self):
        if not self.admin_note:
            self.admin_note = ahelpers.WELCOME_MESSAGE
        super(AmazingRacePool, self).save()
        saved = True

    def __unicode__(self):
        return "%s" % (self.name)

class BaseTeam(models.Model):
    team_member_1 = models.CharField(max_length=30)
    team_member_2 = models.CharField(max_length=30)
    nickname = models.CharField(max_length=30)
    season = models.ForeignKey('amazingrace.AmazingRaceSeason')
    image_src = models.ImageField(upload_to = 'amazingrace/teams/')

    #Each one is how many times it happened for the team
    completing_leg = models.IntegerField(default=0)
    first_in_detour = models.IntegerField(default=0)
    used_obstacle = models.IntegerField(default=0)
    first_place = models.IntegerField(default=0)
    first_team_out = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s %s - %s" % (self.team_member_1,self.team_member_2,self.season)

    def update_customteam_points(self):
        from mysite.amazingrace.helpers import POINTS_CATEGORIES
        custom_teams = CustomTeam.objects.filter(base_team=self).select_related('base_team','amazingrace_pool')
        for custom in custom_teams:
            total_points = 0
            for key,value in POINTS_CATEGORIES.iteritems():
                if getattr(custom.amazingrace_pool,key):
                    total_points += POINTS_CATEGORIES[key] * getattr(custom.base_team,key)

            custom.total_points = total_points
            custom.save()
        return

    def save(self,*args,**kwargs):
        super(BaseTeam,self).save(*args,**kwargs)
        self.update_customteam_points()

class CustomTeam(models.Model):
    total_points = models.IntegerField(default=0)
    amazingrace_pool = models.ForeignKey('amazingrace.AmazingRacePool')
    base_team = models.ForeignKey('amazingrace.BaseTeam')

    def __unicode__(self):
        return "%s & %s" % (self.base_team.team_member_1,self.base_team.team_member_2)

class AmazingRacePickSheet(models.Model):
    name = models.CharField("Pick Sheet Name",max_length=30)
    total_points = models.IntegerField(default=0)
    picks = models.ManyToManyField('amazingrace.CustomTeam')
    member = models.ForeignKey('auth.USER')
    amazingrace_pool = models.ForeignKey('amazingrace.AmazingRacePool')

    def __unicode__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse("amazingrace_picksheet",kwargs={'id':self.amazingrace_pool.id,'picksheet_id':self.id})
