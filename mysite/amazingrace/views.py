from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages

@login_required
def amazing_race_pool(request,id=None,form=None):

    if not settings.AMAZING_RACE_POOLS_OPEN:
        messages.error(request,"You've missed your chance to create an Amazing Race pool.  Come back when the cast is revealed for the next season.")
        return HttpResponseRedirect(reverse('root'))

    context = {}
    return render(request,'survivor/survivor_pool_form.html',context)
