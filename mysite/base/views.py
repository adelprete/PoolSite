from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from mysite.base import forms as bforms
from mysite.base import models as bmodels
from mysite.oscars import models as omodels
from mysite.survivor import models as smodels

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

def profile_basics(request,id=None,form_class=bforms.MemberProfileForm,addr_class=bforms.AddressForm):

    template = "profile.html"
    profile = None
    address = None

    if id:
        profile = get_object_or_404(bmodels.MemberProfile,id=id)
        address = profile.address

    if request.POST:
        profile_form = form_class(request.POST,instance=profile)
        address_form = addr_class(request.POST,instance=address)

        if profile_form.is_valid() and address_form.is_valid():
            profile_record = profile_form.save(commit=False)
            profile_record.address = address_form.save()
            profile_record.user = request.user
            profile_record.save()

            messages.success(request,"Thank you for Signing Up!")
            return redirect(reverse("root"))


    profile_form = form_class(instance=profile)
    addr_form = addr_class(instance=address)

    context = {
        'form':profile_form,
        'addr_form':addr_form,
    }

    return render(request,template,context)

def your_pools(request):

    if request.user.is_anonymous():
        messages.error(request,"Please log in first")
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))

    current_oscar_ceremony = omodels.OscarCeremony.objects.latest('date')
    cur_oscar_pools = omodels.OscarPool.objects.filter(Q(administrator=request.user)|Q(members=request.user),oscar_ceremony=current_oscar_ceremony).distinct()
    old_oscar_pools = omodels.OscarPool.objects.filter(Q(administrator=request.user)|Q(members=request.user)).exclude(oscar_ceremony=current_oscar_ceremony).distinct()

    current_survivor_season = smodels.SurvivorSeason.objects.latest('start_date')
    cur_survivor_pools = smodels.SurvivorPool.objects.filter(Q(administrator=request.user)|Q(members=request.user),season=current_survivor_season).distinct()
    old_survivor_pools = smodels.SurvivorPool.objects.filter(Q(administrator=request.user)|Q(members=request.user)).exclude(season=current_survivor_season).distinct()

    context = {
        'cur_oscar_pools':cur_oscar_pools,
        'old_oscar_pools':old_oscar_pools,
        'cur_survivor_pools':cur_survivor_pools,
        'old_survivor_pools':old_survivor_pools,
    }

    return render(request,"base/pool_list.html",context)

def join_pool(request):

    if request.user.is_anonymous():
        messages.error(request,"Please log in first")
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))

    form = bforms.JoinForm(request.POST or None)

    if form.is_valid():

        pool = get_object_or_404(bmodels.Pool,identity=form.cleaned_data['pool_id'])

        if pool.password == form.cleaned_data['password']:
            pool.members.add(request.user)
            messages.success(request,"You've successfully joined the pool!")
            if hasattr(pool,"oscarpool"):
                pool = pool.oscarpool
                return HttpResponseRedirect(pool.get_absolute_url())
        messages.error(request,"Either the ID and Password given do not match.")

    return render(request,'join_form.html', {'form':form})