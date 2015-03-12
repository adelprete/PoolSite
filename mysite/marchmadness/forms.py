import datetime
from django import forms
from mysite.marchmadness import models as mmodels
from mysite.marchmadness import helpers as mhelpers
from datetimewidget.widgets import DateTimeWidget
from mysite.base import forms as bforms

class MarchMadnessPoolForm(forms.ModelForm):

    scoring_system = forms.ChoiceField(choices=[('default','Default'),('flat','Flat'),('slow_build','Slow Build'),('custom','Custom')])

    entry_deadline = forms.DateTimeField(
        widget=DateTimeWidget(attrs={'id':"entry_deadline_id"},options={'showMeridian':'true'},usel10n = True),
        help_text="This is the last date and time pool members can submit or edit their ballots.",
        required=False
    )

    def __init__(self,*args,**kwargs):
        super(MarchMadnessPoolForm,self).__init__(*args,**kwargs)
        self.fields['max_submissions'].help_text = "This is the max number of pick sheets each member may submit"
        self.fields['scoring_system'].widget.attrs['style'] = "width:110px"
        self.fields['round_1'].widget.attrs['style'] = "width:60px"
        self.fields['round_2'].widget.attrs['style'] = "width:60px"
        self.fields['round_3'].widget.attrs['style'] = "width:60px"
        self.fields['round_4'].widget.attrs['style'] = "width:60px"
        self.fields['round_5'].widget.attrs['style'] = "width:60px"
        self.fields['round_6'].widget.attrs['style'] = "width:60px"

    def clean_entry_deadline(self):
        data = self.cleaned_data['entry_deadline']
        if data:
            if self.instance.id:
                if datetime.timedelta(0) > (self.instance.season.start_date - data):
                    raise forms.ValidationError("You can't have an entry deadline past the start of the tournament")
            else:
                season = mmodels.NCAABasketballTourney.objects.latest('start_date')

                if datetime.timedelta(0) > (season.start_date - data):
                    raise forms.ValidationError("You can't have an entry deadline past the start of the tournament")
        return data

    def clean_max_submissions(self):
        data = self.cleaned_data['max_submissions']
        if data <= 0:
            raise forms.ValidationError("Max submissions cannot be 0")
        return data

    def clean(self):
        cleaned_data = super(MarchMadnessPoolForm, self).clean()

        if cleaned_data['scoring_system'] == 'default':
            cleaned_data['round_1'] = 1
            cleaned_data['round_2'] = 2
            cleaned_data['round_3'] = 4
            cleaned_data['round_4'] = 8
            cleaned_data['round_5'] = 16
            cleaned_data['round_6'] = 32
        elif cleaned_data['scoring_system'] == 'flat':
            cleaned_data['round_1'] = 1
            cleaned_data['round_2'] = 1
            cleaned_data['round_3'] = 1
            cleaned_data['round_4'] = 1
            cleaned_data['round_5'] = 1
            cleaned_data['round_6'] = 1
        elif cleaned_data['scoring_system'] == 'slow_build':
            cleaned_data['round_1'] = 1
            cleaned_data['round_2'] = 2
            cleaned_data['round_3'] = 3
            cleaned_data['round_4'] = 4
            cleaned_data['round_5'] = 6
            cleaned_data['round_6'] = 10

        if cleaned_data.get('public') == False:
            if cleaned_data.get('password').__len__() < 6:
                self._errors["password"] = self.error_class(["The password must be at least 6 characters long"])
            elif (' ' in cleaned_data.get('password')) == True:
                self._errors['password'] = self.error_class(["There cannot be any spaces in the password"])
        return cleaned_data

    class Meta:
        model = mmodels.MarchMadnessPool
        exclude = {'season','identity','creation_date'}

class BracketForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        super(BracketForm,self).__init__(*args,**kwargs)
        self.fields['B1'].widget.attrs['class']  = 'bracket_field'
        self.fields['B2'].widget.attrs['class']  = 'bracket_field'
        self.fields['B3'].widget.attrs['class']  = 'bracket_field'
        self.fields['B4'].widget.attrs['class']  = 'bracket_field'
        self.fields['B5'].widget.attrs['class']  = 'bracket_field'
        self.fields['B6'].widget.attrs['class']  = 'bracket_field'
        self.fields['B7'].widget.attrs['class']  = 'bracket_field'
        self.fields['B8'].widget.attrs['class']  = 'bracket_field'
        self.fields['B9'].widget.attrs['class']  = 'bracket_field'
        self.fields['B10'].widget.attrs['class']  = 'bracket_field'
        self.fields['B11'].widget.attrs['class']  = 'bracket_field'
        self.fields['B12'].widget.attrs['class']  = 'bracket_field'
        self.fields['B13'].widget.attrs['class']  = 'bracket_field'
        self.fields['B14'].widget.attrs['class']  = 'bracket_field'
        self.fields['B15'].widget.attrs['class']  = 'bracket_field'
        self.fields['B16'].widget.attrs['class']  = 'bracket_field'
        self.fields['B17'].widget.attrs['class']  = 'bracket_field'
        self.fields['B18'].widget.attrs['class']  = 'bracket_field'
        self.fields['B19'].widget.attrs['class']  = 'bracket_field'
        self.fields['B20'].widget.attrs['class']  = 'bracket_field'
        self.fields['B21'].widget.attrs['class']  = 'bracket_field'
        self.fields['B22'].widget.attrs['class']  = 'bracket_field'
        self.fields['B23'].widget.attrs['class']  = 'bracket_field'
        self.fields['B24'].widget.attrs['class']  = 'bracket_field'
        self.fields['B25'].widget.attrs['class']  = 'bracket_field'
        self.fields['B26'].widget.attrs['class']  = 'bracket_field'
        self.fields['B27'].widget.attrs['class']  = 'bracket_field'
        self.fields['B28'].widget.attrs['class']  = 'bracket_field'
        self.fields['B29'].widget.attrs['class']  = 'bracket_field'
        self.fields['B30'].widget.attrs['class']  = 'bracket_field'
        self.fields['B31'].widget.attrs['class']  = 'bracket_field'
        self.fields['B32'].widget.attrs['class']  = 'bracket_field'

        self.fields['C1'].widget.attrs['class']  = 'bracket_field'
        self.fields['C2'].widget.attrs['class']  = 'bracket_field'
        self.fields['C3'].widget.attrs['class']  = 'bracket_field'
        self.fields['C4'].widget.attrs['class']  = 'bracket_field'
        self.fields['C5'].widget.attrs['class']  = 'bracket_field'
        self.fields['C6'].widget.attrs['class']  = 'bracket_field'
        self.fields['C7'].widget.attrs['class']  = 'bracket_field'
        self.fields['C8'].widget.attrs['class']  = 'bracket_field'
        self.fields['C9'].widget.attrs['class']  = 'bracket_field'
        self.fields['C10'].widget.attrs['class']  = 'bracket_field'
        self.fields['C11'].widget.attrs['class']  = 'bracket_field'
        self.fields['C12'].widget.attrs['class']  = 'bracket_field'
        self.fields['C13'].widget.attrs['class']  = 'bracket_field'
        self.fields['C14'].widget.attrs['class']  = 'bracket_field'
        self.fields['C15'].widget.attrs['class']  = 'bracket_field'
        self.fields['C16'].widget.attrs['class']  = 'bracket_field'

        self.fields['D1'].widget.attrs['class']  = 'bracket_field'
        self.fields['D2'].widget.attrs['class']  = 'bracket_field'
        self.fields['D3'].widget.attrs['class']  = 'bracket_field'
        self.fields['D4'].widget.attrs['class']  = 'bracket_field'
        self.fields['D5'].widget.attrs['class']  = 'bracket_field'
        self.fields['D6'].widget.attrs['class']  = 'bracket_field'
        self.fields['D7'].widget.attrs['class']  = 'bracket_field'
        self.fields['D8'].widget.attrs['class']  = 'bracket_field'

        self.fields['E1'].widget.attrs['class']  = 'bracket_field E1'
        self.fields['E2'].widget.attrs['class']  = 'bracket_field E2'
        self.fields['E3'].widget.attrs['class']  = 'bracket_field E3'
        self.fields['E4'].widget.attrs['class']  = 'bracket_field E4'

        self.fields['F1'].widget.attrs['class']  = 'bracket_field'
        self.fields['F2'].widget.attrs['class']  = 'bracket_field'
        self.fields['champ'].widget.attrs['class']  = 'bracket_field'

        self.fields['tie_breaker_score_1'].widget.attrs['style'] = 'width:50px !important;height: 20px !important;font-size:12px;padding:0px;'
        self.fields['tie_breaker_score_2'].widget.attrs['style'] = 'width:50px !important;height: 20px !important;font-size:12px;padding:0px;text-align:right;'

        if self.instance.id:
            self.colorPredictions()

    def colorPredictions(self):
        if self.instance:
            official_bracket = mmodels.Bracket.objects.get(official_bracket=True,march_madness_pool__season=self.instance.march_madness_pool.season)
            red_teams = []
            for field in mhelpers.BRACKET_FIELDS:
                if getattr(self.instance,field) in red_teams:
                    self.fields[field].widget.attrs['style'] = 'color:red;'
                elif getattr(official_bracket,field) != '':
                    if getattr(self.instance,field) == getattr(official_bracket,field):
                        self.fields[field].widget.attrs['style'] = 'color:green;'

                    else:
                        self.fields[field].widget.attrs['style'] = 'color:red;'
                        red_teams.append(getattr(self.instance,field))

            if self.instance.champ in red_teams:
                self.fields['champ'].widget.attrs['style'] = 'color:red;'
            elif official_bracket.champ != '':
                if official_bracket.champ == self.instance.champ:
                    self.fields[field].widget.attrs['style'] = 'color:green;'
                else:
                    self.fields[field].widget.attrs['style'] = 'color:red;'

    class Meta:
        model = mmodels.Bracket
        exclude = ['march_madness_pool','member','total_points']

class AdminMessageForm(forms.ModelForm):

    class Meta:
        model = mmodels.MarchMadnessPool
        fields = {'admin_note'}