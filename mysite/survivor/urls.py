from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

urlpatterns = patterns('mysite.survivor.views',
    url(r'^getting-started$',                               TemplateView.as_view(template_name='survivor/getting_started.html'),            name='survivor_getting_started'),
    url(r'^create/',                                        'survivor_pool',              name='create_survivor_pool'),
    url(r'^public-pools/',                                  'SurvivorPublicPools',          name='survivor_public_pools'),
    url(r'^(?P<id>\d+)/settings$',                          'survivor_pool',              name='survivor_pool'),
    url(r'^(?P<id>\d+)/home$',                              'pool_homepage',              name='survivor_home'),
    url(r'^(?P<id>\d+)/picksheets$',                        'survivor_member_picksheets', name='survivor_member_picksheets'),
    url(r'^(?P<id>\d+)/picksheets/create$',                 'survivor_picksheet',         name='survivor_picksheet_create'),
    url(r'^(?P<id>\d+)/picksheets/(?P<picksheet_id>\d+)$',  'survivor_picksheet',         name='survivor_picksheet'),
    url(r'^(?P<id>\d+)/remove-picksheet/(?P<picksheet_id>\d+)$',  'remove_picksheet',     name='survivor_remove_picksheet'),
    url(r'^(?P<id>\d+)/remove-member/(?P<member_id>\d+)$',  'remove_member',              name='survivor_remove_member'),
    url(r'^(?P<id>\d+)/standings$',                         'survivor_standings',         name='survivor_standings'),
    url(r'^(?P<id>\d+)/members$',                           'pool_members',               name='survivor_members'),
    url(r'^(?P<id>\d+)/stats$',                             'stats',                      name='survivor_stats'),
    url(r'^(?P<id>\d+)/message$',                           'pool_admin_message',         name='survivor_admin_message'),
    url(r'^stats$',                                         'castaway_info',              name='castaway_info'),
    url(r'^(?P<id>\d+)/email_members$',                     'email_members',              name='survivor_email_members'),
    url(r'^(?P<id>\d+)/recap$',                         'survivor_standings',         {'template':'survivor/recap.html'},       name='survivor_pool_recap'),
)
