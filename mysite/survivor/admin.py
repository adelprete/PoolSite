from django.contrib import admin
from mysite.survivor import models as smodels

class SurvivorSeasonAdmin(admin.ModelAdmin):
    pass

class BaseCastawayAdmin(admin.ModelAdmin):
    pass

class CustomCastawayAdmin(admin.ModelAdmin):
    pass

class SurvivorPoolAdmin(admin.ModelAdmin):
    pass

class SurvivorPickSheetAdmin(admin.ModelAdmin):
    pass

admin.site.register(smodels.SurvivorSeason,SurvivorSeasonAdmin)
admin.site.register(smodels.BaseCastaway,BaseCastawayAdmin)
admin.site.register(smodels.CustomCastaway,CustomCastawayAdmin)
admin.site.register(smodels.SurvivorPool,SurvivorPoolAdmin)
admin.site.register(smodels.SurvivorPickSheet,SurvivorPickSheetAdmin)