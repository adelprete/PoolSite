import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from mysite.marchmadness import models as mmodels
from mysite.marchmadness import forms as mforms
from mysite.base import forms as bforms
from mysite.base.views import pool_views as pviews
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings

@login_required
class pool_homepage(pviews.PoolHomepage):

    template = "marchmadness/pool_home.html"

    def get_pool(self,id):
        return get_object_or_404(mmodels.MarchMadnessPool,id=id)

@login_required
def march_pool(request,id=None,form=mforms.MarchMadnessPoolForm):

    try:
        season = mmodels.NCAABasketballTourney.objects.latest('start_date')
    except:
        messages.error(request,"You've missed your chance to create a March Madness pool.")
        return HttpResponseRedirect(reverse('root'))

    march_madness_pool = None

    if not id:
        today = datetime.datetime.utcnow()
        if datetime.timedelta(0) > (season.start_date.replace(tzinfo=None) - today) or settings.MARCH_MADNESS_POOLS_OPEN is False:
            messages.error(request,"You've missed your chance to create a March Madness pool.")
            return HttpResponseRedirect(reverse('root'))

    if id:
        march_madness_pool = get_object_or_404(mmodels.MarchMadnessPool,id=id)

        # check if the user is the admin
        if request.user != march_madness_pool.administrator:
            return HttpResponseRedirect(reverse("root"))

    if 'delete' in request.POST:
        march_madness_pool.delete()
        messages.success(request,"Pool was successfully deleted")
        return HttpResponseRedirect(reverse('root'))

    march_madness_pool_form = form(instance=march_madness_pool)

    if request.POST:
        march_madness_pool_form = form(request.POST,instance=march_madness_pool)
        if march_madness_pool_form.is_valid():
            march_madness_pool_record = march_madness_pool_form.save(commit=False)
            march_madness_pool_record.season = season
            march_madness_pool_record.administrator = request.user
            march_madness_pool_record.save()

            messages.success(request,"Successfully saved")
            return redirect(march_madness_pool_record.get_absolute_url())

    if not march_madness_pool:
        march_madness_pool_form.initial = {'entry_deadline':season.start_date}

    context = {
        'season':season,
        'pool':march_madness_pool,
        'form':march_madness_pool_form,
    }

    return render(request,'marchmadness/march_madness_pool_form.html',context)

@login_required
def member_brackets(request,id=None):

    pool = get_object_or_404(mmodels.MarchMadnessPool,id=id)

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("root"))

    brackets = pool.bracket_set.all()
    your_brackets = brackets.filter(member=request.user)

    allow_new_picksheets = True
    if pool.allow_new_picksheets() == False or (brackets.filter(member=request.user).count() >= pool.max_submissions):
        allow_new_picksheets = False

    if settings.MARCH_MADNESS_BRACKETS_OPEN == False:
        messages.info(request,"Come back to this page when we know who will be in the Tournament to start filling out your Brackets")

    context = {
        'pool':pool,
        'brackets':brackets,
        'your_brackets':your_brackets,
        'allow_new_picksheets':allow_new_picksheets,
        'teams': settings.MARCH_MADNESS_BRACKETS_OPEN,
    }
    return render(request,'marchmadness/bracket_list.html',context)

def pool_bracket(request,id,bracket_id=None,form=mforms.BracketForm):

    pool = get_object_or_404(mmodels.MarchMadnessPool,id=id)
    bracket = None

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("root"))

    if bracket_id:
        bracket = get_object_or_404(mmodels.Bracket,id=bracket_id)

    bracket_form = form(instance=bracket)
    if request.POST:
        bracket_form = form(request.POST,instance=bracket)
        if "delete" in request.POST:
            if datetime.timedelta(0) < (bracket.march_madness_pool.season.start_date.replace(tzinfo=None) - datetime.datetime.utcnow()):
                bracket.delete()
                messages.success(request,"The Bracket was successfully deleted")
                return HttpResponseRedirect(reverse("marchmadness_member_brackets",kwargs={'id':pool.id}))
            else:
                messages.error(request,"You cannot delete brackets after the Tourney has started")
        if bracket_form.is_valid():
            bracket_record = bracket_form.save(commit=False)
            bracket_record.member = request.user
            bracket_record.march_madness_pool = pool
            bracket_record.save()
            bracket_form.save_m2m()

            messages.success(request,"Your bracket was saved successfully")
            return redirect(bracket_record.get_absolute_url())

    context = {
        'pool':pool,
        'form':bracket_form,
        'bracket':bracket,
    }

    return render(request,'marchmadness/bracket_form.html',context)

@login_required
def remove_bracket(request,id,bracket_id):

    bracket = get_object_or_404(mmodels.Bracket,id=bracket_id)
    pool = get_object_or_404(mmodels.MarchMadnessPool,id=id)

    # check if this user is the admin in this pool
    if request.user != pool.administrator:
        return HttpResponseRedirect(pool.get_absolute_url())

    bracket.delete()

    success_str="Successfully removed bracket from your pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("marchmadness_member_brackets",kwargs={'id':pool.id}))

class standings(pviews.PoolStandings):
    template = 'marchmadness/standings.html'
    brackets = None
    def __call__(self,request,*args,**kwargs):
        self.pool_instance = self.get_pool(kwargs['id'])
        self.brackets = self.pool_instance.bracket_set.filter(march_madness_pool=self.pool_instance).select_related('marchmadness_pool').distinct()
        self.brackets = self.brackets.order_by('-total_points','tie_breaker_score')
        return super(standings,self).__call__(request,*args,**kwargs)

    def get_pool(self,id):
        return get_object_or_404(mmodels.MarchMadnessPool,id=id)

    def get_extra_context(self):
        return{'brackets':self.brackets}

class pool_admin_message(pviews.PoolAdminMessage):
    template = 'marchmadness/admin_message_form.html'
    form_class=mforms.AdminMessageForm
    def get_pool(self,id):
        return get_object_or_404(mmodels.MarchMadnessPool,id=id)

@login_required
def pool_members(request,id=None):

    pool = get_object_or_404(mmodels.MarchMadnessPool,id=id)

    # check if the user is in this pool
    if request.user not in pool.members.all() and request.user != pool.administrator and not request.user.is_superuser:
        return HttpResponseRedirect(reverse("root"))

    context = {
        'pool':pool,
        'join_url': request.build_absolute_uri(reverse("join_pool"))
    }
    return render(request,'marchmadness/members.html',context)

from mysite.base.views import PublicPools
class MarchMadnessPublicPools(PublicPools):

    def get_title(self):
        return 'March Madness'

    def get_queryset(self):

        try:
            current_season = mmodels.NCAABasketballTourney.objects.latest('start_date')
        except:
            current_season = None

        return mmodels.MarchMadnessPool.objects.filter(season=current_season,public=True).distinct()

@login_required
def remove_bracket(request,id,bracket_id):

    bracket = get_object_or_404(mmodels.Bracket,id=bracket_id)
    pool = get_object_or_404(mmodels.MarchMadnessPool,id=id)

    # check if this user is the admin in this pool
    if request.user != pool.administrator:
        return HttpResponseRedirect(pool.get_absolute_url())

    bracket.delete()

    success_str="Successfully removed bracket from your pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("marchmadness_member_brackets",kwargs={'id':pool.id}))

@login_required
def remove_member(request,id,member_id):

    member = get_object_or_404(User,id=member_id)
    pool = get_object_or_404(mmodels.MarchMadnessPool,id=id)

    # check if this user is the admin in this pool
    if request.user != pool.administrator:
        return HttpResponseRedirect(pool.get_absolute_url())

    pool.members.remove(member)
    pool.bracket_set.filter(member=member).delete()
    success_str="Successfully removed " + member.username + " from your pool."
    messages.success(request,success_str)

    return HttpResponseRedirect(reverse("marchmadness_members",kwargs={'id':pool.id}))

@login_required
def email_members(request,id):

    pool = get_object_or_404(mmodels.MarchMadnessPool,id=id)
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

    return render(request,"marchmadness/email_members.html",context)
