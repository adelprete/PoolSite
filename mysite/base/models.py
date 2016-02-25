from django.db import models
from django.contrib.auth.models import User
from localflavor.us.models import USStateField, PhoneNumberField
from mysite.base import helpers as bhelpers
from django.core.urlresolvers import reverse
import datetime

from mysite.base import choices as bchoices

class ActiveDefinitionManager(models.Manager):
    """Manager that only returns objects that are active"""
    def get_queryset(self):
        return super(ActiveDefinitionManager,self).get_query_set().filter(active=True)

class Definition(models.Model):
    """Very basic abstract model"""
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    objects = models.Manager()

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        ordering = ['-active','name']
        abstract = True


class Pool(models.Model):
    """This Pool Class that is used as a super class to every pool on the site."""
    administrator = models.ForeignKey('auth.User',blank=True,null=True)
    name = models.CharField(max_length=30,verbose_name='Pool Name')
    password = models.CharField("Pool password",blank=True,max_length=30,help_text="Must be 6 characters long.  Members will use this to join your pool.")
    members = models.ManyToManyField('auth.User',related_name='member_set',blank=True)
    identity = models.BigIntegerField(unique=True)
    creation_date = models.DateField()
    admin_note = models.TextField(blank=True,null=True)
    max_submissions = models.PositiveIntegerField(default=1)
    public = models.BooleanField(default=False,help_text="By making your pool public, random people will be able to join your pool.")
    max_members =  models.PositiveIntegerField(default=12)
    is_full = models.BooleanField(default=False)

    #Top 3
    winner = models.ForeignKey('auth.User',null=True,blank=True,related_name='winner_set')
    second_place = models.ForeignKey('auth.User',null=True,blank=True,related_name='second_place_set')
    third_place = models.ForeignKey('auth.User',null=True,blank=True,related_name='third_place_set')

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

        if not self.creation_date:
            self.creation_date = datetime.date.today()

        if self.id:
            if (self.members.count() + 1) == self.max_members:
                self.is_full = True
            else:
                self.is_full = False

        super(Pool, self).save()
        saved = True

class MemberProfile(models.Model):
    """
        Member profile is used to store some more information about the users
    """
    user = models.OneToOneField('auth.User',editable=False)
    first_name = models.CharField(max_length=30,blank=False)
    last_name = models.CharField(max_length=30,blank=False)
    birth_date = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=5,null=True,blank=True, choices=bchoices.GENDER)
    creation_date = models.DateField(null=True, blank=True)
    show_email = models.BooleanField("Allow other pool members to see your email address?",default=True)
    agree_to_terms = models.BooleanField("Check to Agree",
                    help_text="Do you agree to not use OfficePoolHub.com for gambling purposes and to use it \
                                purely for entertainment?",
                    default=False)
    receive_newsletter = models.BooleanField(default=True,help_text="We only send like, 2 or 3 emails a year tops.")

    line_1 = models.CharField(max_length=60,blank=True,null=True,verbose_name="Street Address")
    line_2 = models.CharField(max_length=60,blank=True,null=True,verbose_name="APT./Condo/Suite #")
    city = models.CharField(max_length=30,blank=True,null=True)
    state = USStateField(null=True,blank=True)
    zip = models.CharField(max_length=5,null=True)
    phone = PhoneNumberField(blank=True,null=True)

    def __unicode__(self):
        return "%s - %s" % (self.user.username,self.last_name)

    def get_absolute_url(self):
        return reverse("profile_stats",kwargs={'id':self.id})

    def save(self,*args,**kwargs):
        super(MemberProfile,self).save(*args,**kwargs)

class Contact(models.Model):
    """ This Contact model allows a person to contact me through the site"""
    email = models.CharField(max_length=60,blank=False)
    subject = models.CharField(max_length=60,blank=False)
    body = models.TextField(blank=False)
    creation_date = models.DateField(blank=False)

    def __unicode__(self):
        return "%s" % self.subject
