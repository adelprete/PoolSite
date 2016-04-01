from mysite.oscars import models as omodels
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages

def paid(func):
    """
        simple decorator that checks if the pool has been paid for,
        if not send them to the payment screen
    """
    def decorator(request,id=None,*args, **kwargs):
        if id:
            pool = get_object_or_404(omodels.OscarPool,id=id)
            if not pool.paid:
                messages.error(request,"Pool not paid for yet")
                return HttpResponseRedirect(reverse("oscar_payment",kwargs={'id':pool.id}))
            return func(request, id, *args, **kwargs)
    return decorator
