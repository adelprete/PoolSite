import datetime
from django import forms
from django.db import models
from datetimewidget.widgets import DateTimeWidget
from mysite.survivor import models as smodels

class SurvivorPoolForm(forms.ModelForm):

    entry_deadline = forms.DateTimeField(
        widget=DateTimeWidget(attrs={'id':"entry_deadline_id"},options={'showMeridian':'true'},usel10n = True),
        help_text="This is the last date and time pool members can submit or edit their ballots.",
        required=False
    )

    def clean_entry_deadline(self):
        data = self.cleaned_data['entry_deadline']
        if self.instance.id:
            if datetime.timedelta(0) > (self.instance.season.start_date - data):
                raise forms.ValidationError("You can't have an entry deadline past the start of the Survivor Season")
        else:
            season = smodels.SurvivorSeason.objects.latest('start_date')

            if datetime.timedelta(0) > (season.start_date - data):
                raise forms.ValidationError("You can't have an entry deadline past the start of the Survivor Season")
        return data

    class Meta:
        model = smodels.SurvivorPool
        exclude = {'season','identity','creation_date'}

class SurvivorPickSheetForm(forms.ModelForm):
    four_picks = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=smodels.CustomCastaway.objects.all())

    def __init__(self,user,pool,*args,**kwargs):
        self.user = user
        self.pool = pool
        super(SurvivorPickSheetForm,self).__init__(*args,**kwargs)

    def clean_four_picks(self):
        data = self.cleaned_data['four_picks']

        if data.count() > 4:
            raise forms.ValidationError("Please choose only 4 casataways")
        elif data.count() < 4:
            raise forms.ValidationError("Please choose 4 castaways")

        if self.instance.id:
            picksheets = smodels.SurvivorPickSheet.objects.filter(survivor_pool=self.pool).exclude(id=self.instance.id).distinct()
        else:
            picksheets = smodels.SurvivorPickSheet.objects.filter(survivor_pool=self.pool).distinct()
        for castaway in data:
            picksheets = picksheets.filter(four_picks=castaway).distinct()

        if picksheets:
            raise forms.ValidationError("Someone has chosen that combination already.  Please choose again.")

        return data

    class Meta:
        model = smodels.SurvivorPickSheet
        exclude = {'member','survivor_pool','total_score'}