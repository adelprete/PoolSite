import datetime
from django.utils import timezone
from django.db import models
from django.core.urlresolvers import reverse
from mysite.survivor import helpers as shelpers

from mysite.base import models as bmodels

class SurvivorSeason(bmodels.Definition):
    start_date = models.DateTimeField()
    display_winners = models.BooleanField("Display the winners for all the pools for this season",default=False)

    def __unicode__(self):
        return "%s" % (self.name)

class SurvivorPool(bmodels.Pool):
    entry_deadline = models.DateTimeField()
    season = models.ForeignKey('survivor.SurvivorSeason')

    making_merge = models.BooleanField("Castaway makes the Merge",default=True)
    individual_immunity = models.BooleanField("Castaway wins an individual Immunity Challenge",default=True)
    individual_reward = models.BooleanField("Castaway wins an individual reward",default=True)
    tribe_reward = models.BooleanField("Castaway's tribe wins reward",default=True)
    tribe_immunity = models.BooleanField("Castaway's Tribe wins immunity",default=True)
    finding_immunity = models.BooleanField("Castaway finds a hidden immunity idol",default=True)
    going_with_vote = models.BooleanField("Castaway is a part of the majority vote during a tribal council",default=True)
    successful_idol_use = models.BooleanField("Castaway used a hidden idol successfully",default=True)
    ri_victory = models.BooleanField("Castaway won the challenge at redemption island",default=True)
    returned_from_ri = models.BooleanField("Castaway returned from Redemption Island",default=True)
    ftc_votes = models.BooleanField("Castaway gets two points for every vote at the final tribal counsel",default=True)
    first_out = models.BooleanField("Castaway is the first person voted out",default=True)

    @property
    def is_past_due(self):
        if timezone.now() > self.season.start_date:
            return True
        return False

    def allow_new_picksheets(self):
        if datetime.timedelta(0) > (self.entry_deadline.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return False
        return True

    def get_absolute_url(self):
        return reverse("survivor_home",kwargs={'id':self.id})
    def save(self):
        if not self.admin_note:
            self.admin_note = shelpers.WELCOME_MESSAGE
        super(SurvivorPool, self).save()
        saved = True

    def __unicode__(self):
        return "%s" % (self.name)

class BaseCastaway(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30,blank=True,null=True)
    season = models.ForeignKey('survivor.SurvivorSeason')
    image_src = models.ImageField(upload_to = 'survivor/castaways/')

    #Each one is how many times it happened for the castaway
    making_merge = models.IntegerField(default=0)
    individual_immunity = models.IntegerField(default=0)
    individual_reward = models.IntegerField(default=0)
    tribe_reward = models.IntegerField(default=0)
    tribe_immunity = models.IntegerField(default=0)
    finding_immunity = models.IntegerField(default=0)
    going_with_vote = models.IntegerField(default=0)
    successful_idol_use = models.IntegerField(default=0)
    ri_victory = models.IntegerField(default=0)
    returned_from_ri = models.IntegerField(default=0)
    ftc_votes = models.IntegerField(default=0)
    first_out = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s - %s" % (self.first_name,self.season)

    def update_customcastaway_points(self):
        from mysite.survivor.helpers import POINTS_CATEGORIES
        custom_castaways = CustomCastaway.objects.filter(base_castaway=self).select_related('base_castaway','survivor_pool')
        for custom in custom_castaways:
            total_points = 0
            for key,value in POINTS_CATEGORIES.iteritems():
                if getattr(custom.survivor_pool,key):
                    total_points += POINTS_CATEGORIES[key] * getattr(custom.base_castaway,key)

            custom.total_points = total_points
            custom.save()
        return

    def save(self,*args,**kwargs):
        super(BaseCastaway,self).save(*args,**kwargs)
        self.update_customcastaway_points()

class CustomCastaway(models.Model):
    total_points = models.IntegerField(default=0)
    survivor_pool = models.ForeignKey('survivor.SurvivorPool')
    base_castaway = models.ForeignKey('survivor.BaseCastaway')

    def __unicode__(self):
        return "%s" % (self.base_castaway.first_name)

class SurvivorPickSheet(models.Model):
    name = models.CharField("Pick Sheet Name",max_length=30)
    total_points = models.IntegerField(default=0)
    four_picks = models.ManyToManyField('survivor.CustomCastaway')
    member = models.ForeignKey('auth.USER')
    survivor_pool = models.ForeignKey('survivor.SurvivorPool')

    def __unicode__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse("survivor_picksheet",kwargs={'id':self.survivor_pool.id,'picksheet_id':self.id})


