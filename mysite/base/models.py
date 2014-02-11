from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import USStateField, PhoneNumberField

class pool(models.Model):
    administrator = models.OneToOneField('auth.User')
    members = models.ManyToManyField('auth.User')

class UserProfile(User):
    user = models.OneToOneField('auth.User')
    birth_date = models.DateField(null=True,blank=True)
    creation_date = models.Datefield(null=True, blank=True)
    address = models.OneToOneField('base.Address',editable=False,)
    email = models.EmailField(max_length=50,blank=True,null=True)

class Address(models.Model):
    line_1 = models.CharField(max_length=60,blank=True,null=True,verbose_name="Address")
    line_2 = models.CharField(max_length=60,blank=True,null=True,verbose_name="APT./Condo/Suite #")
    city = models.CharField(max_length=30,blank=True,null=True)
    state = USStateField(default='FL',blank=True,null=True)
    zip = models.CharField(max_length=5,blank=True,null=True)
    phone = PhoneNumberField(blank=True,null=True)


# Create your models here.
