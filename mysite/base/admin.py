from django.contrib import admin
from mysite.base import models as bmodels

admin.site.register(bmodels.StandardBracket)
admin.site.register(bmodels.MemberProfile)


# Register your models here.
