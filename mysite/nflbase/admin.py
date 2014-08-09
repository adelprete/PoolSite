from django.contrib import admin
from mysite.nflbase import models as nflbmodels

class SeasonAdmin(admin.ModelAdmin):
    pass

class TeamAdmin(admin.ModelAdmin):
    pass

admin.site.register(nflbmodels.Team,TeamAdmin)
admin.site.register(nflbmodels.Season,SeasonAdmin)
