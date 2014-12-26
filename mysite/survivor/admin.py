from django.contrib import admin
from mysite.survivor import models as smodels

class SurvivorSeasonAdmin(admin.ModelAdmin):
    pass

class BaseCastawayAdmin(admin.ModelAdmin):
    pass

class CustomCastawayAdmin(admin.ModelAdmin):
    pass

class SurvivorPoolAdmin(admin.ModelAdmin):

    def total_members(obj):
        return obj.members.count() + 1

    def total_picksheets(obj):
        return obj.survivorpicksheet_set.count()

    list_display = ['name','administrator',total_members,total_picksheets]
    ordering = ['name','administrator']

class SurvivorPickSheetAdmin(admin.ModelAdmin):
    list_display = ['member','name','survivor_pool','total_points']
    ordering = ['member','name','survivor_pool','total_points']

admin.site.register(smodels.SurvivorSeason,SurvivorSeasonAdmin)
admin.site.register(smodels.BaseCastaway,BaseCastawayAdmin)
admin.site.register(smodels.CustomCastaway,CustomCastawayAdmin)
admin.site.register(smodels.SurvivorPool,SurvivorPoolAdmin)
admin.site.register(smodels.SurvivorPickSheet,SurvivorPickSheetAdmin)