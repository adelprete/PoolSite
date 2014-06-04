import datetime
from django.utils import timezone
from collections import Counter, OrderedDict
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.forms.models import modelformset_factory
from django.forms.models import BaseModelFormSet
from django.conf import settings
from mysite.base import models as bmodels
from mysite.oscars import forms as oforms
from mysite.oscars import models as omodels

# Create your views here.
def pool_homepage(request,id=None):

    pool=None

    if id:
        pool = get_object_or_404(omodels.OscarPool,id=id)
        if request.user not in pool.members.all() and request.user != pool.administrator:
            return HttpResponseRedirect(reverse("root"))
        members = pool.members.all()

    context = {
        'pool':pool,
        'members':members,
    }

    return render(request,"oscars/pool_home.html",context)

def join_pool(request):

    if request.user.is_anonymous():
        messages.error(request,"Please log in first")
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))

    form = oforms.JoinForm(request.POST or None)

    if form.is_valid():
        pool = get_object_or_404(bmodels.Pool,id=form.cleaned_data['pool_id'])
        if pool.password == form.cleaned_data['password']:
            pool.members.add(request.user)
            messages.success(request,"You've successfully joined the pool!")
            if hasattr(pool,"oscarpool"):
                pool = pool.oscarpool
                return HttpResponseRedirect(pool.get_absolute_url())
        messages.error(request,"Either the ID and Password given do not match.")

    return render(request,'oscars/join_form.html', {'form':form})

def pool_members(request,id=None):

    pool = get_object_or_404(omodels.OscarPool,id=id)
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))
    context = {
        'pool':pool,
        'join_url': request.build_absolute_uri(reverse("join_pool"))
    }
    return render(request,'oscars/members.html',context)

def pool_ballot_list(request,id=None):

    pool = get_object_or_404(omodels.OscarPool,id=id)
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))

    ballots = pool.ballot_set.all()
    your_ballots = ballots.filter(member=request.user)
    allow_new_ballots = True
    if datetime.timedelta(0) > (pool.entry_deadline.replace(tzinfo=None) - datetime.datetime.utcnow()):
        allow_new_ballots = False

    context = {
        'pool':pool,
        'ballots':ballots,
        'your_ballots':your_ballots,
        'allow_new_ballots':allow_new_ballots,
    }
    return render(request,'oscars/ballots.html',context)

def pool_ballot(request,id=None,ballot_id=None):

    pool = get_object_or_404(omodels.OscarPool,id=id)
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))

    allow_new_ballots = True
    if datetime.timedelta(0) > (pool.entry_deadline.replace(tzinfo=None) - datetime.datetime.utcnow()):
        allow_new_ballots = False

    ballot=None
    response_forms=[]

    if ballot_id:
        ballot = get_object_or_404(omodels.Ballot,id=ballot_id)

    if not ballot:
        pool_categories = pool.customcategory_set.filter(active=True)

    ballot_form = oforms.BallotForm(allow_new_ballots,instance=ballot)

    if request.POST:
        ballot_form = oforms.BallotForm(allow_new_ballots,request.POST,instance=ballot)
        if "delete" in request.POST:
            if datetime.timedelta(0) < (ballot.pool.oscar_ceremony.date.replace(tzinfo=None) - datetime.datetime.utcnow()):
                ballot.delete()
                messages.success(request,"The Ballot was successfully deleted")
                return HttpResponseRedirect(reverse("pool_ballots",kwargs={'id':pool.id}))
            else:
                messages.error(request,"You cannot delete ballots after the Ceremony has started")
        elif ballot_form.is_valid():
            if not ballot:
                valid_forms=True
                response_forms = []
                for category in pool_categories:
                    response_forms.append(oforms.ResponseForm(category,allow_new_ballots,request.POST,prefix=category.name))
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
                        messages.success(request,"Ballot saved successfully")
                        return HttpResponseRedirect(ballot_record.get_absolute_url())
            if ballot:
                for response in ballot.response_set.all():
                    response_form = oforms.ResponseForm(response.category,allow_new_ballots,request.POST,prefix=response.category.name,instance=response)
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
                    messages.success(request,"Ballot saved successfully")
                    return HttpResponseRedirect(ballot_record.get_absolute_url())

        messages.error(request,"Please double check that you've filled out every field.")

    if ballot and response_forms.__len__() == 0:
        for response in ballot.response_set.all():
            response_forms.append(oforms.ResponseForm(response.category,allow_new_ballots,prefix=response.category.name,instance=response))
    elif response_forms.__len__() == 0:
        for category in pool_categories:
            response_forms.append(oforms.ResponseForm(category,allow_new_ballots,prefix=category.name))

    context = {
        'pool':pool,
        'ballot':ballot,
        'ballot_form':ballot_form,
        'response_forms':response_forms,
        'allow_new_ballots':allow_new_ballots,
    }
    return render(request,'oscars/ballot_form.html',context)

def pool_standings(request,id=None):

    pool = get_object_or_404(omodels.OscarPool,id=id)
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))

    ballots = pool.ballot_set.all().distinct()

    for ballot in ballots:
        ballot.total_points = 0
        ballot.total_correct = 0
        for response in ballot.response_set.all():
            if response.category.active:
                ballot.total_points += response.points
                if response.correct:
                    ballot.total_correct += 1

        ballot.save()

    if pool.how_to_win == 'points':
        ballots = ballots.order_by('-total_points','last_save_date')
    else:
        ballots = ballots.order_by('-total_correct','last_save_date')

    context = {
        'pool':pool,
        'ballots':ballots,
    }

    return render(request,'oscars/standings.html',context)

def oscar_pool(request,id=None,form_class=oforms.OscarPoolForm):

    ceremony = omodels.OscarCeremony.objects.latest('date')

    if request.user.is_anonymous():
        messages.error(request,"Please log in first")
        return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))

    if not id:
        today = datetime.datetime.utcnow()
        if settings.OSCAR_POOLS_OPEN is False or datetime.timedelta(0) > (ceremony.date.replace(tzinfo=None) - today):
            messages.error(request,"You've missed your chance to create a pool.  Come back when the Nominees are announced for next year's award show.")
            return HttpResponseRedirect(reverse('root'))

    pool = None
    base_categories = ceremony.basecategory_set.all().order_by('priority')
    custom_categories = None
    category_forms = []

    if id:
        pool = get_object_or_404(omodels.OscarPool,id=id)
        if request.user not in pool.members.all() and request.user != pool.administrator:
            return HttpResponseRedirect(reverse("root"))
        custom_categories = omodels.CustomCategory.objects.filter(pool=pool).order_by('base_category__priority')
    if 'delete' in request.POST:
        pool.delete()
        messages.success(request,"Pool was successfully deleted")
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
                messages.success(request,"Your Pool Settings have been Saved")
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

                    messages.success(request,"Your Pool Settings have been Saved")
                return HttpResponseRedirect(pool_record.get_absolute_url())

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

    return render(request,"oscars/oscar_pool_form.html",context)

def pool_admin_message(request,id=None,form_class=oforms.AdminMessageForm):
    pool = None

    if id:
        pool = get_object_or_404(omodels.OscarPool,id=id)

    message_form = form_class(instance=pool)

    if request.POST:
        message_form = form_class(request.POST,instance=pool)

        if message_form.is_valid():
            pool_record = message_form.save()
            messages.success(request,"Welcome Message saved successfully.")
            return HttpResponseRedirect(pool_record.get_absolute_url())

    context = {
        'pool':pool,
        'form':message_form
    }

    return render(request,'oscars/admin_message_form.html',context)

def leave_pool(request,id):

    pool = get_object_or_404(omodels.OscarPool,id=id)

    if request.user != pool.administrator:
        pool.members.remove(request.user)
        pool.ballot_set.filter(member=request.user).delete()
        messages.success(request,"You have been removed from the pool")
        return HttpResponseRedirect(reverse("root"))
    else:
        messages.error(request,"You cannot leave your own pool.  If you want to delete the pool, go to 'Settings'")

    return HttpResponseRedirect(reverse("pool_members",kwargs={'id':pool.id}))

def remove_member(request,id,member_id):

    member = get_object_or_404(User,id=member_id)
    pool = get_object_or_404(omodels.OscarPool,id=id)

    pool.members.remove(member)
    pool.ballot_set.filter(member=member).delete()
    success_str="Successfully removed " + member.username + " from your pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("pool_members",kwargs={'id':pool.id}))

def predictions(request,id):


    pool = get_object_or_404(omodels.OscarPool,id=id)
    categories={}
    all_winners={}
    for custom_category in pool.customcategory_set.all():
        counts = Counter()
        percentages = OrderedDict()
        for nominee in custom_category.base_category.nominee.all():
            counts[nominee] = omodels.Response.objects.filter(category__name=custom_category.name,predicted_winner__name=nominee.name).count()
        total_responses = omodels.Response.objects.filter(category__name=custom_category.name).count()
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