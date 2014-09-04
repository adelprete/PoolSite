import datetime
from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from mysite.base import models as bmodels
from mysite.nflbase import helpers as nflbhelpers
from mysite.nflsurvivor import helpers as nflshelpers


class NFLSurvivorPool(bmodels.Pool):
    entry_deadline = models.DateTimeField(help_text="No new members will be allowed in after this date and time, and no new picksheets will be created for leagues that have an "
                                                    "All at Once selection process.")
    season = models.ForeignKey('nflbase.Season')
    selection_process = models.CharField(max_length=30,choices=(('weekly','Week By Week'),('allatonce','All at Once')),
                                         help_text="Week By Week means each member will have a chance to make their picks before the start of each week.  "
                                                   "All at Once means each member has to make their selections for the entire year before the entry deadline.")
    start_week = models.CharField(max_length=30,blank=False,choices=(('wk1','Week 1'),('wk2','Week 2')),help_text="Which week of the season do you want to start on?")

    @property
    def is_past_due(self):
        if self.start_week == 'wk1':
            if timezone.now() > self.season.start_date:
                return True
        elif self.start_week == 'wk2':
            if timezone.now() > self.season.start_date2:
                return True
        return False

    def allow_new_picksheets(self):
        if datetime.timedelta(0) > (self.entry_deadline.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return False
        return True

    def get_absolute_url(self):
        return reverse("nflsurvivor_home",kwargs={'id':self.id})

    def save(self):
        if not self.admin_note:
            self.admin_note = nflshelpers.WELCOME_MESSAGE

        super(NFLSurvivorPool, self).save()
        saved = True

    def __unicode__(self):
        return "%s" % (self.name)

#This is used only for creating matchups, not used by any users.
class Matchup(models.Model):
    season = models.ForeignKey('nflbase.Season')
    away_team = models.ForeignKey('nflbase.Team',related_name='away_matchups')
    home_team = models.ForeignKey('nflbase.Team',related_name='home_matchups')
    winner = models.CharField(max_length=30,blank=True,choices=(('home_team','Home Team'),('away_team','Away Team')))
    week = models.CharField(max_length=30,choices=nflbhelpers.WEEKS)

    def __unicode__(self):
        return "%s: %s v %s" % (self.week,self.away_team,self.home_team)

    def update_picksheets(self):

        if self.winner != "":

            kwargs = {
                '{0}'.format(self.week): self.home_team,
                '{0}'.format('still_alive'): True,
            }
            home_team_picksheets = PickSheet.objects.filter(**kwargs)
            if self.week == 'week1':
                home_team_picksheets = home_team_picksheets.exclude(survivor_pool__start_week = 'wk2')

            kwargs = {
                '{0}'.format(self.week): self.away_team,
                '{0}'.format('still_alive'): True,
            }
            away_team_picksheets = PickSheet.objects.filter(**kwargs)
            if self.week == 'week1':
                away_team_picksheets = away_team_picksheets.exclude(survivor_pool__start_week = 'wk2')

            import pdb;pdb.set_trace()
            if self.winner == 'home_team':
                for sheet in home_team_picksheets:
                    #if self.week == 1 and not sheet.nflsurvivorpool.start_week == 'wk2':
                    sheet.total_points = sheet.total_points + 1
                    sheet.save()
                for sheet in away_team_picksheets:
                    #if self.week == 1 and not sheet.nflsurvivorpool.start_week == 'wk2':
                    sheet.still_alive = False
                    sheet.save()

            elif self.winner == 'away_team':
                for sheet in away_team_picksheets:
                    #if self.week == 1 and not sheet.nflsurvivorpool.start_week == 'wk2':
                        sheet.total_points = sheet.total_points + 1
                        sheet.save()
                for sheet in home_team_picksheets:
                    #if self.week == 1 and not sheet.nflsurvivorpool.start_week == 'wk2':
                    sheet.still_alive = False
                    sheet.save()

            #everyone who left it blank this week, dies.
            kwargs = {
                '{0}'.format(self.week): "",
                '{0}'.format('still_alive'): True,
            }
            if self.week == 'week1':
                PickSheet.objects.filter(**kwargs).exclude(survivor_pool__start_week = 'wk2').update(still_alive=False)
            else:
                PickSheet.objects.filter(**kwargs).update(still_alive=False)

        return

    def save(self,*args,**kwargs):
        super(Matchup,self).save(*args,**kwargs)
        self.update_picksheets()


class PickSheet(models.Model):
    name = models.CharField('Pick Sheet name',max_length=30)
    member = models.ForeignKey('auth.USER')
    survivor_pool = models.ForeignKey('nflsurvivor.NFLSurvivorPool')
    total_points = models.IntegerField(default=0)
    still_alive = models.BooleanField(default=True)

    #These are who they think will win
    week1 = models.CharField(max_length=30,blank=True)
    week2 = models.CharField(max_length=30,blank=True)
    week3 = models.CharField(max_length=30,blank=True)
    week4 = models.CharField(max_length=30,blank=True)
    week5 = models.CharField(max_length=30,blank=True)
    week6 = models.CharField(max_length=30,blank=True)
    week7 = models.CharField(max_length=30,blank=True)
    week8 = models.CharField(max_length=30,blank=True)
    week9 = models.CharField(max_length=30,blank=True)
    week10 = models.CharField(max_length=30,blank=True)
    week11 = models.CharField(max_length=30,blank=True)
    week12 = models.CharField(max_length=30,blank=True)
    week13 = models.CharField(max_length=30,blank=True)
    week14 = models.CharField(max_length=30,blank=True)
    week15 = models.CharField(max_length=30,blank=True)
    week16 = models.CharField(max_length=30,blank=True)
    week17 = models.CharField(max_length=30,blank=True)

    def __unicode__(self):
        return "%s" % (self.name)

    def get_absolute_url(self,week_num=1):
        return reverse("nflsurvivor_picksheet",kwargs={'id':self.survivor_pool.id,'picksheet_id':self.id,'week_num':week_num})

