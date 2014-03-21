from django.shortcuts import render,redirect
from django.contrib import messages
from django.core.urlresolvers import reverse

from mysite.base import forms as bforms
from mysite.base import models as bmodels
from django.db.models import Q

from registration.backends.default.views import ActivationView

def root(request):
    context = {}
    return render(request, "panel_core.html",context)

def signup(request,form=bforms.MemberProfileForm,addr_form=bforms.AddressForm):

    if request.POST:
        member_form = form(request.POST)
        member_addr_form = addr_form(request.POST)
        import pdb;pdb.set_trace()
        if member_form.is_valid() and member_addr_form.is_valid():
            import pdb;pdb.set_trace()
    context = {
        'form':form,
        'addr_form':addr_form,
    }
    return render(request,"signup_form.html",context)

def login(request):
    context={}
    return render(request, "login.html",context)

class CustomActivationView(ActivationView):
    def get_success_url(self, request, user):
        messages.success(request, 'You may now log in')
        return ('django.contrib.auth.views.login', (), {})

def pool_basic(request,pool=None,form=bforms.StandardBracketForm):

    if request.POST:
        pool_form = form(request.POST, instance=pool)

        if pool_form.is_valid():
            pool_record = pool_form.save(commit=False)
            pool_record.save()

            pool_record.administrator = request.user
            pool_record.save()
            return redirect(reverse("root"))

    context = {
        'form':form,
    }

    return render(request,"base/pool_form.html",context)

def your_pools(request):

    users_pools = bmodels.StandardBracket.objects.filter(Q(administrator=request.user)|Q(members=request.user)).distinct()

    context = {
        'pools':users_pools,
    }
    return render(request,"base/pool_list.html",context)