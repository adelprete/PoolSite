from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

urlpatterns = patterns('mysite.amazingrace.views',
    url(r'^getting-started$',                               TemplateView.as_view(template_name='amazingrace/getting_started.html'),            name='amazingrace_getting_started'),
    url(r'^create/',                                        'amazingrace_pool',              name='create_amazing_race_pool'),
    url(r'^public-pools/',                                  'AmazingRacePublicPools',        name='amazingrace_public_pools'),
    url(r'^(?P<id>\d+)/settings$',                          'amazingrace_pool',              name='amazingrace_pool'),
    url(r'^(?P<id>\d+)/home$',                              'pool_homepage',                 name='amazingrace_home'),
    url(r'^(?P<id>\d+)/picksheets$',                        'amazingrace_member_picksheets', name='amazingrace_member_picksheets'),
    url(r'^(?P<id>\d+)/picksheets/create$',                 'amazingrace_picksheet',         name='amazingrace_picksheet_create'),
    url(r'^(?P<id>\d+)/picksheets/(?P<picksheet_id>\d+)$',  'amazingrace_picksheet',         name='amazingrace_picksheet'),
    url(r'^(?P<id>\d+)/remove-picksheet/(?P<picksheet_id>\d+)$',  'remove_picksheet',        name='amazingrace_remove_picksheet'),
    url(r'^(?P<id>\d+)/remove-member/(?P<member_id>\d+)$',  'remove_member',                 name='amazingrace_remove_member'),
    url(r'^(?P<id>\d+)/standings$',                         'amazingrace_standings',         name='amazingrace_standings'),
    url(r'^(?P<id>\d+)/members$',                           'pool_members',                  name='amazingrace_members'),
    url(r'^(?P<id>\d+)/stats$',                             'stats',                         name='amazingrace_stats'),
    url(r'^(?P<id>\d+)/message$',                           'pool_admin_message',            name='amazingrace_admin_message'),
    url(r'^stats$',                                         'team_info',                     name='team_info'),
    url(r'^(?P<id>\d+)/email_members$',                     'email_members',                 name='amazingrace_email_members'),
    url(r'^(?P<id>\d+)/recap$',                             'amazingrace_standings',         {'template':'amazingrace/recap.html'},       name='amazingrace_pool_recap'),
)