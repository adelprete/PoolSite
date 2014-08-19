from django.shortcuts import get_object_or_404,render,redirect
from mysite.marchmadness import models as mmodels
from mysite.marchmadness import forms as mforms
from django.core.urlresolvers import reverse

# Create your views here.
def pool_bracket(request,bracket_id=None):

    bracket = None

    if bracket_id:
        bracket = get_object_or_404(mmodels.Bracket,id=bracket_id)

    bracket_form = mforms.BracketForm(instance=bracket)

    if request.POST:
        bracket_form = mforms.BracketForm(request.POST,instance=bracket)
        if bracket_form.is_valid():
            bracket_record = bracket_form.save()
            return redirect(bracket_record.get_absolute_url())

    context = {
        'form':bracket_form,
    }

    return render(request,'marchmadness/bracket_form.html',context)
