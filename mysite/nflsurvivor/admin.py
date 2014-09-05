from django.contrib import admin
from mysite.nflsurvivor import models as nflsmodels

class NFLSurvivorPoolAdmin(admin.ModelAdmin):

    def total_members(obj):
        return obj.members.count() + 1

    def total_picksheets(obj):
        return obj.picksheet_set.count()

    list_display = ['name','administrator',total_members,total_picksheets]
    ordering = ['name','administrator']

class MatchupAdmin(admin.ModelAdmin):
    pass

class PickSheetAdmin(admin.ModelAdmin):
    list_display = ['name','total_points','still_alive']
    ordering = ['name','total_points','still_alive']

admin.site.register(nflsmodels.Matchup,MatchupAdmin)
admin.site.register(nflsmodels.NFLSurvivorPool,NFLSurvivorPoolAdmin)
admin.site.register(nflsmodels.PickSheet,PickSheetAdmin)
