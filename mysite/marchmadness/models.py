import datetime
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from mysite.base import models as bmodels
from mysite.marchmadness import helpers as mhelpers

# Create your models here.
#class Tournament(models.Model):
#    start_date = models.DateTimeField(help_text="Start time of the first game")

class NCAABasketballTourney(bmodels.Definition):
    start_date = models.DateTimeField()
    display_winners = models.BooleanField("Display the winners for all the pools for this Tournament",default=False)

    def __unicode__(self):
        return "%s" % (self.name)

    def latest_season(self):
        season = NCAABasketballTourney.objects.latest('start_date')
        if self == season:
            return True
        return False

    def save(self):
        if self.display_winners:
            pools = MarchMadnessPool.objects.filter(season=self)
            for pool in pools:
                brackets = pool.bracket_set.filter(march_madness_pool=pool).distinct()

                brackets = brackets.order_by('-total_points','tie_breaker_score')

                try:
                    pool.winner = brackets[0].member
                except:
                    pool.winner = None
                try:
                    pool.second_place_id = brackets[1].member
                except:
                    pool.second_place_id = None
                try:
                    pool.third_place_id = brackets[2].member
                except:
                    pool.third_place_id = None

                pool.save()

        super(NCAABasketballTourney, self).save()

class MarchMadnessPool(bmodels.Pool):
    entry_deadline = models.DateTimeField()
    season = models.ForeignKey('marchmadness.NCAABasketballTourney')

    round_1 = models.IntegerField(blank=True)
    round_2 = models.IntegerField(blank=True)
    round_3 = models.IntegerField(blank=True)
    round_4 = models.IntegerField(blank=True)
    round_5 = models.IntegerField(blank=True)
    round_6 = models.IntegerField(blank=True)


    @property
    def is_past_due(self):
        if timezone.now() > self.season.start_date:
            return True
        return False

    def allow_new_picksheets(self):
        if datetime.timedelta(0) > (self.entry_deadline.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return False
        if settings.MARCH_MADNESS_BRACKETS_OPEN == False:
            return False
        return True

    def get_absolute_url(self):
        return reverse("marchmadness_home",kwargs={'id':self.id})

    def __unicode__(self):
        return "%s" % (self.name)

    def save(self):
        if not self.admin_note:
            self.admin_note = mhelpers.WELCOME_MESSAGE
        super(MarchMadnessPool, self).save()
        saved = True

class Bracket(models.Model):
    name = models.CharField('Bracket Name',max_length=30)
    member = models.ForeignKey('auth.USER')
    official_bracket = models.BooleanField(default=False)
    total_points = models.IntegerField(default=0)
    march_madness_pool = models.ForeignKey(MarchMadnessPool,null=True,blank=True)
    tie_breaker_score_1 = models.IntegerField(null=True,blank=True);
    tie_breaker_score_2 = models.IntegerField(null=True,blank=True);
    tie_breaker_score = models.IntegerField(default=0,null=True,blank=True);


    B1 = models.CharField(max_length=30,null=True,blank=True)
    B2 = models.CharField(max_length=30,null=True,blank=True)
    B3 = models.CharField(max_length=30,null=True,blank=True)
    B4 = models.CharField(max_length=30,null=True,blank=True)
    B5 = models.CharField(max_length=30,null=True,blank=True)
    B6 = models.CharField(max_length=30,null=True,blank=True)
    B7 = models.CharField(max_length=30,null=True,blank=True)
    B8 = models.CharField(max_length=30,null=True,blank=True)
    B9 = models.CharField(max_length=30,null=True,blank=True)
    B10 = models.CharField(max_length=30,null=True,blank=True)
    B11 = models.CharField(max_length=30,null=True,blank=True)
    B12 = models.CharField(max_length=30,null=True,blank=True)
    B13 = models.CharField(max_length=30,null=True,blank=True)
    B14 = models.CharField(max_length=30,null=True,blank=True)
    B15 = models.CharField(max_length=30,null=True,blank=True)
    B16 = models.CharField(max_length=30,null=True,blank=True)
    B17 = models.CharField(max_length=30,null=True,blank=True)
    B18 = models.CharField(max_length=30,null=True,blank=True)
    B19 = models.CharField(max_length=30,null=True,blank=True)
    B20 = models.CharField(max_length=30,null=True,blank=True)
    B21 = models.CharField(max_length=30,null=True,blank=True)
    B22 = models.CharField(max_length=30,null=True,blank=True)
    B23 = models.CharField(max_length=30,null=True,blank=True)
    B24 = models.CharField(max_length=30,null=True,blank=True)
    B25 = models.CharField(max_length=30,null=True,blank=True)
    B26 = models.CharField(max_length=30,null=True,blank=True)
    B27 = models.CharField(max_length=30,null=True,blank=True)
    B28 = models.CharField(max_length=30,null=True,blank=True)
    B29 = models.CharField(max_length=30,null=True,blank=True)
    B30 = models.CharField(max_length=30,null=True,blank=True)
    B31 = models.CharField(max_length=30,null=True,blank=True)
    B32 = models.CharField(max_length=30,null=True,blank=True)
    C1 = models.CharField(max_length=30,null=True,blank=True)
    C2 = models.CharField(max_length=30,null=True,blank=True)
    C3 = models.CharField(max_length=30,null=True,blank=True)
    C4 = models.CharField(max_length=30,null=True,blank=True)
    C5 = models.CharField(max_length=30,null=True,blank=True)
    C6 = models.CharField(max_length=30,null=True,blank=True)
    C7 = models.CharField(max_length=30,null=True,blank=True)
    C8 = models.CharField(max_length=30,null=True,blank=True)
    C9 = models.CharField(max_length=30,null=True,blank=True)
    C10 = models.CharField(max_length=30,null=True,blank=True)
    C11 = models.CharField(max_length=30,null=True,blank=True)
    C12 = models.CharField(max_length=30,null=True,blank=True)
    C13 = models.CharField(max_length=30,null=True,blank=True)
    C14 = models.CharField(max_length=30,null=True,blank=True)
    C15 = models.CharField(max_length=30,null=True,blank=True)
    C16 = models.CharField(max_length=30,null=True,blank=True)
    D1 = models.CharField(max_length=30,null=True,blank=True)
    D2 = models.CharField(max_length=30,null=True,blank=True)
    D3 = models.CharField(max_length=30,null=True,blank=True)
    D4 = models.CharField(max_length=30,null=True,blank=True)
    D5 = models.CharField(max_length=30,null=True,blank=True)
    D6 = models.CharField(max_length=30,null=True,blank=True)
    D7 = models.CharField(max_length=30,null=True,blank=True)
    D8 = models.CharField(max_length=30,null=True,blank=True)
    E1 = models.CharField(max_length=30,null=True,blank=True)
    E2 = models.CharField(max_length=30,null=True,blank=True)
    E3 = models.CharField(max_length=30,null=True,blank=True)
    E4 = models.CharField(max_length=30,null=True,blank=True)
    F1 = models.CharField(max_length=30,null=True,blank=True)
    F2 = models.CharField(max_length=30,null=True,blank=True)
    champ = models.CharField("Champion",max_length=30,null=True,blank=True)

    def __unicode__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse("marchmadness_bracket",kwargs={'id':self.march_madness_pool.id,'bracket_id':self.id})

    def save(self):
        if self.official_bracket:
            all_brackets = Bracket.objects.filter(march_madness_pool__season=self.march_madness_pool.season).exclude(official_bracket=True).select_related('march_madness_pool')

            for bracket in all_brackets:
                total_points = 0
                for field in mhelpers.BRACKET_FIELDS:
                    if getattr(self,field) != '':
                        bracket_val = getattr(bracket,field)
                        official_val = getattr(self,field)
                        if(bracket_val == official_val):
                            if field[0] == 'B':
                                total_points += bracket.march_madness_pool.round_1
                            elif field[0] == 'C':
                                total_points += bracket.march_madness_pool.round_2
                            elif field[0] == 'D':
                                total_points += bracket.march_madness_pool.round_3
                            elif field[0] == 'E':
                                total_points += bracket.march_madness_pool.round_4
                            elif field[0] == 'F':
                                total_points += bracket.march_madness_pool.round_5

                if self.champ != '' and bracket.champ == self.champ:
                    total_points += bracket.march_madness_pool.round_6

                if self.tie_breaker_score_1 and self.tie_breaker_score_2:
                    if bracket.tie_breaker_score_1:
                        diff_1 = self.tie_breaker_score_1 - bracket.tie_breaker_score_1
                    else:
                        diff_1 = self.tie_breaker_score_1

                    if bracket.tie_breaker_score_2:
                        diff_2 = self.tie_breaker_score_2 - bracket.tie_breaker_score_2
                    else:
                        diff_2 = self.tie_breaker_score_2

                    bracket.tie_breaker_score = abs(diff_1) + abs(diff_2)
                    bracket.save()

                if total_points != bracket.total_points:
                    bracket.total_points = total_points
                    bracket.save()



        super(Bracket, self).save()