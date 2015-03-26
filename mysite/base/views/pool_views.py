from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse

class PoolHomepage(object):

    template = None
    pool_instance = None
    members = None

    def __new__(cls, request,*args, **kwargs):
        obj = super(PoolHomepage,cls).__new__(cls)
        return obj(request, *args, **kwargs)

    def __call__(self,request,*args,**kwargs):

        if 'id' in kwargs:
            self.pool_instance = self.get_pool(id=kwargs['id'])
            if request.user not in self.pool_instance.members.all() and request.user != self.pool_instance.administrator:
                return HttpResponseRedirect(reverse("root"))

        return render(request,self.template,self.get_context())

    def get_pool(self):
        pass

    def get_template(self):
        pass

    def get_context(self):
        context = {
            'pool':self.pool_instance,
            'members':self.pool_instance.members.all()
        }
        context.update(self.get_extra_context())
        return context

    def get_extra_context(self):
        return {}
