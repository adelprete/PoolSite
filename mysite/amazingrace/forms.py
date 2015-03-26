import datetime
from django import forms
from django.db import models
from datetimewidget.widgets import DateTimeWidget
from mysite.amazingrace import models as amodels

class AmazingRacePoolForm(forms.ModelForm):

    entry_deadline = forms.DateTimeField(
        widget=DateTimeWidget(attrs={'id':"entry_deadline_id"},options={'showMeridian':'true'},usel10n = True),
        help_text="This is the last date and time pool members can submit or edit their ballots.",
        required=False
    )

    def __init__(self,*args,**kwargs):
        super(AmazingRacePoolForm,self).__init__(*args,**kwargs)
        self.fields['max_submissions'].help_text = "This is the max number of pick sheets each member may submit"

    def clean_entry_deadline(self):
        data = self.cleaned_data['entry_deadline']
        if self.instance.id:
            if datetime.timedelta(0) > (self.instance.season.start_date - data):
                raise forms.ValidationError("You can't have an entry deadline past the start of the Amazing Race Season")
        else:
            season = amodels.AmazingRaceSeason.objects.latest('start_date')

            if datetime.timedelta(0) > (season.start_date - data):
                raise forms.ValidationError("You can't have an entry deadline past the start of the Amazing Race Season")
        return data

    def clean_max_submissions(self):
        data = self.cleaned_data['max_submissions']
        if data <= 0:
            raise forms.ValidationError("Max submissions cannot be 0")
        return data

    def clean(self):
        cleaned_data = super(AmazingRacePoolForm, self).clean()

        if cleaned_data.get('public') == False:
            if cleaned_data.get('password').__len__() < 6:
                self._errors["password"] = self.error_class(["The password must be at least 6 characters long"])
            elif (' ' in cleaned_data.get('password')) == True:
                self._errors['password'] = self.error_class(["There cannot be any spaces in the password"])

        return cleaned_data

    class Meta:
        model = amodels.AmazingRacePool
        exclude = {'season','identity','creation_date'}


class AmazingRacePickSheetForm(forms.ModelForm):
    picks = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=amodels.CustomTeam.objects.all())

    def __init__(self,user,pool,*args,**kwargs):
        self.user = user
        self.pool = pool
        super(AmazingRacePickSheetForm,self).__init__(*args,**kwargs)
        self.fields["picks"].queryset = amodels.CustomTeam.objects.filter(amazingrace_pool=self.pool)

    def clean_picks(self):
        data = self.cleaned_data['picks']

        if data.count() > 3:
            raise forms.ValidationError("Please choose only 3 teams")
        elif data.count() < 3:
            raise forms.ValidationError("Please choose 3 teams")

        if self.instance.id:
            picksheets = amodels.AmazingRacePickSheet.objects.filter(amazingrace_pool=self.pool).exclude(id=self.instance.id).distinct()
        else:
            picksheets = amodels.AmazingRacePickSheet.objects.filter(amazingrace_pool=self.pool).distinct()

        for team in data:
            picksheets = picksheets.filter(picks=team).distinct()

        if picksheets:
            raise forms.ValidationError("Someone has chosen that combination already.  Please choose again.")

        return data

    class Meta:
        model = amodels.AmazingRacePickSheet
        exclude = {'member','amazingrace_pool','total_points'}


class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s & %s" % (obj.base_team.team_member_1,obj.base_team.team_member_2)

class AmazingRaceStatsForm(forms.Form):
    teams = MyModelChoiceField(queryset=amodels.CustomTeam.objects.all(),empty_label=None)
    def __init__(self,teams,*args,**kwargs):
        super(AmazingRaceStatsForm,self).__init__(*args,**kwargs)
        self.fields['teams'].queryset = teams
        self.fields['teams'].widget.attrs = {'style':'width:180px;'}

class AdminMessageForm(forms.ModelForm):

    class Meta:
        model = amodels.AmazingRacePool
        fields = {'admin_note'}


