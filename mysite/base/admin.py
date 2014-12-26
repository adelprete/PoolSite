from django.contrib import admin
from mysite.base import models as bmodels
from mysite.base import forms as bforms

class MemberProfileAdmin(admin.ModelAdmin):

    def last_name(obj):
        return obj.last_name
    def email(obj):
        return obj.user.email

    list_display = ['user',last_name,email,'id']
    ordering = ['user','id']

class ContactAdmin(admin.ModelAdmin):
    pass

admin.site.register(bmodels.MemberProfile,MemberProfileAdmin)
admin.site.register(bmodels.Contact,ContactAdmin)


# Register your models here.
