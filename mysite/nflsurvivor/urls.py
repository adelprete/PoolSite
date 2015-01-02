from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from mysite.base.views import PublicPools


urlpatterns = patterns('mysite.nflsurvivor.views',
    url(r'^getting-started$',                               TemplateView.as_view(template_name='nflsurvivor/getting_started.html'),            name='nflsurvivor_getting_started'),
    url(r'^create/',                                                'survivor_pool',              name='create_nflsurvivor_pool'),
    url(r'^public-pools/',                                          'NFLSurvivorPublicPools',     name='nflsurvivor_public_pools'),
    url(r'^(?P<id>\d+)/settings$',                                  'survivor_pool',              name='nflsurvivor_pool'),
    url(r'^(?P<id>\d+)/home$',                                      'pool_homepage',              name='nflsurvivor_home'),
    url(r'^(?P<id>\d+)/picksheets$',                                'member_picksheets', name='nflsurvivor_member_picksheets'),
    url(r'^(?P<id>\d+)/picksheets/create/(?P<week_num>\d+)$',                    'pool_picksheet',          name='nflsurvivor_create_picksheet'),
    url(r'^(?P<id>\d+)/picksheets/(?P<picksheet_id>\d+)/(?P<week_num>\d+)$',        'pool_picksheet',          name='nflsurvivor_picksheet'),
    url(r'^(?P<id>\d+)/remove-picksheet/(?P<picksheet_id>\d+)$',    'remove_picksheet',     name='nflsurvivor_remove_picksheet'),
    url(r'^(?P<id>\d+)/standings$',                                 'standings',         name='nflsurvivor_standings'),
    url(r'^(?P<id>\d+)/members$',                                   'members',               name='nflsurvivor_members'),
    url(r'^(?P<id>\d+)/stats$',                             'stats',                      name='nflsurvivor_stats'),
    url(r'^(?P<id>\d+)/message$',                           'pool_admin_message',         name='nflsurvivor_admin_message'),
    url(r'^(?P<id>\d+)/email_members$',                     'email_members',              name='nflsurvivor_email_members'),
)
