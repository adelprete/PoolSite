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

    def __init__(self,*args,**kwargs):
        super(SurvivorPoolForm,self).__init__(*args,**kwargs)
        self.fields['max_submissions'].help_text = "This is the max number of pick sheets each member may submit"

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

    def clean_max_submissions(self):
        data = self.cleaned_data['max_submissions']
        if data <= 0:
            raise forms.ValidationError("Max submissions cannot be 0")
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
        self.fields["four_picks"].queryset = smodels.CustomCastaway.objects.filter(survivor_pool=self.pool)

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
        exclude = {'member','survivor_pool','total_points'}

class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.base_castaway.first_name

class SurvivorStatsForm(forms.Form):
    castaways = MyModelChoiceField(queryset=smodels.CustomCastaway.objects.all(),empty_label=None)
    def __init__(self,castaways,*args,**kwargs):
        #castaway = forms.ChoiceField(choices=smodels.BaseCastaways.objects.all())
        super(SurvivorStatsForm,self).__init__(*args,**kwargs)
        self.fields['castaways'].queryset = castaways
        self.fields['castaways'].widget.attrs = {'style':'width:100px;'}

class AdminMessageForm(forms.ModelForm):

    class Meta:
        model = smodels.SurvivorPool
        fields = {'admin_note'}
