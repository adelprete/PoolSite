from django import forms
from mysite.base import models as bmodels
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField


"""
class StandardBracketForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput,help_text="This Password will be used for new members to join the pool.  Must be 6 characters long.")
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def __init__(self,*args,**kwargs):
        super(StandardBracketForm,self).__init__(*args,**kwargs)
        self.fields['first_round_pts'].widget.attrs['style'] = "width:30px"
        self.fields['second_round_pts'].widget.attrs['style'] = "width:30px"
        self.fields['sweet_sixteen_pts'].widget.attrs['style'] = "width:30px"
        self.fields['elite_eight_pts'].widget.attrs['style'] = "width:30px"
        self.fields['final_four_pts'].widget.attrs['style'] = "width:30px"
        self.fields['national_championship_pts'].widget.attrs['style'] = "width:30px"

    class Meta:
        model = bmodels.StandardBracket
        exclude = {'administrator','identity','members'}
"""
class DateMaskWidget(forms.TextInput):
    def __init__(self,*args,**kwargs):
        super(DateMaskWidget,self).__init__(*args,**kwargs)
        cls = ' '.join(['date_picker input_mask date'])
        self.attrs.update({'class': cls})

class MemberProfileForm(forms.ModelForm):
    birth_date = forms.DateField(widget = DateMaskWidget(),required=False)

    def __init__(self,*args,**kwargs):
        super(MemberProfileForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'required'
        self.fields['last_name'].widget.attrs['class'] = 'required'

    class Meta:
        model = bmodels.MemberProfile
        exclude = ['user','birth_date']

class AddressForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        super(AddressForm,self).__init__(*args,**kwargs)
        self.fields['line_1'].widget.attrs['class'] = 'required'
        self.fields['line_2'].widget.attrs['class'] = 'required'
        self.fields['city'].widget.attrs['class'] = 'required'
        self.fields['state'].widget.attrs['class'] = 'required'
        self.fields['zip'].widget.attrs['class'] = 'required'
        self.fields['phone'].widget.attrs['class'] = 'required'


    class Meta:
        model = bmodels.Address

class JoinForm(forms.Form):
    pool_id = forms.IntegerField()
    password = forms.CharField(widget=forms.PasswordInput())

