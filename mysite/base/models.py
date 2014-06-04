from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import USStateField, PhoneNumberField
from mysite.base import helpers as bhelpers
import datetime

from mysite.base import choices as bchoices

class ActiveDefinitionManager(models.Manager):
    def get_query_set(self):
        return super(ActiveDefinitionManager,self).get_query_set().filter(active=True)

class Definition(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        ordering = ['-active','name']
        abstract = True


class Pool(models.Model):
    administrator = models.ForeignKey('auth.User',blank=True,null=True)
    name = models.CharField(max_length=30,verbose_name='Pool Name')
    password = models.CharField("Pool password",max_length=30,help_text="Must be 6 characters long.  Members will use this to join your pool.")
    members = models.ManyToManyField('auth.User',related_name='member_set',blank=True,null=True)
    identity = models.BigIntegerField(unique=True)
    winner = models.IntegerField(blank=True,null=True)
    creation_date = models.DateField()
    admin_note = models.TextField(blank=True,null=True)

    def save(self):
        if not self.identity:
            try:
                identity = Pool.objects.latest('creation_date').identity + 1
                while not self.identity:
                    if Pool.objects.filter(identity=identity):
                        identity += 1
                    else:
                        self.identity = identity
            except:
                self.identity = 100
        if not self.admin_note:
            self.admin_note = bhelpers.WELCOME_MESSAGE

        if not self.creation_date:
            self.creation_date = datetime.date.today()

        super(Pool, self).save()
        saved = True

"""
class StandardBracket(Pool):
    first_round_pts = models.IntegerField(default=1,null=True,blank=True,verbose_name="First Round")
    second_round_pts = models.IntegerField(default=2,null=True,blank=True,verbose_name="Second Round")
    sweet_sixteen_pts = models.IntegerField(default=4,null=True,blank=True,verbose_name="Sweet 16")
    elite_eight_pts = models.IntegerField(default=8,null=True,blank=True,verbose_name="Elite 8")
    final_four_pts = models.IntegerField(default=16,null=True,blank=True,verbose_name="Final Four")
    national_championship_pts = models.IntegerField(default=32,null=True,blank=True,verbose_name="National Championship")
    seed_bonus = models.BooleanField(default=False,blank=True,help_text="A seed bonus is added to each round victory", verbose_name="Seed Bonus")
    multiple_brackets = models.BooleanField(default=False,blank=True,help_text="Check this box if you want to allow members of the pool to submit multiple brackets",verbose_name="Multiple Brackets")

    def __unicode__(self):
        return u'%s - %s' % (self.identity, self.name)

    def save(self):
        if not self.identity:
            try:
                self.identity = StandardBracket.objects.latest('entry_date').identity + 1
            except:
                self.identity = 100

        if not self.entry_date:
            self.entry_date = datetime.date.today()

        super(Pool, self).save()
        saved = True
"""

class MemberProfile(models.Model):
    user = models.OneToOneField('auth.User',editable=False)
    first_name = models.CharField(max_length=30,blank=False)
    last_name = models.CharField(max_length=30,blank=False)
    birth_date = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=5,null=True,blank=True, choices=bchoices.GENDER)
    creation_date = models.DateField(null=True, blank=True)
    address = models.OneToOneField('base.Address',editable=False,)

    def save(self,*args,**kwargs):

        super(MemberProfile,self).save(*args,**kwargs)

class Address(models.Model):
    line_1 = models.CharField(max_length=60,blank=True,null=True,verbose_name="Street Address")
    line_2 = models.CharField(max_length=60,blank=True,null=True,verbose_name="APT./Condo/Suite #")
    city = models.CharField(max_length=30,blank=True,null=True)
    state = USStateField(blank=True,null=True)
    zip = models.CharField(max_length=5,blank=True,null=True)
    phone = PhoneNumberField()
