from django.conf.urls import patterns, include, url

urlpatterns = patterns('mysite.survivor.views',
    url(r'^create/',                                        'survivor_pool',              name='create_survivor_pool'),
    url(r'^(?P<id>\d+)/settings$',                          'survivor_pool',              name='survivor_pool'),
    url(r'^(?P<id>\d+)/home$',                              'pool_homepage',              name='survivor_home'),
    url(r'^(?P<id>\d+)/picksheets$',                        'survivor_member_picksheets', name='survivor_member_picksheets'),
    url(r'^(?P<id>\d+)/picksheets/create$',                 'survivor_picksheet',         name='survivor_picksheet_create'),
    url(r'^(?P<id>\d+)/picksheets/(?P<picksheet_id>\d+)$',  'survivor_picksheet',         name='survivor_picksheet'),
    url(r'^(?P<id>\d+)/standings$',                         'survivor_standings',         name='survivor_standings'),
    url(r'^(?P<id>\d+)/members$',                           'pool_members',               name='survivor_members'),
    url(r'^(?P<id>\d+)/stats$',                             'stats',                      name='survivor_stats'),
)
