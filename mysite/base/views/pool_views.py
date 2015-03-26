from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

# check if this user is in this pool
def check_if_valid_member(pool,user):

    if user.is_anonymous():
        return HttpResponseRedirect(reverse("root"))

    if user not in pool.members.all() and user != pool.administrator:
        return HttpResponseRedirect(reverse("root"))

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
            check_if_valid_member(self.pool_instance,request.user)

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

        check_if_valid_member(self.pool_instance,request.user)
        return render(request,self.template,self.get_context())

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

class PoolAdminMessage(object):
    template = None
    pool_instance = None
    form_class = None
    message_form = None

    def __new__(cls, request,*args, **kwargs):
        obj = super(PoolAdminMessage,cls).__new__(cls)
        return obj(request, *args, **kwargs)

    def __call__(self,request,*args,**kwargs):
        self.pool_instance = self.get_pool(kwargs['id'])
        # check if this user is in this pool
        check_if_valid_member(self.pool_instance,request.user)

        if request.user != self.pool_instance.administrator:
            return HttpResponseRedirect(self.pool_instance.get_absolute_url())

        self.message_form = self.form_class(instance=self.pool_instance)
        if request.POST:
            message_form = self.form_class(request.POST,instance=self.pool_instance)
            if message_form.is_valid():
                pool_record = message_form.save()
                messages.success(request,"Welcome Message saved successfully.")
                return HttpResponseRedirect(pool_record.get_absolute_url())

        return render(request,self.template,self.get_context())

    def get_pool(self,id):
        pass

    def get_context(self):
        context = {
            'pool':self.pool_instance,
            'form':self.message_form
        }
        return context

