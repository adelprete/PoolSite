import datetime
from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

from mysite.base import forms as bforms
from mysite.base import models as bmodels
from mysite.oscars import models as omodels
from mysite.survivor import models as smodels
from mysite.amazingrace import models as amodels

from django.db.models import Q

from registration.backends.default.views import ActivationView
from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail

class RegistrationViewUniqueEmail(RegistrationView):
    form_class = RegistrationFormUniqueEmail

def root(request):
    context = {}
    return render(request, "panel_core.html",context)


def signup(request,form=bforms.MemberProfileForm,addr_form=bforms.AddressForm):

    if request.POST:
        member_form = form(request.POST)
        member_addr_form = addr_form(request.POST)
        if member_form.is_valid() and member_addr_form.is_valid():
            member_profile_record = member_form.save(commit=False)
            member_addr_record = member_addr_form.save()
            member_profile_record.address = member_addr_record
            member_profile_record.creation_date = datetime.datetime.utcnow()
            member_profile_record.save()
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

    profile_form = form_class(instance=profile)
    addr_form = addr_class(instance=address)

    if request.POST:
        profile_form = form_class(request.POST,instance=profile)
        if profile_form.is_valid():
            profile_record = profile_form.save(commit=False)
            profile_record.user = request.user
            profile_record.creation_date = datetime.datetime.utcnow()
            profile_record.save()

            messages.success(request,"Thank you for Signing Up!")
            send_mail('New Member!', 'A new member by the name of '+profile_record.user.username+' has joined the site.  Go say something!','officepoolhub@gmail.com',
                      ['adelprete87@gmail.com'], fail_silently=False)
            return redirect(reverse("root"))

    context = {
        'form':profile_form,
        'addr_form':addr_form,
    }

    return render(request,template,context)

def your_pools(request):

    if request.user.is_anonymous():
        messages.error(request,"Please log in first")
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))

    #Oscar Pools
    if omodels.OscarCeremony.objects.all().count() == 0:
        cur_oscar_pools = False
        old_oscar_pools = False
    else:
        current_oscar_ceremony = omodels.OscarCeremony.objects.latest('date')
        cur_oscar_pools = omodels.OscarPool.objects.filter(Q(administrator=request.user)|Q(members=request.user),oscar_ceremony=current_oscar_ceremony).distinct()
        old_oscar_pools = omodels.OscarPool.objects.filter(Q(administrator=request.user)|Q(members=request.user)).exclude(oscar_ceremony=current_oscar_ceremony).distinct()

    #Survivor Pools
    if smodels.SurvivorSeason.objects.all().count() == 0:
        cur_survivor_pools = False
        old_survivor_pools = False
    else:
        current_survivor_season = smodels.SurvivorSeason.objects.latest('start_date')
        cur_survivor_pools = smodels.SurvivorPool.objects.filter(Q(administrator=request.user)|Q(members=request.user),season=current_survivor_season).distinct()
        old_survivor_pools = smodels.SurvivorPool.objects.filter(Q(administrator=request.user)|Q(members=request.user)).exclude(season=current_survivor_season).distinct()

    #Amazing Race Pools
    if amodels.AmazingRaceSeason.objects.all().count() == 0:
        cur_amazingrace_pools = False
        old_amazingrace_pools = False
    else:
        current_amazingrace_season = amodels.AmazingRaceSeason.objects.latest('start_date')
        cur_amazingrace_pools = amodels.AmazingRacePool.objects.filter(Q(administrator=request.user)|Q(members=request.user),season=current_amazingrace_season).distinct()
        old_amazingrace_pools = amodels.AmazingRacePool.objects.filter(Q(administrator=request.user)|Q(members=request.user)).exclude(season=current_amazingrace_season).distinct()


    context = {
        'cur_oscar_pools':cur_oscar_pools,
        'old_oscar_pools':old_oscar_pools,
        'cur_survivor_pools':cur_survivor_pools,
        'old_survivor_pools':old_survivor_pools,
        'cur_amazingrace_pools':cur_amazingrace_pools,
        'old_amazingrace_pools':old_amazingrace_pools,
    }

    return render(request,"base/pool_list.html",context)

@login_required
def join_pool(request, id=None, password=None):

    if id and password:
        messages.info(request,"Enter " + id + " for the Pool id, and " + password + " for the password.")

    form = bforms.JoinForm(request.POST or None)
    pool = None
    if form.is_valid():

        try:
            pool = bmodels.Pool.objects.get(identity=form.cleaned_data['pool_id'])
        except:
            messages.error(request,"Pool id did not match any pools in our system. Please try again")

        if pool:
            if pool.password == form.cleaned_data['password']:
                if pool.administrator != request.user and request.user not in pool.members.all():
                    pool.members.add(request.user)
                    messages.success(request,"You've successfully joined the pool!")
                    if hasattr(pool,"oscarpool"):
                        pool = pool.oscarpool
                        return HttpResponseRedirect(pool.get_absolute_url())
                    if hasattr(pool,"survivorpool"):
                        pool = pool.survivorpool
                        return HttpResponseRedirect(pool.get_absolute_url())
                    if hasattr(pool,"amazingracepool"):
                        pool = pool.amazingracepool
                        return HttpResponseRedirect(pool.get_absolute_url())
                else:
                    messages.error(request,"You are already in this pool")
            else:
                messages.error(request,"Pool id and Password given do not match any pools. Please try again")

    return render(request,'join_form.html', {'form':form})

@login_required
def leave_pool(request,id):

    pool = get_object_or_404(bmodels.Pool,id=id)

    if request.user != pool.administrator:
        pool.members.remove(request.user)
        if hasattr(pool,"oscarpool"):
            pool.oscarpool.ballot_set.filter(member=request.user).delete()
        if hasattr(pool,"survivorpool"):
            pool.survivorpool.survivorpicksheet_set.filter(member=request.user).delete()
        messages.success(request,"You have been removed from the pool")
        return HttpResponseRedirect(reverse("root"))
    else:
        messages.error(request,"You cannot leave your own pool.  If you want to delete the pool, go to 'Settings'")

    return HttpResponseRedirect(reverse("pool_members",kwargs={'id':pool.id}))

def contact(request, form=bforms.ContactForm):

    if request.POST:
        form = form(request.POST)
        if form.is_valid():
            contact_record = form.save(commit=False)
            contact_record.creation_date = datetime.datetime.utcnow()
            contact_record.save()
            messages.success(request,"Thank You. We have received your message.")
            send_mail('New Contact', 'Someone left us a message in the contact section','officepoolhub@gmail.com',
                      ['adelprete87@gmail.com'], fail_silently=False)

    context = {
        "form":form,
    }
    return render(request,'base/contact.html',context)
