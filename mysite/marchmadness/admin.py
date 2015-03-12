from django.contrib import admin
from mysite.marchmadness import models as mmodels
# Register your models here.

class NCAABasketballTourneyAdmin(admin.ModelAdmin):
    pass

class MarchMadnessPoolAdmin(admin.ModelAdmin):
    pass

class BracketAdmin(admin.ModelAdmin):
    pass

admin.site.register(mmodels.NCAABasketballTourney,NCAABasketballTourneyAdmin)
admin.site.register(mmodels.MarchMadnessPool,MarchMadnessPoolAdmin)
admin.site.register(mmodels.Bracket,BracketAdmin)
