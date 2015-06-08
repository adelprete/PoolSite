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

class JoinForm(forms.Form):
    pool_id = forms.IntegerField()
    password = forms.CharField(widget=forms.PasswordInput(),required=False)

class EmailMembersForm(forms.Form):

    subject = forms.CharField(max_length=60,required=True);
    body = forms.CharField(widget=forms.Textarea)

class ContactForm(forms.ModelForm):

    class Meta:
        model = bmodels.Contact
        exclude = ['creation_date']

