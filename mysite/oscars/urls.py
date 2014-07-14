from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from mysite.oscars import models as omodels
from mysite.base.views import PublicPools

current_ceremony = omodels.OscarCeremony.objects.latest('date')

urlpatterns = patterns('mysite.oscars.views',
    url(r'^getting-started$',                               TemplateView.as_view(template_name='oscars/getting_started.html'),            name='oscars_getting_started'),
    url(r'^create/',                                        'oscar_pool',           name='create_oscar_pool'),
    url(r'^public-pools/',
        PublicPools.as_view(title='Oscar',queryset=omodels.OscarPool.objects.filter(oscar_ceremony=current_ceremony,public=True).distinct()),
        name='oscar_public_pools'),
    url(r'^(?P<id>\d+)/settings$',                          'oscar_pool',           name='oscar_settings'),
    url(r'^(?P<id>\d+)/home$',                              'pool_homepage',        name='oscar_home'),
    url(r'^(?P<id>\d+)/members$',                           'pool_members',         name='oscar_members'),
    url(r'^(?P<id>\d+)/ballots$',                           'pool_ballot_list',     name='oscar_pool_ballots'),
    url(r'^(?P<id>\d+)/ballots/create$',                    'pool_ballot',          name='oscar_create_ballot'),
    url(r'^(?P<id>\d+)/ballots/(?P<ballot_id>\d+)$',        'pool_ballot',          name='oscar_ballot'),
    url(r'^(?P<id>\d+)/standings$',                         'pool_standings',       name='oscar_standings'),
    url(r'^(?P<id>\d+)/message$',                           'pool_admin_message',   name='oscar_admin_message'),
    url(r'^(?P<id>\d+)/remove-member/(?P<member_id>\d+)$',  'remove_member',        name='remove_member'),
    url(r'^(?P<id>\d+)/remove-ballot/(?P<ballot_id>\d+)$',  'remove_ballot',        name='oscar_remove_ballot'),
    url(r'^(?P<id>\d+)/predictions$',                       'predictions',          name='predictions'),
)


