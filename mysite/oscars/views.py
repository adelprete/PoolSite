import datetime
import stripe
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from collections import Counter, OrderedDict
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from mysite.base import forms as bforms, models as bmodels
from mysite.base.views import pool_views as pviews
from mysite.oscars import forms as oforms, models as omodels
from mysite.oscars.decorators import paid

#Rest imports
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from mysite.oscars.models import OscarPool
from mysite.oscars.serializers import OscarPoolSerializer

# REST views start here

class OscarPoolList(generics.ListAPIView):
    model = OscarPool
    serializer_class = OscarPoolSerializer
    queryset = OscarPool.objects.all()

    def get_queryset(self):
        import pdb;pdb.set_trace()
        queryset = super(OscarPoolList, self).get_queryset()

        return queryset#.filter(Q(members=self.kwargs.get('username')))

@api_view(['GET', 'POST'])
def oscars_list(request, format=None):
    """
    List all oscar pools, or create a new pool.
    """
    if request.method == 'GET':
        pools = OscarPool.objects.all()
        serializer = OscarPoolSerializer(pools, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OscarPoolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def oscars_detail(request, pk, format=None):
    """
    Retrieve, update or delete an oscar pool.
    """
    try:
        pool = OscarPool.objects.get(pk=pk)
    except OscarPool.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OscarPoolSerializer(pool)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OscarPoolSerializer(pool, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        pool.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# end of REST views

class pool_homepage(pviews.PoolHomepage):

    template = "oscars/pool_home.html"

    def get_pool(self,id):
        return get_object_or_404(omodels.OscarPool,id=id)

@login_required
@paid
def pool_members(request,id=None):

    pool = get_object_or_404(omodels.OscarPool,id=id)

    # check if user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("root"))

    context = {
        'pool':pool,
        'join_url': request.build_absolute_uri(reverse("join_pool"))
    }
    return render(request,'oscars/members.html',context)

@login_required
@paid
def pool_ballot_list(request,id=None):

    pool = get_object_or_404(omodels.OscarPool,id=id)

    # check if user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("root"))

    ballots = pool.ballot_set.all()
    your_ballots = ballots.filter(member=request.user)
    allow_new_picksheets = True

    no_picksheets_reason = ""
    if (ballots.filter(member=request.user).count() >= pool.max_submissions):
        allow_new_picksheets = False
        no_picksheets_reason = "You have reached your maximum ballot submissions."
    if not pool.allow_new_picksheets():
        allow_new_picksheets = False
        no_picksheets_reason = "The deadline has past to enter or edit any ballots."

    context = {
        'pool':pool,
        'ballots':ballots,
        'your_ballots':your_ballots,
        'allow_new_ballots':allow_new_picksheets,
        'no_picksheets_reason': no_picksheets_reason,
    }
    return render(request,'oscars/ballots.html',context)

@login_required
@paid
def pool_ballot(request,id=None,ballot_id=None):

    pool = get_object_or_404(omodels.OscarPool,id=id)

    # check if this user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("root"))

    allow_new_picksheets = True
    if datetime.timedelta(0) > (pool.entry_deadline.replace(tzinfo=None) - datetime.datetime.utcnow()):
        allow_new_picksheets = False

    ballot=None
    response_forms=[]

    if ballot_id:
        ballot = get_object_or_404(omodels.Ballot,id=ballot_id)

    if not ballot:
        pool_categories = pool.customcategory_set.filter(active=True)

    ballot_form = oforms.BallotForm(allow_new_picksheets,instance=ballot)

    if request.POST:
        ballot_form = oforms.BallotForm(allow_new_picksheets,request.POST,instance=ballot)
        if "delete" in request.POST:
            if datetime.timedelta(0) < (ballot.pool.oscar_ceremony.date.replace(tzinfo=None) - datetime.datetime.utcnow()):
                ballot.delete()
                messages.success(request,"The Ballot was deleted")
                return HttpResponseRedirect(reverse("oscar_pool_ballots",kwargs={'id':pool.id}))
            else:
                messages.error(request,"You cannot delete ballots after the Ceremony has started")
        elif ballot_form.is_valid():
            if not ballot:
                valid_forms=True
                response_forms = []
                for category in pool_categories:
                    response_forms.append(oforms.ResponseForm(category,allow_new_picksheets,request.POST,prefix=category.name))
                for response_form in response_forms:
                    if response_form.is_valid() == False:
                        valid_forms=False;

                if valid_forms:
                    for response_form in response_forms:
                        #response_form = oforms.ResponseForm(category,request.POST,prefix=category.name)
                        if response_form.is_valid():

                            ballot_record = ballot_form.save(commit=False)
                            ballot_record.pool = pool
                            ballot_record.member = request.user
                            ballot_record.save(update_last_save=True)

                            response_record = response_form.save(commit=False)
                            response_record.category = pool_categories.get(name=response_form.prefix)
                            response_record.ballot = ballot_record
                            response_record.save()
                    if response_form.is_valid():
                        messages.success(request,"Ballot saved")
                        return HttpResponseRedirect(reverse("oscar_pool_ballots",kwargs={'id':pool.id}))
            if ballot:
                for response in ballot.response_set.all():
                    response_form = oforms.ResponseForm(response.category,allow_new_picksheets,request.POST,prefix=response.category.name,instance=response)
                    if response_form.is_valid():

                        ballot_record = ballot_form.save(commit=False)
                        ballot_record.pool = pool
                        ballot_record.member = request.user
                        ballot_record.save(update_last_save=True)

                        response_record = response_form.save(commit=False)
                        response_record.category = response.category
                        response_record.ballot = ballot_record
                        response_record.save()
                if response_form.is_valid():
                    messages.success(request,"Ballot saved")
                    return HttpResponseRedirect(reverse("oscar_pool_ballots",kwargs={'id':pool.id}))

        messages.error(request,"Ballot not saved! Please check that you've filled out every field.")

    if ballot and response_forms.__len__() == 0:
        for response in ballot.response_set.all():
            response_forms.append(oforms.ResponseForm(response.category,allow_new_picksheets,prefix=response.category.name,instance=response))
    elif response_forms.__len__() == 0:
        for category in pool_categories:
            response_forms.append(oforms.ResponseForm(category,allow_new_picksheets,prefix=category.name))

    context = {
        'pool':pool,
        'ballot':ballot,
        'ballot_form':ballot_form,
        'response_forms':response_forms,
        'allow_new_ballots':allow_new_picksheets,
    }
    return render(request,'oscars/ballot_form.html',context)


class pool_standings(pviews.PoolStandings):
    template = 'oscars/standings.html'
    ballots = None

    def __call__(self,request,*args,**kwargs):

        self.pool_instance = self.get_pool(kwargs['id'])
        self.ballots = self.pool_instance.ballot_set.all().distinct()

        if self.pool_instance.up_to_date == False:
            for ballot in self.ballots:
                ballot.total_points = 0
                ballot.total_correct = 0
                for response in ballot.response_set.all():
                    if response.category.active:
                        ballot.total_points += response.points
                        if response.correct:
                            ballot.total_correct += 1

                ballot.save()
            self.pool_instance.up_to_date = True
            self.pool_instance.save()

        if self.pool_instance.how_to_win == 'points':
            self.ballots = self.ballots.order_by('-total_points','-total_correct','last_save_date')
        else:
            self.ballots = self.ballots.order_by('-total_correct','last_save_date')

        return super(pool_standings,self).__call__(request,*args,**kwargs)

    def get_pool(self,id):
        return get_object_or_404(omodels.OscarPool,id=id)

    def get_extra_context(self):
        return {'ballots':self.ballots}


@login_required
@paid
def oscar_pool(request,id=None,form_class=oforms.OscarPoolForm,template="oscars/oscar_pool_form.html"):

    try:
        ceremony = omodels.OscarCeremony.objects.latest('date')
    except:
        messages.error(request,"Pools are Closed at this time. If you are a registered user, you will be notified when the Nominees are announced for the next award show.")
        return HttpResponseRedirect(reverse('root'))

    if not id:
        today = datetime.datetime.utcnow()
        if datetime.timedelta(0) > (ceremony.date.replace(tzinfo=None) - today) or settings.OSCARS_POOLS_OPEN is False:
            messages.error(request,"Pools are Closed at this time.  If you are a registered user, you will be notified when the Nominees are announced for next award show.")
            return HttpResponseRedirect(reverse('root'))

    pool = None
    base_categories = ceremony.basecategory_set.all().order_by('-points')
    custom_categories = None
    category_forms = []

    if id:
        pool = get_object_or_404(omodels.OscarPool,id=id)

        # check if user is admin for this pool
        if request.user != pool.administrator:
            return HttpResponseRedirect(pool.get_absolute_url())

        custom_categories = omodels.CustomCategory.objects.filter(pool=pool).order_by('base_category__priority')
    if 'delete' in request.POST:
        pool.delete()
        messages.success(request,"Pool deleted")
        return HttpResponseRedirect(reverse('root'))

    pool_form = form_class(instance=pool)

    if request.POST:
        pool_form = form_class(request.POST, instance=pool)
        if pool_form.is_valid():
            pool_record = pool_form.save(commit=False)
            if custom_categories:
                for custom in custom_categories:
                    post_values = request.POST.copy()
                    post_values[custom.name+"-name"] = custom.name
                    category_form = oforms.CustomCategoryForm(post_values,prefix=custom.name,instance=custom)
                    if category_form.is_valid():
                        category_record = category_form.save(commit=False)
                        pool_record.administrator = request.user
                        pool_record.save()
                        category_record.pool = pool_record
                        category_record.save()
                messages.success(request,"Pool Settings Saved")

                #return HttpResponseRedirect(reverse("oscar_payment",kwargs={'id':pool_record.id}))
                if pool.paid == False:
                    return HttpResponseRedirect(reverse("oscar_payment",kwargs={'id':pool_record.id}))
                return HttpResponseRedirect(pool_record.get_absolute_url())
            else:
                for base in base_categories:
                    post_values = request.POST.copy()
                    post_values[base.name+"-name"] = base.name
                    category_form = oforms.CustomCategoryForm(post_values,prefix=base.name)
                    if category_form.is_valid():
                        category_record = category_form.save(commit=False)
                        category_record.base_category = base
                        pool_record.administrator = request.user
                        pool_record.oscar_ceremony = ceremony
                        pool_record.save()
                        category_record.pool = pool_record
                        category_record.save()

                #messages.success(request,"Pool Settings Saved")
                return HttpResponseRedirect(reverse("oscar_payment",kwargs={'id':pool_record.id}))
                #return HttpResponseRedirect(pool_record.get_absolute_url())
        else:
            messages.error(request,"Pool not saved.  Check that each field is filled out correctly.")

    if not pool:
        pool_form.initial = {'entry_deadline':ceremony.date}
        for base in base_categories:
            category_forms.append(oforms.CustomCategoryForm(initial={'name':base.name, 'active':True,'points':base.points},prefix=base.name,instance=custom_categories))
    else:
        for custom in custom_categories:
            category_forms.append(oforms.CustomCategoryForm(prefix=custom.name,instance=custom))


    context = {
        'ceremony':ceremony,
        'form':pool_form,
        'pool':pool,
        'category_forms':category_forms,
    }

    return render(request,template,context)


class pool_admin_message(pviews.PoolAdminMessage):
    template = 'oscars/admin_message_form.html'
    form_class=oforms.AdminMessageForm
    def get_pool(self,id):
        return get_object_or_404(omodels.OscarPool,id=id)

@login_required
def remove_ballot(request,id,ballot_id):

    ballot = get_object_or_404(omodels.Ballot,id=ballot_id)
    pool = get_object_or_404(omodels.OscarPool,id=id)

    # check if this user is the admin in this pool
    if request.user != pool.administrator:
        return HttpResponseRedirect(pool.get_absolute_url())

    ballot.delete()

    success_str="Removed ballot from the pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("oscar_pool_ballots",kwargs={'id':pool.id}))

@login_required
def remove_member(request,id,member_id):

    member = get_object_or_404(User,id=member_id)
    pool = get_object_or_404(omodels.OscarPool,id=id)

    # check if this user is the admin in this pool
    if request.user != pool.administrator:
        return HttpResponseRedirect(pool.get_absolute_url())

    pool.members.remove(member)
    pool.ballot_set.filter(member=member).delete()
    success_str="Removed " + member.username + " from your pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("oscar_members",kwargs={'id':pool.id}))

@login_required
def predictions(request,id):

    pool = get_object_or_404(omodels.OscarPool,id=id)

    # check if this user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("root"))

    categories=OrderedDict()
    all_winners={}
    for custom_category in pool.customcategory_set.all().order_by("base_category__priority"):
        counts = Counter()
        percentages = OrderedDict()
        for nominee in custom_category.base_category.nominee.all():
            counts[nominee] = omodels.Response.objects.filter(
                ballot__pool__oscar_ceremony=pool.oscar_ceremony,
                category__name=custom_category.name,
                predicted_winner__name=nominee.name).count()
        total_responses = omodels.Response.objects.filter(
                ballot__pool__oscar_ceremony=pool.oscar_ceremony,
                category__name=custom_category.name).count()
        if total_responses == 0:
            total_responses = 1
        for key,value in counts.items():
            percentages[key] = "%.2f%%" % ((float(value)/float(total_responses))*100)
        categories[custom_category.name] = percentages

        all_winners[custom_category.name] =  custom_category.base_category.winner

    context = {
        'pool':pool,
        'predicted_results':categories,
        'winners':all_winners,
    }
    return render(request,'oscars/predictions.html',context)

from mysite.base.views import PublicPools
class OscarPublicPools(PublicPools):

    def get_title(self):
        return 'Oscar'

    def get_queryset(self):

        try:
            current_ceremony = omodels.OscarCeremony.objects.latest('date')
        except:
            current_ceremony = None

        pools = omodels.OscarPool.objects.filter(oscar_ceremony=current_ceremony,public=True).distinct()
        public_pools = [pool for pool in pools if pool.allow_new_picksheets()]

        return public_pools

@login_required
def email_members(request, id):

    pool = get_object_or_404(omodels.OscarPool,id=id)
    form = bforms.EmailMembersForm()
    # check if this user is the admin in this pool
    if request.user != pool.administrator:
        return HttpResponseRedirect(pool.get_absolute_url())

    if request.GET:
        emails = pool.members.all().values_list('email',flat=True)
        messages.success(request,"Emails Sent")
        send_mail(request.GET['subject'], 'Message from your pool administrator: \n\n'+request.GET['body'],'officepoolhub@gmail.com',
                  emails, fail_silently=False)
    context = {
        'pool':pool,
        'form':form,
    }

    return render(request,"oscars/email_members.html",context)


@login_required
def oscar_payment(request, id):

    pool = get_object_or_404(omodels.OscarPool, id=id)
    custom_categories = omodels.CustomCategory.objects.filter(pool=pool).order_by('base_category__priority')
    if request.POST:
        size = request.POST['pool_size']
        charge_amount = 0
        if size == '25':
            charge_amount = 1000
        elif size == '50':
            charge_amount = 2000
        elif size == '75':
            charge_amount = 3000
        elif size == '100':
            charge_amount = 4000
        elif size == '200':
            charge_amount = 6000

        if charge_amount:
            # Set your secret key: remember to change this to your live secret key in production
            # See your keys here https://dashboard.stripe.com/account/apikeys
            stripe.api_key = settings.STRIPE_API_KEY
            # Get the credit card details submitted by the form
            token = request.POST['stripeToken']
            # Create the charge on Stripe's servers - this will charge the user's card
            try:
              charge = stripe.Charge.create(
                  amount=charge_amount, # amount in cents, again
                  currency="usd",
                  source=token,
                  description="Oscar Pool"
              )
              pool.max_members = int(size)
              pool.paid = True
              pool.save()
              messages.success(request,"Payment Accepted")
              return HttpResponseRedirect(pool.get_absolute_url())
            except stripe.error.CardError, e:
              # The card has been declined
              messages.error(request, e.message)
        else:
            pool.max_members = 5
            pool.paid = True
            pool.save()
            messages.success(request,"Payment Accepted")
            return HttpResponseRedirect(pool.get_absolute_url())

    context = {
        "pool": pool,
        'custom_categories': custom_categories,
        'PUBLISHABLE_KEY': settings.PUBLISHABLE_KEY,
    }
    return render(request, "oscars/oscar_payment.html", context)
