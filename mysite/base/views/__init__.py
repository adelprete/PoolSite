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

from django.db.models import Q

from registration.backends.default.views import ActivationView
from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail

#Angular views
#Testing out Django rest framework to see if it could be useful
# not used anywhere on the site at the moment
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
    """
        Assigning the type of form we want to use for user registration
    """
    form_class = RegistrationFormUniqueEmail

class CustomActivationView(ActivationView):
    """
        Telss the user after activation that they are able to log in now.
    """
    def get_success_url(self, request, user):
        messages.success(request, 'You may now log in')
        return ('django.contrib.auth.views.login', (), {})

def signup(request,form=bforms.MemberProfileForm):
    """
        Brings up a blank sign up form for a new user to fill out.
        Afterwards they must verify their acount through an email sent to them.
    """
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


def profile_basics(request,id=None,form_class=bforms.MemberProfileForm):
    """
        Displays the form for updating a user's member profiles
    """
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

def profile_stats(request,id):
    """
        Displays the users stats on the site.
        Currently only displays their win record for 1st, 2nd, and 3rd.
    """
    profile = get_object_or_404(bmodels.MemberProfile,id=id)
    member = profile.user
    oscarpools = omodels.OscarPool.objects.filter(Q(administrator=member)|Q(members=member)).distinct()

    context = {
        "member":member,
        "first_place_total": oscarpools.filter(winner=member).count(),
        "second_place_total": oscarpools.filter(second_place=member).count(),
        "third_place_total": oscarpools.filter(third_place=member).count()
        }
    return render(request,"profile_stats.html",context)


def join_pool(request, id=None, password=None):
    """
        View creates the template for joining a public pool.
        To join a public pool the user can only enter its Identity
        To join a private pool, the identity and password is required.
        Page also displays a link to see a list of open public pools to join.
    """
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


def your_pools(request):
    """
        Finds the pools that the user is in.
        Seperates them out by current and past pools.
    """
    if request.user.is_anonymous():
        messages.error(request,"Please log in first")
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))


    current_oscar_ceremony = omodels.OscarCeremony.objects.latest('date')
    cur_oscar_pools = omodels.OscarPool.objects.filter(Q(administrator=request.user)|Q(members=request.user),oscar_ceremony=current_oscar_ceremony).distinct()
    old_oscar_pools = omodels.OscarPool.objects.filter(Q(administrator=request.user)|Q(members=request.user)).exclude(oscar_ceremony=current_oscar_ceremony).distinct()

    context = {
        'cur_oscar_pools':cur_oscar_pools,
        'old_oscar_pools':old_oscar_pools,
    }

    return render(request,"base/pool_list.html",context)


@login_required
def join_public_pool(request,id=None):
    """
        A view that handles joining a public pool chosen on the public pools list.
    """
    if id:
        pool = bmodels.Pool.objects.get(identity=id)
        pool.members.add(request.user)
        pool.save()
        messages.success(request,"You've successfully joined the pool!")
        return HttpResponseRedirect(pool.oscarpool.get_absolute_url())
    else:
        messages.error(request,"Pool Not Found")

    return HttpResponseRedirect(reverse("oscar_public_pools"))


@login_required
def leave_pool(request,id):
    """
        A button within each pool that allows the logged in user to leave the
        pool.  Admins of the pool can not use this view.
    """
    pool = get_object_or_404(bmodels.Pool,id=id)

    if request.user != pool.administrator:
        pool.members.remove(request.user)
        pool.oscarpool.ballot_set.filter(member=request.user).delete()
        messages.success(request,"You have been removed from the pool")
        return HttpResponseRedirect(reverse("root"))

    messages.error(request,"You cannot leave your own pool.  If you want to delete the pool, go to 'Settings'")
    return HttpResponseRedirect(reverse("oscar_members", args=(pool.id,)))

def contact(request, form=bforms.ContactForm):
    """
        Displays a blank contact form for the user to contact me.
        Im notified by email when I get new contacts.
    """
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
