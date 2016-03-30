from mysite.oscars import models as omodels
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

def paid(func):
    def decorator(request,id,*args, **kwargs):
        pool = get_object_or_404(omodels.OscarPool,id=id)
        if not pool.paid:
            messages.warning(request,"Pool not paid for")
            return HttpResponseRedirect(reverse("oscar_settings",kwargs={'id':pool.id}))
        return func(request, id, *args, **kwargs)
    return decorator
