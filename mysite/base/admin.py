from django.contrib import admin
from mysite.base import models as bmodels
from mysite.base import forms as bforms

class MemberProfileAdmin(admin.ModelAdmin):
    pass

class ContactAdmin(admin.ModelAdmin):
    pass

admin.site.register(bmodels.MemberProfile,MemberProfileAdmin)
admin.site.register(bmodels.Contact,ContactAdmin)


# Register your models here.
