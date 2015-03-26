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

class PoolStandings(object):
    template = None
    pool_instance = None
    members = None
    picksheets=None
    def __new__(cls, request,*args, **kwargs):
        obj = super(PoolStandings,cls).__new__(cls)
        return obj(request, *args, **kwargs)

    def __call__(self,request,*args,**kwargs):

        self.check_if_valid_member(request.user)
        return render(request,self.template,self.get_context())

    # check if this user is in this pool
    def check_if_valid_member(self,user):

        if user.is_anonymous():
            return HttpResponseRedirect(reverse("root"))

        if user not in self.pool_instance.members.all() and user != self.pool_instance.administrator:
            return HttpResponseRedirect(reverse("root"))

    def get_pool(self):
        pass

    def get_template(self):
        pass

    def get_context(self):
        context = {
            'pool':self.pool_instance,
            'picksheets':self.picksheets
        }
        context.update(self.get_extra_context())
        return context

    def get_extra_context(self):
        return {}
