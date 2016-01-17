import datetime
from django import forms
from mysite.oscars import models as omodels
from mysite.base import forms as bforms
from django.forms.fields import DateField, DateTimeInput
from datetimewidget.widgets import DateTimeWidget

dateTimeOptions={'showMeridian':'true'}


class OscarPoolForm(forms.ModelForm):

    entry_deadline = forms.DateTimeField(
        widget=DateTimeWidget(attrs={'id':"entry_deadline_id"},options={'showMeridian':'true'},usel10n = True),
        help_text="This is the last date and time pool members can submit or edit their ballots.",
        required=False
    )

    def __init__(self,*args,**kwargs):
        super(OscarPoolForm,self).__init__(*args,**kwargs)
        self.fields['name'].error_messages = {'required':'Required'}
        self.fields['password'].error_messages = {'required':'Required'}
        self.fields['entry_deadline'].error_messages = {'required':'Required'}
        self.fields['max_submissions'].help_text = "This is the max number of ballots each member may submit"

    def clean_entry_deadline(self):
        data = self.cleaned_data['entry_deadline']
        if self.instance.id:
            if datetime.timedelta(0) > (self.instance.oscar_ceremony.date - data):
                raise forms.ValidationError("You can't have an entry deadline past the start of the Oscar Ceremony")
        else:
            ceremony = omodels.OscarCeremony.objects.latest('date')

            if datetime.timedelta(0) > (ceremony.date - data):
                raise forms.ValidationError("You can't have an entry deadline past the start of the Oscar Ceremony")
        return data

    def clean_max_submissions(self):
        data = self.cleaned_data['max_submissions']
        if data <= 0:
            raise forms.ValidationError("Max submissions cannot be 0")
        return data

    def clean(self):
        cleaned_data = super(OscarPoolForm, self).clean()

        if cleaned_data.get('public') == False:
            if cleaned_data.get('password').__len__() < 6:
                self._errors["password"] = self.error_class(["The password must be at least 6 characters long"])
            elif (' ' in cleaned_data.get('password')) == True:
                self._errors['password'] = self.error_class(["There cannot be any spaces in the password"])

        return cleaned_data

    class Meta:
        model = omodels.OscarPool
        exclude = {'winner','categories','identity','creation_date','oscar_ceremony','admin_note'}

class AdminMessageForm(forms.ModelForm):

    class Meta:
        model = omodels.OscarPool
        fields = {'admin_note'}


class CustomCategoryForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        super(CustomCategoryForm,self).__init__(*args,**kwargs)
        from django.utils import timezone
        if self.instance.id:
            if timezone.now() > self.instance.pool.oscarpool.oscar_ceremony.date:
                pass

        self.fields['points'].widget.attrs['style'] = "width:60px"

    class Meta:
        model = omodels.CustomCategory
        exclude = {'base_category','pool','pool_id'}

class BallotForm(forms.ModelForm):

    def __init__(self,allow_new_ballots,*args,**kwargs):
        super(BallotForm,self).__init__(*args,**kwargs)
        if allow_new_ballots == False:
            self.fields['name'].widget.attrs['disabled'] = 'disabled'

    class Meta:
        model = omodels.Ballot
        exclude = {'pool','member','total_points','total_correct','play_off_guess','last_save_date'}

class BaseCategoryForm(forms.ModelForm):

    def __init__(self,category,allow_new_ballots,*args,**kwargs):
        super(ResponseForm,self).__init__(*args,**kwargs)

    def __init__(self,*args,**kwargs):
        super(BaseCategoryForm,self).__init__(*args,**kwargs)
        if self.instance.year:
            self.fields['nominee'] = forms.ModelMultipleChoiceField(
                    queryset=omodels.Nominee.objects.filter(year=self.instance.year))
        self.fields['nominee'].widget.attrs = {"size":200}
        
    class Meta:
        model = omodels.BaseCategory


class ResponseForm(forms.ModelForm):

    def __init__(self,category,allow_new_ballots,*args,**kwargs):
        super(ResponseForm,self).__init__(*args,**kwargs)
        self.category = category
        nominees = category.base_category.nominee.all()

        self.fields['predicted_winner'] = forms.ModelChoiceField(
            queryset=nominees,
            empty_label=None,
            widget=forms.RadioSelect)

        if allow_new_ballots == False:
            self.fields['predicted_winner'].widget.attrs['disabled'] = 'disabled'

    class Meta:
        model = omodels.Response
        exclude = {'ballot','category','points','correct'}

class OscarCeremonyForm(forms.ModelForm):
    class Meta:
        model = omodels.OscarCeremony
