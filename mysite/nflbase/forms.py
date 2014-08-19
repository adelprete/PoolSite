from django import forms
from mysite.nflbase import models as nflbmodels

class TeamForm(nflbmodels.Team):
    class Meta:
        model = nflbmodels.Team

