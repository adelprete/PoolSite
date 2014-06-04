from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from mysite.survivor import forms as sforms
from mysite.survivor import models as smodels
from django.core.urlresolvers import reverse

def pool_homepage(request,id=None):

    pool=None

    if id:
        pool = get_object_or_404(smodels.SurvivorPool,id=id)
        if request.user not in pool.members.all() and request.user != pool.administrator:
            return HttpResponseRedirect(reverse("root"))
        members = pool.members.all()

    context = {
        'pool':pool,
        'members':members,
    }

    return render(request,"survivor/pool_home.html",context)

def survivor_pool(request,id=None,form=sforms.SurvivorPoolForm):

    season = smodels.SurvivorSeason.objects.latest('start_date')

    survivor_pool = None
    custom_castaways = None

    if id:
        survivor_pool = get_object_or_404(smodels.SurvivorPool,id=id)
        custom_castaways = survivor_pool.customcastaway_set.all()

    survivor_pool_form = form(instance=survivor_pool)

    if request.POST:
        survivor_pool_form = form(request.POST,instance=survivor_pool)
        if survivor_pool_form.is_valid():
            survivor_pool_record = survivor_pool_form.save(commit=False)
            survivor_pool_record.season = season
            survivor_pool_record.administrator = request.user
            survivor_pool_record.save()
            if not custom_castaways:
                for base_cast in season.basecastaway_set.all():
                    smodels.CustomCastaway.objects.create(total_points=0,survivor_pool_id=survivor_pool_record.id,base_castaway=base_cast)
            messages.success(request,"Successfully saved")
            return redirect(survivor_pool_record.get_absolute_url())



    context = {
        'season':season,
        'pool':survivor_pool,
        'form':survivor_pool_form,
    }

    return render(request,'survivor/survivor_pool_form.html',context)

def pool_members(request,id=None):

    pool = get_object_or_404(smodels.SurvivorPool,id=id)
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))
    context = {
        'pool':pool,
        'join_url': request.build_absolute_uri(reverse("join_pool"))
    }
    return render(request,'survivor/members.html',context)

def survivor_member_picksheets(request,id=None):

    pool = get_object_or_404(smodels.SurvivorPool,id=id)

    picksheets = pool.survivorpicksheet_set.all()
    your_picksheets = picksheets.filter(member=request.user)

    context = {
        'pool':pool,
        'picksheets':picksheets,
        'your_picksheets':your_picksheets,
    }
    return render(request,'survivor/picksheet_list.html',context)

def survivor_picksheet(request,id=None,picksheet_id=None,form=sforms.SurvivorPickSheetForm):

    pool = get_object_or_404(smodels.SurvivorPool,id=id)
    picksheet = None

    if picksheet_id:
        picksheet = get_object_or_404(smodels.SurvivorPickSheet,id=picksheet_id)

    picksheet_form = form(request.user,pool,instance=picksheet)
    if request.POST:
        picksheet_form = form(request.user,pool,request.POST,instance=picksheet)
        if picksheet_form.is_valid():
            picksheet_record = picksheet_form.save(commit=False)
            picksheet_record.member = request.user
            picksheet_record.survivor_pool = pool
            picksheet_record.save()
            picksheet_form.save_m2m()

            messages.success(request,"Your Pick Sheet was saved successfully")
            return redirect(picksheet_record.get_absolute_url())

    picksheets = pool.survivorpicksheet_set.all()
    combinations_list = []
    [combinations_list.append(sheet.four_picks.all().values_list("base_castaway__first_name",flat=True)) for sheet in picksheets]

    context = {
        'picksheet':picksheet,
        'form':picksheet_form,
        'pool':pool,
        'combinations_list':combinations_list,
    }

    return render(request,'survivor/picksheet_form.html',context)

def survivor_standings(request,id=None):

    pool = get_object_or_404(smodels.SurvivorPool,id=id)
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))

    picksheets = pool.survivorpicksheet_set.filter(survivor_pool=pool).select_related('four_picks').distinct()

    for picksheet in picksheets:
        total_points = 0
        for castaway in picksheet.four_picks.all():
            total_points += castaway.total_points
        picksheet.total_points = total_points
        picksheet.save()

    picksheets.order_by('-total_points')

    context = {
        'pool':pool,
        'picksheets':picksheets,
    }

    return render(request,'survivor/standings.html',context)

def leave_pool(request,id):

    pool = get_object_or_404(smodels.SurvivorPool,id=id)

    if request.user != pool.administrator:
        pool.members.remove(request.user)
        pool.ballot_set.filter(member=request.user).delete()
        messages.success(request,"You have been removed from the pool")
        return HttpResponseRedirect(reverse("root"))
    else:
        messages.error(request,"You cannot leave your own pool.  If you want to delete the pool, go to 'Settings'")

    return HttpResponseRedirect(reverse("survivor_members",kwargs={'id':pool.id}))

def remove_member(request,id,member_id):

    member = get_object_or_404(User,id=member_id)
    pool = get_object_or_404(smodels.SurvivorPool,id=id)

    pool.members.remove(member)
    pool.ballot_set.filter(member=member).delete()
    success_str="Successfully removed " + member.username + " from your pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("survivor_members",kwargs={'id':pool.id}))

from mysite.survivor.helpers import POINTS_CATEGORIES
def stats(request,id):

    pool = get_object_or_404(smodels.SurvivorPool,id=id)
    castaways = pool.season.basecastaway_set.all().distinct()
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))

    events_table={}
    """
    for key,value in POINTS_CATEGORIES.iteritems():
        if getattr(pool,key):
            event_table[key] = []
            for castaway in castaways:
                event_table[key].append(getattr(castaway,key))
    """

    context = {
        'pool':pool,
        'castaways':castaways,
        'categories':POINTS_CATEGORIES,
    }

    return render(request,'survivor/stats.html',context)