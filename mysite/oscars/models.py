from django.utils import timezone
import datetime
from django.db import models
from django.core.urlresolvers import reverse
from datetime import timedelta
from mysite.base import models as bmodels
from mysite.oscars import helpers as ohelpers


class OscarCeremony(bmodels.Definition):
    """
    The Oscar Ceremony model is mainly used to form a relationship between oscar pools and the ceremony that they are for.
    """
    date = models.DateTimeField(help_text="Date and time of ceremony")
    display_winners = models.BooleanField("Display the winners for all the pools for this season",default=False)

    def save(self):
        """
            If display_winners is true we are ready to calculate the winners of each pool.
            We simply go through each pool and their ballots and order them by
            highest points, then total correct, then by the oldest.
        """
        if self.display_winners:
            pools = OscarPool.objects.filter(oscar_ceremony=self)
            for pool in pools:
                ballots = pool.ballot_set.filter(pool=pool).distinct()

                if pool.how_to_win == 'points':
                    ballots = ballots.order_by('-total_points','-total_correct','last_save_date')
                elif pool.how_to_win == 'correct':
                    ballots = ballots.order_by('-total_correct', 'last_save_date')

                try:
                    pool.winner = ballots[0].member
                except:
                    pool.winner = None
                try:
                    pool.second_place_id = ballots[1].member
                except:
                    pool.second_place_id = None
                try:
                    pool.third_place_id = ballots[2].member
                except:
                    pool.third_place_id = None

                pool.save()

        super(OscarCeremony, self).save()

class BaseCategory(bmodels.Definition):
    """

    """
    ceremony = models.ForeignKey('oscars.OscarCeremony')
    nominee = models.ManyToManyField('oscars.Nominee',blank=True,help_text="Enter a year and save to see Nominees for that year only")
    winner = models.ForeignKey('oscars.Nominee',related_name="winner_set",blank=True,null=True)
    year = models.IntegerField(help_text="Year of the Award Ceremony")
    points = models.IntegerField(help_text="Default points")
    priority = models.IntegerField()

    def __unicode__(self):
        return "%s - %s" % (self.name,self.year)

    def update_responses(self):
        """
            When called it goes through all the Responses tied to this Base Category,
            and determines whether they are correct or not and updates their point values.
        """
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
        """
            With each save we update all the responses related to this Category

            We also update the pools tied to Category's Oscar Ceremony and mark them as out of date.
            This tells the pools to update their all their ballots' total points the next time
            someone visits their stadings page.
        """
        self.update_responses()
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

class OscarPool(bmodels.Pool):
    """
        Each Oscar Pool is tied to an Oscar Ceremony.  It also has relationships with ballots.

        up_to_date tells the pool if it needs to update its Standings page.
    """
    entry_deadline = models.DateTimeField(null=True,blank=True,help_text="Last date pool members can submit there ballots.")
    oscar_ceremony = models.ForeignKey('oscars.OscarCeremony',null=True)
    how_to_win = models.CharField(max_length=40, choices={('points','By Accumulated Points'),('correct','By Number of Correct Picks')})
    up_to_date = models.BooleanField()

    def allow_new_picksheets(self):
        """
            If the current date and time is past the entry_deadline date and time, we close off
            the creation and edits of Ballots
        """
        if datetime.timedelta(0) > (self.entry_deadline.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return False
        return True

    @property
    def can_display_winners(self):
        """
            4 hours after the Oscar Ceremony has started.  The pool gives the okay to display the winners of the pool.
        """
        if timezone.now() > (self.oscar_ceremony.date + timedelta(hours=4)):
            return True
        return False

    def __unicode__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse("oscar_home",kwargs={'id':self.id})

    def save(self):
        """
            We default the admin_note to the initial admin welcome message.
            Should only occur when a pool is first created.
        """
        if not self.admin_note:
            self.admin_note = ohelpers.WELCOME_MESSAGE
        super(OscarPool, self).save()
        saved = True

class CustomCategory(bmodels.Definition):
    """
        Custom Categories are copies of Base categories but Custom Categories are assigned to Oscar Pools.
        The reason we don't assign Base Categories to Pools is because they are considered the Default,
        and if an Oscar Admin wants to edit the point value of a Category they will do so in their Custom Categories.
    """
    pool = models.ForeignKey('oscars.OscarPool')
    points = models.IntegerField()
    base_category = models.ForeignKey('oscars.BaseCategory',blank=True,null=True)

    class Meta:
        ordering = ['base_category__priority']

class Ballot(models.Model):
    """
        Ballots are what pool members create to make their guess on who will win each Category.
        Ballots are tied to Oscar Pools, the member that created the ballot, and Responses that hold each
        response to each category.

        Ballot total points and total correct is calculated when a Base Category is saved and
        a winner was chosen for the Category.  This is done on the Base Catgeory model.
    """
    pool = models.ForeignKey('oscars.OscarPool')
    name = models.CharField("Name of Ballot",max_length=30)
    #play_off_guess = models.IntegerField("How many awards in will we have to go until they try to 'Play off' a winner's award speech?",help_text="This will be used only as a tie breaker.",null=True,blank=True);
    member = models.ForeignKey('auth.User')
    total_points = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    last_save_date = models.DateTimeField()

    def __unicode__(self):
        return "%s -- %s" % (self.member,self.name)

    def get_absolute_url(self):
        return reverse("oscar_ballot",kwargs={'id':self.pool.id,'ballot_id':self.id})

    def save(self,update_last_save=False):
        """
            If update_last_save we will update the dae this ballot was last saved on.
            This gives us an extra tie breaker by giving the older ballot an edge.
        """
        if update_last_save == True:
            self.last_save_date = timezone.now()
        super(Ballot, self).save()
        saved = True

class Response(models.Model):
    """
        Responses are tied to Ballots and Custom Categories.
        They hold a member's guess on who will win the category this Response is refering to.
    """
    ballot = models.ForeignKey('oscars.Ballot')
    category = models.ForeignKey('oscars.CustomCategory')
    predicted_winner = models.ForeignKey('oscars.Nominee')
    points = models.IntegerField(default=0)
    correct = models.NullBooleanField()

    class Meta:
        ordering = ['category__base_category__priority']
