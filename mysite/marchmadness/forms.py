from django import forms
from mysite.marchmadness import models as mmodels
from mysite.base import forms as bforms

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

    class Meta:
        model = mmodels.Bracket