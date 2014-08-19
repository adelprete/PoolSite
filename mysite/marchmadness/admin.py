from django.contrib import admin
from mysite.marchmadness import models as mmodels
# Register your models here.

class BracketAdmin(admin.ModelAdmin):
    pass

admin.site.register(mmodels.Bracket,BracketAdmin)