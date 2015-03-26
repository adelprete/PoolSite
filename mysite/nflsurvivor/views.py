import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from mysite.base import forms as bforms
from mysite.base.views import pool_views as pviews
from mysite.nflbase import models as nflbmodels
from mysite.nflsurvivor import models as nflsmodels
from mysite.nflbase import helpers as nflbhelpers
from mysite.nflsurvivor import forms as nflsforms

@login_required

class pool_homepage(pviews.PoolHomepage):

    template = "nflsurvivor/pool_home.html"

    def get_pool(self,id):
        return get_object_or_404(nflsmodels.NFLSurvivorPool,id=id)

@login_required
def survivor_pool(request,id=None,form=nflsforms.NFLSurvivorPoolForm):

    try:
        season = nflbmodels.Season.objects.latest('start_date')
    except:
        messages.error(request,"You've missed your chance to create an NFL Survivor pool. If you are a registered user, you will be notified when the schedule is revealed for the next season.")
        return HttpResponseRedirect(reverse('root'))

    nflsurvivor_pool = None

    if not id:
        today = datetime.datetime.utcnow()
        if datetime.timedelta(0) > (season.start_date2.replace(tzinfo=None) - today) or settings.NFL_SURVIVOR_POOLS_OPEN is False:
            messages.error(request,"You've missed your chance to create an NFL Survivor pool. If you are a registered user, you will be notified when the schedule is revealed for the next season.")
            return HttpResponseRedirect(reverse('root'))

    if id:
        nflsurvivor_pool = get_object_or_404(nflsmodels.NFLSurvivorPool,id=id)

        # check if the user is the admin
        if request.user != nflsurvivor_pool.administrator:
            return HttpResponseRedirect(reverse("root"))

    if 'delete' in request.POST:
        nflsurvivor_pool.delete()
        messages.success(request,"Pool was successfully deleted")
        return HttpResponseRedirect(reverse('root'))

    nflsurvivor_pool_form = form(instance=nflsurvivor_pool)

    if request.POST:
        nflsurvivor_pool_form = form(request.POST,instance=nflsurvivor_pool)
        if nflsurvivor_pool_form.is_valid():
            survivor_pool_record = nflsurvivor_pool_form.save(commit=False)
            survivor_pool_record.season = season
            survivor_pool_record.administrator = request.user
            survivor_pool_record.save()

            messages.success(request,"Successfully saved")
            return redirect(survivor_pool_record.get_absolute_url())

    if not nflsurvivor_pool:
        if datetime.timedelta(0) > (season.start_date.replace(tzinfo=None) - datetime.datetime.utcnow()):
            nflsurvivor_pool_form.initial = {'entry_deadline':season.start_date2}
        else:
            nflsurvivor_pool_form.initial = {'entry_deadline':season.start_date}

    context = {
        'season':season,
        'pool':nflsurvivor_pool,
        'form':nflsurvivor_pool_form,
    }

    return render(request,'nflsurvivor/nflsurvivor_pool_form.html',context)

@login_required
def member_picksheets(request,id=None):

    pool = get_object_or_404(nflsmodels.NFLSurvivorPool,id=id)

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("root"))

    picksheets = pool.picksheet_set.all()
    your_picksheets = picksheets.filter(member=request.user)

    allow_new_picksheets = True
    if pool.allow_new_picksheets() == False or (picksheets.filter(member=request.user).count() >= pool.max_submissions):
        allow_new_picksheets = False

    context = {
        'pool':pool,
        'picksheets':picksheets,
        'your_picksheets':your_picksheets,
        'allow_new_picksheets':allow_new_picksheets,
    }
    return render(request,'nflsurvivor/picksheet_list.html',context)

def pool_picksheet(request,week_num=1,id=None,picksheet_id=None,form=nflsforms.PickSheetForm):

    pool = get_object_or_404(nflsmodels.NFLSurvivorPool,id=id)
    picksheet=None
    allow_new_picksheets = True

    if pool.start_week == 'wk2' and week_num == '1':
        week_num = 2
    wk = 'week' + str(week_num)

    matchups = nflsmodels.Matchup.objects.filter(week = wk,season=pool.season)

    is_users_picksheet = True
    if picksheet_id:
        picksheet = get_object_or_404(nflsmodels.PickSheet,id=picksheet_id)
        if picksheet.member != request.user:
            is_users_picksheet = False


    if pool.selection_process == 'weekly':
        if wk == 'week1':
            cut_off = pool.season.start_date
        elif wk == 'week2':
            cut_off = pool.season.start_date2
        else:
            cut_off = getattr(pool.season,wk)

        if datetime.timedelta(0) > (cut_off.replace(tzinfo=None) - datetime.datetime.utcnow()):
            allow_new_picksheets = False
    else:
        allow_new_picksheets = pool.allow_new_picksheets()

    picksheet_form = form(wk,instance=picksheet)
    if request.POST and allow_new_picksheets:

        # This is to catch members trying to go over their max submission count
        if not picksheet:
            picksheets = pool.picksheet_set.all()
            if picksheets.filter(member=request.user).count() >= pool.max_submissions:
                if pool.max_submissions == 1:
                    messages.error(request,"This pool doesn't allow more than " + str(pool.max_submissions) + " picksheet submission")
                else:
                    messages.error(request,"This pool doesn't allow more than " + str(pool.max_submissions) + " picksheet submissions")

                return HttpResponseRedirect(reverse("nflsurvivor_member_picksheets",kwargs={'id':pool.id}))


        picksheet_form = form(wk,request.POST,instance=picksheet)
        if 'team' in request.POST:

            if picksheet_form.is_valid():
                picksheet_record = picksheet_form.save(commit=False)
                picksheet_record.member = request.user
                picksheet_record.survivor_pool = pool

                if 'clear' in request.POST:
                    setattr(picksheet_record,'week'+str(week_num),"")
                else:
                    setattr(picksheet_record,'week'+str(week_num),request.POST['team'])

                if not picksheet:
                    picksheet_record.still_alive = True

                picksheet_record.save()
                picksheet_form.save_m2m()

                messages.success(request,"Your Pick was saved successfully")

                if 'continue' in request.POST:
                    return redirect(picksheet_record.get_absolute_url(week_num=int(week_num) +1))
                return redirect(picksheet_record.get_absolute_url(week_num=week_num))
        else:
            messages.error(request,"Please select a team before saving.")

    chosen_team = None
    picks = []
    picksheet_results = 0
    if picksheet:
        chosen_team = getattr(picksheet,'week'+str(week_num))
        for week in range(1,18):
            picks.append(getattr(picksheet,'week'+str(week)))

        picksheet_results = picksheet.total_points
        if pool.start_week == 'wk2':
            picksheet_results += 1

    context = {
        'pool':pool,
        'week_num':"Week " + str(week_num),
        'matchups':matchups,
        'weeks':nflbhelpers.WEEKS,
        'chosen_team':chosen_team,
        'form':picksheet_form,
        'picksheet':picksheet,
        'picks':picks,
        'allow_new_picksheets':allow_new_picksheets,
        'is_users_picksheet': is_users_picksheet,
        'picksheet_results':int(picksheet_results),
    }

    return render(request,'nflsurvivor/picksheet_form.html',context)

@login_required
def remove_picksheet(request,id,picksheet_id):

    picksheet = get_object_or_404(nflsmodels.PickSheet,id=picksheet_id)
    pool = get_object_or_404(nflsmodels.NFLSurvivorPool,id=id)

    # check if this user is the admin in this pool
    if request.user != pool.administrator:
        return HttpResponseRedirect(pool.get_absolute_url())

    picksheet.delete()

    success_str="Successfully removed picksheet from your pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("nflsurvivor_member_picksheets",kwargs={'id':pool.id}))

class standings(pviews.PoolStandings):
    template = 'nflsurvivor/standings.html'
    def __call__(self,request,*args,**kwargs):
        self.pool_instance = self.get_pool(kwargs['id'])
        self.picksheets = self.pool_instance.picksheet_set.filter(survivor_pool=self.pool_instance).distinct()
        self.picksheets.order_by('-total_points')
        return super(standings,self).__call__(request,*args,**kwargs)

    def get_pool(self,id):
        return get_object_or_404(nflsmodels.NFLSurvivorPool,id=id)

@login_required
def members(request,id=None):

    pool = get_object_or_404(nflsmodels.NFLSurvivorPool,id=id)

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))

    context = {
        'pool':pool,
        'join_url': request.build_absolute_uri(reverse("join_pool"))
    }
    return render(request,'nflsurvivor/members.html',context)

@login_required
def remove_member(request,id,member_id):

    member = get_object_or_404(User,id=member_id)
    pool = get_object_or_404(nflsmodels.NFLSurvivorPool,id=id)

    # check if this user is the admin in this pool
    if request.user != pool.administrator:
        return HttpResponseRedirect(pool.get_absolute_url())

    pool.members.remove(member)
    pool.picksheet_set.filter(member=member).delete()
    success_str="Successfully removed " + member.username + " from your pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("nflsurvivor_members",kwargs={'id':pool.id}))

@login_required
def stats(request,id):

    pool = get_object_or_404(nflsmodels.NFLSurvivorPool,id=id)

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("root"))
    current_season = nflbmodels.Season.objects.latest('start_date')
    all_picksheets = nflsmodels.PickSheet.objects.filter(survivor_pool__season=current_season).distinct()
    total_picksheets = float(all_picksheets.count())
    all_teams = nflbmodels.Team.objects.all()

    predicted_winners = []
    for week in nflbhelpers.WEEKS:
        highest_picked_team = None
        highest_number_of_picks = 0
        for team in all_teams:

            kwargs = {
                '{0}'.format(week[0]): team.__unicode__(),
            }
            count = all_picksheets.filter(**kwargs).distinct().count()

            if count > highest_number_of_picks:
                highest_picked_team = team
                highest_number_of_picks = count

        predicted_winners.append([highest_picked_team,"%.0f%%" % ((highest_number_of_picks/total_picksheets)*100)])

    top_picksheets = all_picksheets.order_by('-total_points')[:10]

    context = {
        'pool':pool,
        'predicted_winners':predicted_winners,
        'top_picksheets': top_picksheets,
    }

    return render(request,'nflsurvivor/stats.html',context)

class pool_admin_message(pviews.PoolAdminMessage):
    template = 'nflsurvivor/admin_message_form.html'
    form_class=nflsforms.AdminMessageForm
    def get_pool(self,id):
        return get_object_or_404(nflsmodels.NFLSurvivorPool,id=id)

from mysite.base.views import PublicPools
import datetime
class NFLSurvivorPublicPools(PublicPools):

    def get_title(self):
        return 'NFL Survivor'

    def get_queryset(self):

        try:
            current_season = nflbmodels.Season.objects.latest('start_date')
        except:
            current_season = None
        if datetime.timedelta(0) > (current_season.start_date.replace(tzinfo=None) - datetime.datetime.utcnow()):
            return None
        else:
            return nflsmodels.NFLSurvivorPool.objects.filter(season=current_season,public=True,is_full=False).distinct()

@login_required
def email_members(request,id):

    pool = get_object_or_404(nflsmodels.NFLSurvivorPool,id=id)
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

    return render(request,"nflsurvivor/email_members.html",context)