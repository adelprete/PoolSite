from django.contrib import admin
from mysite.oscars import models as omodels
from mysite.oscars import forms as oforms

# Register your models here.

class OscarCeremonyAdmin(admin.ModelAdmin):
    pass

class OscarPoolAdmin(admin.ModelAdmin):
    pass

class BaseCategoryAdmin(admin.ModelAdmin):
    form = oforms.BaseCategoryForm
    pass

class CustomCategoryAdmin(admin.ModelAdmin):
    pass

class NomineeAdmin(admin.ModelAdmin):
    pass

class ResponseAdmin(admin.ModelAdmin):
    pass

class BallotAdmin(admin.ModelAdmin):
    pass

admin.site.register(omodels.OscarCeremony,OscarCeremonyAdmin)
admin.site.register(omodels.Response,ResponseAdmin)
admin.site.register(omodels.Ballot,BallotAdmin)
admin.site.register(omodels.OscarPool,OscarPoolAdmin)
admin.site.register(omodels.BaseCategory,BaseCategoryAdmin)
admin.site.register(omodels.CustomCategory,CustomCategoryAdmin)
admin.site.register(omodels.Nominee,NomineeAdmin)