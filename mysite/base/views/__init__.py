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
from mysite.nflsurvivor import models as nflsmodels
from mysite.nflbase import models as nflbmodels
from mysite.marchmadness import models as mmodels


from django.db.models import Q

from registration.backends.default.views import ActivationView
from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail

#Angular views
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from mysite.base.serializers import UserSerializer


@api_view(['GET'])
def current_user(request):
    user = request.user
    return Response({'username': user.username})

class UserList(generics.ListCreateAPIView):
    model = User
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]

class UserDetail(generics.RetrieveAPIView):
    model = User
    serializer_class = UserSerializer
    lookup_field = 'username'
    queryset = User.objects.all()
#End of Angular Views

class RegistrationViewUniqueEmail(RegistrationView):
    form_class = RegistrationFormUniqueEmail

def signup(request,form=bforms.MemberProfileForm):

    if request.POST:
        member_form = form(request.POST)
        if member_form.is_valid():
            member_profile_record = member_form.save(commit=False)
            member_profile_record.creation_date = datetime.datetime.utcnow()
            member_profile_record.save()
    context = {
        'form':form,
    }
    return render(request,"signup_form.html",context)

def login(request):
    context={}
    return render(request, "login.html",context)

class CustomActivationView(ActivationView):
    def get_success_url(self, request, user):
        messages.success(request, 'You may now log in')
        return ('django.contrib.auth.views.login', (), {})

def profile_basics(request,id=None,form_class=bforms.MemberProfileForm):

    template = "profile.html"
    profile = None
    address = None

    if id:
        profile = get_object_or_404(bmodels.MemberProfile,id=id)
        if request.user != profile.user:
            return HttpResponseRedirect(reverse("root"))

    profile_form = form_class(instance=profile,initial={'receive_information':True})

    if request.POST:
        profile_form = form_class(request.POST,instance=profile)
        if profile_form.is_valid():
            profile_record = profile_form.save(commit=False)
            if profile == None:
                profile_record.user = request.user
            profile_record.creation_date = datetime.datetime.utcnow()
            profile_record.save()

            if profile == None:
                messages.success(request,"Thank you for Signing Up!")
                send_mail('New Member!', 'A new member by the name of '+profile_record.user.username+' has joined the site.  Go say something!','admin@oscarpoolhub.com',
                          ['adelprete87@gmail.com'], fail_silently=False)
                return redirect(reverse("root"))

            messages.success(request,"Profile Saved")

    context = {
        'form':profile_form,
        'profile':profile,
    }

    return render(request,template,context)

def profile_stats(request,id=None):

    if id:
        profile = get_object_or_404(bmodels.MemberProfile,id=id)

    member = profile.user

    history={}
    survivorpools = smodels.SurvivorPool.objects.filter(Q(administrator=member)|Q(members=member)).distinct()
    history['Survivor'] = (survivorpools.filter(winner=member).count(),survivorpools.filter(second_place=member).count(),survivorpools.filter(third_place=member).count())

    oscarpools = omodels.OscarPool.objects.filter(Q(administrator=member)|Q(members=member)).distinct()
    history['Oscars'] = (oscarpools.filter(winner=member).count(),oscarpools.filter(second_place=member).count(),oscarpools.filter(third_place=member).count())

    amazingpools = amodels.AmazingRacePool.objects.filter(Q(administrator=member)|Q(members=member)).distinct()
    history['Amazing Race'] = (amazingpools.filter(winner=member).count(),amazingpools.filter(second_place=member).count(),amazingpools.filter(third_place=member).count())

    nflpools = nflsmodels.NFLSurvivorPool.objects.filter(Q(administrator=member)|Q(members=member)).distinct()
    history['NFL Survivor'] = (nflpools.filter(winner=member).count(),nflpools.filter(second_place=member).count(),nflpools.filter(third_place=member).count())

    marchpools = mmodels.MarchMadnessPool.objects.filter(Q(administrator=member)|Q(members=member)).distinct()
    history['March Madness'] = (marchpools.filter(winner=member).count(),marchpools.filter(second_place=member).count(),marchpools.filter(third_place=member).count())


    totals = {'first_total':0,'second_total':0,'third_total':0}
    for key,value in history.iteritems():
        totals['first_total'] += value[0]

    for key,value in history.iteritems():
        totals['second_total'] += value[1]

    for key,value in history.iteritems():
        totals['third_total'] += value[2]

    return render(request,"profile_stats.html",{"history":history,"member":member,"totals":totals})

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
    context = {
        'cur_oscar_pools':cur_oscar_pools,
        'old_oscar_pools':old_oscar_pools,
    }

    return render(request,"base/pool_list.html",context)

def join_pool(request, id=None, password=None):

    if id and password:
        messages.info(request,"Enter " + id + " for the Pool id, and " + password + " for the password to join their pool")
    elif id and not password:
        messages.info(request,"Enter " + id + " for the Pool id, and leave the password field blank to join their pool")

    form = bforms.JoinForm(request.POST or None)
    pool = None

    if request.POST:

        if request.user.is_anonymous():
            messages.error(request,"You have to be logged in to join a pool")

        elif form.is_valid():

            try:
                pool = bmodels.Pool.objects.get(identity=form.cleaned_data['pool_id'])
            except:
                messages.error(request,"Pool id did not match any pools in our system. Please try again")

            if pool:

                if pool.public or pool.password == form.cleaned_data['password']:
                    if pool.administrator == request.user:
                        messages.error(request, "Unable to join. You are the admin of the pool.")
                    elif request.user in pool.members.all():
                        messages.error(request, "You've already joined this pool.")
                    elif pool.paid == False:
                        messages.error(request, "The Admin hasn't paid for this pool yet.")
                    elif pool.members.count()+1 == pool.max_members:
                        messages.error(request, "The pool you are trying to join is full.")
                    else:
                        pool.members.add(request.user)
                        messages.success(request,"You've successfully joined the pool!")
                        if hasattr(pool,"oscarpool"):
                            pool = pool.oscarpool
                        return HttpResponseRedirect(pool.get_absolute_url())
                else:
                    messages.error(request,"Pool id and Password given do not match any pools. Please try again")

    return render(request,'join_form.html', {'form':form})


class PublicPools(object):

    def __new__(cls, request, *args, **kwargs):
        obj = super(PublicPools,cls).__new__(cls)
        return obj(request, *args, **kwargs)

    def __call__(self,request,*args,**kwargs):

        context = {
            'title':self.get_title,
            'pools':self.get_queryset,
        }
        return render(request,'base/public_pools.html',context)

    def get_queryset(self):
        pass

    def get_title(self):
        pass

@login_required
def join_public_pool(request,id=None):
    if id:
        pool = bmodels.Pool.objects.get(identity=id)
        pool.members.add(request.user)
        pool.save()
        messages.success(request,"You've successfully joined the pool!")
        if hasattr(pool,"oscarpool"):
            pool = pool.oscarpool
        if hasattr(pool,"survivorpool"):
            pool = pool.survivorpool
        if hasattr(pool,"amazingracepool"):
            pool = pool.amazingracepool
        if hasattr(pool,"nflsurvivorpool"):
            pool = pool.nflsurvivorpool
        if hasattr(pool,"marchmadnesspool"):
            pool = pool.marchmadnesspool

        return HttpResponseRedirect(pool.get_absolute_url())
    else:
        messages.error(request,"Pool Not Found")

    return


@login_required
def leave_pool(request,id):

    pool = get_object_or_404(bmodels.Pool,id=id)

    if request.user != pool.administrator:
        pool.members.remove(request.user)
        if hasattr(pool,"oscarpool"):
            pool.oscarpool.ballot_set.filter(member=request.user).delete()
        if hasattr(pool,"survivorpool"):
            pool.survivorpool.survivorpicksheet_set.filter(member=request.user).delete()
        if hasattr(pool,"amazingracepool"):
            pool.amazingracepool.amazingracepicksheet_set.filter(member=request.user).delete()
        if hasattr(pool,"nflsurvivorpool"):
            pool.nflsurvivorpool.picksheet_set.filter(member=request.user).delete()
            pool.nflsurvivorpool.save()
        if hasattr(pool,"marchmadnesspool"):
            pool.marchmadnesspool.bracket_set.filter(member=request.user).delete()
            pool.marchmadnesspool.save()
        messages.success(request,"You have been removed from the pool")
        return HttpResponseRedirect(reverse("root"))
    else:
        messages.error(request,"You cannot leave your own pool.  If you want to delete the pool, go to 'Settings'")

    return

def contact(request, form=bforms.ContactForm):

    if request.POST:
        form = form(request.POST)
        if form.is_valid():
            contact_record = form.save(commit=False)
            contact_record.creation_date = datetime.datetime.utcnow()
            contact_record.save()
            messages.success(request,"Thank You. We have received your message.")
            send_mail('New Contact', 'Someone left us a message in the contact section','admin@oscarpoolhub.com',
                      ['adelprete87@gmail.com'], fail_silently=False)

    context = {
        "form":form,
    }
    return render(request,'base/contact.html',context)
