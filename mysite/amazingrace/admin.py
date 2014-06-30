from django.contrib import admin
from mysite.amazingrace import models as amodels

class AmazingRaceSeasonAdmin(admin.ModelAdmin):
    pass

class BaseTeamAdmin(admin.ModelAdmin):
    pass

class CustomTeamAdmin(admin.ModelAdmin):
    pass

class AmazingRacePoolAdmin(admin.ModelAdmin):
    pass

class AmazingRacePickSheetAdmin(admin.ModelAdmin):
    pass

admin.site.register(amodels.AmazingRaceSeason,AmazingRaceSeasonAdmin)
admin.site.register(amodels.BaseTeam,BaseTeamAdmin)
admin.site.register(amodels.CustomTeam,CustomTeamAdmin)
admin.site.register(amodels.AmazingRacePool,AmazingRacePoolAdmin)
admin.site.register(amodels.AmazingRacePickSheet,AmazingRacePickSheetAdmin)
