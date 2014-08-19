from django.contrib import admin
from mysite.nflsurvivor import models as nflsmodels

class NFLSurvivorPoolAdmin(admin.ModelAdmin):
    pass

class MatchupAdmin(admin.ModelAdmin):
    pass

class PickSheetAdmin(admin.ModelAdmin):
    pass

admin.site.register(nflsmodels.Matchup,MatchupAdmin)
admin.site.register(nflsmodels.NFLSurvivorPool,NFLSurvivorPoolAdmin)
admin.site.register(nflsmodels.PickSheet,PickSheetAdmin)
