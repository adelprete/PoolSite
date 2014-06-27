from django import forms
from mysite.base import models as bmodels
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField


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

    def clean_agree_to_terms(self):
        data = self.cleaned_data['agree_to_terms']
        if data == False:
            raise forms.ValidationError("This field is required")
        return data
    class Meta:
        model = bmodels.MemberProfile
        exclude = ['user','birth_date']

class MemberProfileAdminForm(forms.ModelForm):
    birth_date = forms.DateField(widget = DateMaskWidget(),required=False)

    def __init__(self,*args,**kwargs):
        super(MemberProfileAdminForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'required'
        self.fields['last_name'].widget.attrs['class'] = 'required'
        self.fields['zip'].widget.attrs['class'] = 'required'

    def clean_agree_to_terms(self):
        data = self.cleaned_data['agree_to_terms']
        if data == False:
            raise forms.ValidationError("This field is required")
        return data
    class Meta:
        model = bmodels.MemberProfile

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

class ContactForm(forms.ModelForm):

    class Meta:
        model = bmodels.Contact
        exclude = ['creation_date']

