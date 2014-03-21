from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import USStateField, PhoneNumberField
import datetime

from mysite.base import choices as bchoices

class Pool(models.Model):
    administrator = models.ForeignKey('auth.User',blank=True,null=True)
    entry_date = models.DateField(null=True,blank=True)
    name = models.CharField(max_length=30,null=True,blank=True,verbose_name='Pool Name')
    password = models.CharField(max_length=30,null=True,blank=True,help_text="Must be 6 characters long")
    members = models.ManyToManyField('auth.User',related_name='member_set',blank=True,null=True)
    identity = models.BigIntegerField(unique=True)

    class Meta:
        abstract=True

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
        import pdb;pdb.set_trace()
        if not self.identity:
            try:
                self.identity = StandardBracket.objects.latest('entry_date').identity + 1
            except:
                self.identity = 100

        if not self.entry_date:
            self.entry_date = datetime.date.today()

        super(Pool, self).save()
        saved = True


class MemberProfile(User):
    user = models.OneToOneField('auth.User')
    birth_date = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=5,null=True,blank=True, choices=bchoices.GENDER)
    creation_date = models.DateField(null=True, blank=True)
    address = models.OneToOneField('base.Address',editable=False,)


class Address(models.Model):
    line_1 = models.CharField(max_length=60,blank=True,null=True,verbose_name="Street Address")
    line_2 = models.CharField(max_length=60,blank=True,null=True,verbose_name="APT./Condo/Suite #")
    city = models.CharField(max_length=30,blank=True,null=True)
    state = USStateField(blank=True,null=True)
    zip = models.CharField(max_length=5,blank=True,null=True)
    phone = PhoneNumberField()
