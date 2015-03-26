import datetime
import json
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from mysite.base import forms as bforms
from mysite.base.views import pool_views as pviews
from mysite.amazingrace import forms as aforms
from mysite.amazingrace import models as amodels
from django.core.urlresolvers import reverse
from mysite.amazingrace.helpers import POINTS_CATEGORIES

@login_required
class pool_homepage(pviews.PoolHomepage):

    template = "amazingrace/pool_home.html"

    def get_pool(self,id):
        return get_object_or_404(amodels.AmazingRacePool,id=id)

    def get_extra_context(self):
        context = {
            'points_categories':POINTS_CATEGORIES,
        }
        return context

@login_required
def amazingrace_pool(request,id=None,form=aforms.AmazingRacePoolForm):

    try:
        season = amodels.AmazingRaceSeason.objects.latest('start_date')
    except:
        messages.error(request,"You've missed your chance to create an Amazing Race pool. If you are a registered user, you will be notified when the cast is revealed for the next season.")
        return HttpResponseRedirect(reverse('root'))

    amazingrace_pool = None
    custom_teams = None

    if not id:
        today = datetime.datetime.utcnow()
        if datetime.timedelta(0) > (season.start_date.replace(tzinfo=None) - today) or settings.AMAZING_RACE_POOLS_OPEN is False:
            messages.error(request,"You've missed your chance to create an Amazing Race pool.  If you are a registered user, you will be notified when the cast is revealed for the next season.")
            return HttpResponseRedirect(reverse('root'))

    if id:
        amazingrace_pool = get_object_or_404(amodels.AmazingRacePool,id=id)
        custom_teams = amazingrace_pool.customteam_set.all()
        # check if the user is the admin
        if request.user != amazingrace_pool.administrator:
            return HttpResponseRedirect(reverse("root"))

    if 'delete' in request.POST:
        amazingrace_pool.delete()
        messages.success(request,"Pool was successfully deleted")
        return HttpResponseRedirect(reverse('root'))

    amazingrace_pool_form = form(instance=amazingrace_pool)

    if request.POST:
        amazingrace_pool_form = form(request.POST,instance=amazingrace_pool)
        if amazingrace_pool_form.is_valid():
            amazingrace_pool_record = amazingrace_pool_form.save(commit=False)
            amazingrace_pool_record.season = season
            amazingrace_pool_record.administrator = request.user
            amazingrace_pool_record.save()
            if not custom_teams:
                for base_team in season.baseteam_set.all():
                    amodels.CustomTeam.objects.create(total_points=0,amazingrace_pool_id=amazingrace_pool_record.id,base_team=base_team)
            messages.success(request,"Successfully saved")
            return redirect(amazingrace_pool_record.get_absolute_url())

    if not amazingrace_pool:
        amazingrace_pool_form.initial = {'entry_deadline':season.start_date}

    context = {
        'season':season,
        'pool':amazingrace_pool,
        'form':amazingrace_pool_form,
    }

    return render(request,'amazingrace/amazingrace_pool_form.html',context)


@login_required
def pool_members(request,id=None):

    pool = get_object_or_404(amodels.AmazingRacePool,id=id)

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))

    context = {
        'pool':pool,
        'join_url': request.build_absolute_uri(reverse("join_pool"))
    }
    return render(request,'amazingrace/members.html',context)

@login_required
def amazingrace_member_picksheets(request,id=None):

    pool = get_object_or_404(amodels.AmazingRacePool,id=id)

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))

    picksheets = pool.amazingracepicksheet_set.all()
    your_picksheets = picksheets.filter(member=request.user)

    allow_new_picksheets = True
    if pool.allow_new_picksheets() == False or (picksheets.filter(member=request.user).count() >= pool.max_submissions):
        allow_new_picksheets = False

    if settings.AMAZING_RACE_PICKSHEETS_OPEN == False:
        messages.info(request,"Come back to this page when the Cast is revealed to start filling out your Pick Sheets")

    context = {
        'pool':pool,
        'picksheets':picksheets,
        'your_picksheets':your_picksheets,
        'allow_new_picksheets':allow_new_picksheets,
        'cast':settings.AMAZING_RACE_PICKSHEETS_OPEN,
    }
    return render(request,'amazingrace/picksheet_list.html',context)

@login_required
def amazingrace_picksheet(request,id=None,picksheet_id=None,form=aforms.AmazingRacePickSheetForm):

    pool = get_object_or_404(amodels.AmazingRacePool,id=id)
    picksheet = None

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))

    if picksheet_id:
        picksheet = get_object_or_404(amodels.AmazingRacePickSheet,id=picksheet_id)

    picksheet_form = form(request.user,pool,instance=picksheet)
    if request.POST:
        picksheet_form = form(request.user,pool,request.POST,instance=picksheet)
        if picksheet_form.is_valid():
            picksheet_record = picksheet_form.save(commit=False)
            picksheet_record.member = request.user
            picksheet_record.amazingrace_pool = pool
            picksheet_record.save()
            picksheet_form.save_m2m()

            messages.success(request,"Your Pick Sheet was saved successfully")
            return redirect(reverse("amazingrace_member_picksheets",kwargs={'id':pool.id}))

    picksheets = pool.amazingracepicksheet_set.all()
    combinations_list = []
    [combinations_list.append(sheet.picks.all().values_list("base_team__nickname",flat=True)) for sheet in picksheets]

    context = {
        'picksheet':picksheet,
        'form':picksheet_form,
        'pool':pool,
        'combinations_list':combinations_list,
    }

    return render(request,'amazingrace/picksheet_form.html',context)

class amazingrace_standings(pviews.PoolStandings):
    template = 'amazingrace/standings.html'
    def __call__(self,request,*args,**kwargs):

        self.pool_instance = self.get_pool(kwargs['id'])
        self.picksheets = self.pool_instance.amazingracepicksheet_set.filter(amazingrace_pool=self.pool_instance).select_related('picks').distinct()

        for picksheet in self.picksheets:
                total_points = 0
                for team in picksheet.picks.all():
                    total_points += team.total_points
                picksheet.total_points = total_points
                picksheet.save()

        self.picksheets.order_by('-total_points')
        return super(amazingrace_standings,self).__call__(request,*args,**kwargs)

    def get_pool(self,id):
        return get_object_or_404(amodels.AmazingRacePool,id=id)

    def get_extra_context(self):
        return {'picksheets':self.picksheets}

@login_required
def leave_pool(request,id):

    pool = get_object_or_404(amodels.AmazingRacePool,id=id)

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

    return HttpResponseRedirect(reverse("amazingrace_members",kwargs={'id':pool.id}))

@login_required
def stats(request,id):

    pool = get_object_or_404(amodels.AmazingRacePool,id=id)
    teams = pool.customteam_set.all().distinct()
    form = aforms.AmazingRaceStatsForm(teams)

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))

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
        'teams':teams,
        'categories':POINTS_CATEGORIES,
        'cast':settings.AMAZING_RACE_PICKSHEETS_OPEN,
    }

    return render(request,'amazingrace/stats.html',context)

def team_info(request):
    results = {}
    team = amodels.CustomTeam.objects.select_related('base_team').get(id=request.GET['id'])

    for field in team.base_team._meta.get_all_field_names():
        try:
            results[field] = getattr(team.base_team,field)
        except:
            pass

    results['season'] = team.base_team.season.name
    results['image_src'] = team.base_team.image_src.url
    results['total_points'] = team.total_points
    results['pick_percentage'] = "%.0f%%" % ((amodels.AmazingRacePickSheet.objects.filter(picks__base_team__team_member_1=team.base_team.team_member_1,\
                                                                                          picks__base_team__team_member_2=team.base_team.team_member_2,\
                                                                                          picks__base_team__season=team.base_team.season).distinct().count()/float(amodels.AmazingRacePickSheet.objects.all().distinct().count()))*100)
    json_info = json.dumps(results)
    return HttpResponse(json_info, mimetype='application/json')

class pool_admin_message(pviews.PoolAdminMessage):
    template = 'amazingrace/admin_message_form.html'
    form_class=aforms.AdminMessageForm
    def get_pool(self,id):
        return get_object_or_404(amodels.AmazingRacePool,id=id)

@login_required
def remove_picksheet(request,id,picksheet_id):

    picksheet = get_object_or_404(amodels.AmazingRacePickSheet,id=picksheet_id)
    pool = get_object_or_404(amodels.AmazingRacePool,id=id)

    # check if this user is the admin in this pool
    if request.user != pool.administrator:
        return HttpResponseRedirect(pool.get_absolute_url())

    picksheet.delete()

    success_str="Successfully removed picksheet from your pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("amazingrace_member_picksheets",kwargs={'id':pool.id}))

@login_required
def remove_member(request,id,member_id):

    member = get_object_or_404(User,id=member_id)
    pool = get_object_or_404(amodels.AmazingRacePool,id=id)

    # check if this user is the admin in this pool
    if request.user != pool.administrator:
        return HttpResponseRedirect(pool.get_absolute_url())

    pool.members.remove(member)
    pool.amazingracepicksheet_set.filter(member=member).delete()
    success_str="Successfully removed " + member.username + " from your pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("amazingrace_members",kwargs={'id':pool.id}))

from mysite.base.views import PublicPools
class AmazingRacePublicPools(PublicPools):

    def get_title(self):
        return 'Amazing Race'

    def get_queryset(self):

        try:
            current_season = amodels.AmazingRaceSeason.objects.latest('start_date')
        except:
            current_season = None

        return amodels.AmazingRacePool.objects.filter(season=current_season,public=True).distinct()

@login_required
def email_members(request,id):

    pool = get_object_or_404(amodels.AmazingRacePool,id=id)
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

    return render(request,"survivor/email_members.html",context)