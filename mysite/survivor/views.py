import datetime
import json
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from mysite.survivor import forms as sforms
from mysite.survivor import models as smodels
from django.core.urlresolvers import reverse
from mysite.survivor.helpers import POINTS_CATEGORIES

@login_required
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
        'points_categories':POINTS_CATEGORIES,
    }

    return render(request,"survivor/pool_home.html",context)

@login_required
def survivor_pool(request,id=None,form=sforms.SurvivorPoolForm):

    try:
        season = smodels.SurvivorSeason.objects.latest('start_date')
    except:
        messages.error(request,"You've missed your chance to create a Survivor pool. If you are a registered user, you will be notified when the cast is revealed for the next season.")
        return HttpResponseRedirect(reverse('root'))

    survivor_pool = None
    custom_castaways = None

    if not id:
        today = datetime.datetime.utcnow()
        if datetime.timedelta(0) > (season.start_date.replace(tzinfo=None) - today) or settings.SURVIVOR_POOLS_OPEN is False:
            messages.error(request,"You've missed your chance to create a Survivor pool.  If you are a registered user, you will be notified when the cast is revealed for the next season.")
            return HttpResponseRedirect(reverse('root'))

    if id:
        survivor_pool = get_object_or_404(smodels.SurvivorPool,id=id)
        custom_castaways = survivor_pool.customcastaway_set.all()
        # check if the user is the admin
        if request.user != survivor_pool.administrator:
            return HttpResponseRedirect(reverse("root"))

    if 'delete' in request.POST:
        survivor_pool.delete()
        messages.success(request,"Pool was successfully deleted")
        return HttpResponseRedirect(reverse('root'))

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

    if not survivor_pool:
        survivor_pool_form.initial = {'entry_deadline':season.start_date}

    context = {
        'season':season,
        'pool':survivor_pool,
        'form':survivor_pool_form,
    }

    return render(request,'survivor/survivor_pool_form.html',context)

@login_required
def pool_members(request,id=None):

    pool = get_object_or_404(smodels.SurvivorPool,id=id)

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("root"))

    context = {
        'pool':pool,
        'join_url': request.build_absolute_uri(reverse("join_pool"))
    }
    return render(request,'survivor/members.html',context)

@login_required
def survivor_member_picksheets(request,id=None):

    pool = get_object_or_404(smodels.SurvivorPool,id=id)

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("root"))

    picksheets = pool.survivorpicksheet_set.all()
    your_picksheets = picksheets.filter(member=request.user)

    allow_new_picksheets = True
    if pool.allow_new_picksheets() == False or (picksheets.filter(member=request.user).count() >= pool.max_submissions):
        allow_new_picksheets = False

    if settings.SURVIVOR_PICKSHEETS_OPEN == False:
        messages.info(request,"Come back to this page when the Cast is revealed to start filling out your Pick Sheets")

    context = {
        'pool':pool,
        'picksheets':picksheets,
        'your_picksheets':your_picksheets,
        'allow_new_picksheets':allow_new_picksheets,
        'cast': settings.SURVIVOR_PICKSHEETS_OPEN,
    }
    return render(request,'survivor/picksheet_list.html',context)

@login_required
def survivor_picksheet(request,id=None,picksheet_id=None,form=sforms.SurvivorPickSheetForm):

    pool = get_object_or_404(smodels.SurvivorPool,id=id)
    picksheet = None

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("root"))

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
            return redirect(reverse("survivor_member_picksheets",kwargs={'id':pool.id}))

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

@login_required
def survivor_standings(request,id=None):

    pool = get_object_or_404(smodels.SurvivorPool,id=id)

    # check if user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator:
        if not request.user.is_superuser:
            return HttpResponseRedirect(reverse("root"))

    picksheets = pool.survivorpicksheet_set.filter(survivor_pool=pool).select_related('four_picks').distinct()

    for picksheet in picksheets:
        total_points = 0
        for castaway in picksheet.four_picks.all():
            total_points += castaway.total_points
        picksheet.total_points = total_points
        picksheet.save()

    picksheets = picksheets.order_by('-total_points')

    context = {
        'pool':pool,
        'picksheets':picksheets,
    }

    return render(request,'survivor/standings.html',context)

from mysite.base.views import PublicPools
class SurvivorPublicPools(PublicPools):

    def get_title(self):
        return 'Survivor'

    def get_queryset(self):

        try:
            current_season = smodels.SurvivorSeason.objects.latest('start_date')
        except:
            current_season = None

        return smodels.SurvivorPool.objects.filter(season=current_season,public=True).distinct()

@login_required
def leave_pool(request,id):

    pool = get_object_or_404(smodels.SurvivorPool,id=id)

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))

    if request.user != pool.administrator:
        pool.members.remove(request.user)
        pool.ballot_set.filter(member=request.user).delete()
        messages.success(request,"You have been removed from the pool")
        return HttpResponseRedirect(reverse("root"))
    else:
        messages.error(request,"You cannot leave your own pool.  If you want to delete the pool, go to 'Settings'")

    return HttpResponseRedirect(reverse("survivor_members",kwargs={'id':pool.id}))

@login_required
def stats(request,id):

    pool = get_object_or_404(smodels.SurvivorPool,id=id)
    castaways = pool.customcastaway_set.all().distinct()
    form = sforms.SurvivorStatsForm(castaways)

    # check if the user is in this pool
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
        'form':form,
        'pool':pool,
        'castaways':castaways,
        'categories':POINTS_CATEGORIES,
        'cast':settings.SURVIVOR_PICKSHEETS_OPEN,
    }

    return render(request,'survivor/stats.html',context)

def castaway_info(request):
    results = {}
    castaway = smodels.CustomCastaway.objects.select_related('base_castaway').get(id=request.GET['id'])

    for field in castaway.base_castaway._meta.get_all_field_names():
        try:
            results[field] = getattr(castaway.base_castaway,field)
        except:
            pass

    results['season'] = castaway.base_castaway.season.name
    results['image_src'] = castaway.base_castaway.image_src.url
    results['total_points'] = castaway.total_points
    results['pick_percentage'] = "%.0f%%" % ((smodels.SurvivorPickSheet.objects.filter(four_picks__base_castaway__first_name=castaway.base_castaway.first_name,\
                                                                                       four_picks__base_castaway__season=castaway.base_castaway.season).distinct().count()/float(smodels.SurvivorPickSheet.objects.all().distinct().count()))*100)

    json_info = json.dumps(results)
    return HttpResponse(json_info, mimetype='application/json')

@login_required
def pool_admin_message(request,id=None,form_class=sforms.AdminMessageForm):
    pool = None

    if id:
        pool = get_object_or_404(smodels.SurvivorPool,id=id)

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

    return render(request,'survivor/admin_message_form.html',context)

@login_required
def remove_picksheet(request,id,picksheet_id):

    picksheet = get_object_or_404(smodels.SurvivorPickSheet,id=picksheet_id)
    pool = get_object_or_404(smodels.SurvivorPool,id=id)

    # check if this user is the admin in this pool
    if request.user != pool.administrator:
        return HttpResponseRedirect(pool.get_absolute_url())

    picksheet.delete()

    success_str="Successfully removed picksheet from your pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("survivor_member_picksheets",kwargs={'id':pool.id}))

@login_required
def remove_member(request,id,member_id):

    member = get_object_or_404(User,id=member_id)
    pool = get_object_or_404(smodels.SurvivorPool,id=id)

    # check if this user is the admin in this pool
    if request.user != pool.administrator:
        return HttpResponseRedirect(pool.get_absolute_url())

    pool.members.remove(member)
    pool.survivorpicksheet_set.filter(member=member).delete()
    success_str="Successfully removed " + member.username + " from your pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("survivor_members",kwargs={'id':pool.id}))