import datetime
from mysite.nflsurvivor import models as nflsmodels
from mysite.nflbase import models as nflbmodels
from django import forms
from datetimewidget.widgets import DateTimeWidget

class NFLSurvivorPoolForm(forms.ModelForm):

    entry_deadline = forms.DateTimeField(
        widget=DateTimeWidget(attrs={'id':"entry_deadline_id"},options={'showMeridian':'true'},usel10n = True),
        help_text="This is the last date and time pool members can submit or edit their ballots.",
        required=False
    )

    def __init__(self,*args,**kwargs):
        super(NFLSurvivorPoolForm,self).__init__(*args,**kwargs)
        self.fields['max_submissions'].help_text = "This is the max number of pick sheets each member may submit"

        season = nflbmodels.Season.objects.latest('start_date')

        if datetime.timedelta(0) > (season.start_date.replace(tzinfo=None) - datetime.datetime.utcnow()):
            self.fields['start_week'].choices = [(u'','---------'),('wk2','Week 2')]

    def clean_max_members(self):
        data = self.cleaned_data['max_members']
        if data <= 0:
            raise forms.ValidationError("The max amount of members must be higher than 0")
        return data

    def clean_max_submissions(self):
        data = self.cleaned_data['max_submissions']
        if data <= 0:
            raise forms.ValidationError("Max submissions cannot be 0")
        return data

    def clean(self):
        cleaned_data = super(NFLSurvivorPoolForm, self).clean()

        if cleaned_data.get('public') == False:
            if cleaned_data.get('password').__len__() < 6:
                self._errors["password"] = self.error_class(["The password must be at least 6 characters long"])
            elif (' ' in cleaned_data.get('password')) == True:
                self._errors['password'] = self.error_class(["There cannot be any spaces in the password"])

        if cleaned_data.get('start_week') == 'wk1':
            season = nflbmodels.Season.objects.latest('start_date')
            if datetime.timedelta(0) > (season.start_date - cleaned_data.get('entry_deadline')):
                self._errors['entry_deadline'] = self.error_class(["Because you are starting on Week 1, you can't have an entry deadline past the start of Week 1"])
        elif cleaned_data.get('start_week') == 'wk2':
            season = nflbmodels.Season.objects.latest('start_date')
            if datetime.timedelta(0) > (season.start_date2 - cleaned_data.get('entry_deadline')):
                self._errors['entry_deadline'] = self.error_class(["Because you are starting on Week 2, you can't have an entry deadline past the start of Week 2"])

        return cleaned_data

    class Meta:
        model = nflsmodels.NFLSurvivorPool
        exclude = {'season','identity','is_full','creation_date'}

class PickSheetForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        super(PickSheetForm,self).__init__(*args,**kwargs)

        try:
            if self.instance and not self.instance.survivor_pool.allow_new_picksheets():
                del self.fields['name']
        except:
            pass

    def clean(self):
        cleaned_data = super(PickSheetForm, self).clean()

        if self.instance.id and 'team' in self.data and 'clear' not in self.data:
            picksheet = nflsmodels.PickSheet.objects.get(id=self.instance.id)

            picks = []
            for week in range(1,18):
                picks.append(getattr(picksheet,'week'+str(week)))

            if self.data['team'] in picks:
                raise forms.ValidationError('You have already chosen this team')

        return cleaned_data

    class Meta:
        model = nflsmodels.PickSheet
        exclude = {'member','survivor_pool','total_points','still_alive','week1','week2','week3','week4','week5','week6'
        ,'week7','week8','week9','week10','week11','week12','week13','week14','week15','week16'
        ,'week17'}

class AdminMessageForm(forms.ModelForm):

    class Meta:
        model = nflsmodels.NFLSurvivorPool
        fields = {'admin_note'}