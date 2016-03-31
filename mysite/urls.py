from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.conf import settings
from django.views.generic.base import TemplateView
from mysite.base.views import CustomActivationView, RegistrationViewUniqueEmail


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^user/password/reset/$',     'django.contrib.auth.views.password_reset',      {'post_reset_redirect' : '/user/password/reset/done/'}, name="password_reset"),
    url(r'^user/password/reset/done/$',  'django.contrib.auth.views.password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm',  name='password_reset_confirm'),
    url(r'^user/password/done/$', 'django.contrib.auth.views.password_reset_complete',                              name="password_reset_complete"),
    #url(r'^accounts/login/$',       'django.contrib.auth.views.login',          {'template_name': 'login.html'},            name="login_user"),
    url(r'^accounts/logout/$',      'django.contrib.auth.views.logout_then_login',     name="logout_user"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^oscars/', include('mysite.oscars.urls')),
    url(r'^survivor/', include('mysite.survivor.urls')),
    url(r'^amazingrace/', include('mysite.amazingrace.urls')),
    url(r'^marchmadness/', include('mysite.marchmadness.urls')),
    url(r'^nflsurvivor/', include('mysite.nflsurvivor.urls')),
    url(r'^user/register', RegistrationViewUniqueEmail.as_view(), name='registration_register'),
) + patterns('mysite.base.views',
    url(r'^faq$',                                   TemplateView.as_view(template_name='base/faq.html'),            name='faq'),
    url(r'^activate/(?P<activation_key>\w+)/$',     CustomActivationView.as_view(),   name='registration_activate'),
    url(r'^$',                                      TemplateView.as_view(template_name='panel_core.html'),                 name='root'),
    url(r'^signup/$',                               'signup',                   name='signup'),
    #url(r'^pool/add/$',                            'pool_basic',              name='pool_add'),
    url(r'^pool/list/$',                            'your_pools',              name='your_pools'),
    url(r'^profile/$',                              'profile_basics',                   name='add_profile'),
    url(r'^(\d+)/profile/basics/$',                 'profile_basics',                   name='profile_basics'),
    url(r'^(\d+)/profile/$',                        'profile_stats',                   name='profile_stats'),
    url(r'^pool/join/(?P<id>\w+)',                  'join_public_pool',              name='join_public_pool'),
    url(r'^pool/join/(?P<id>\w+)/(?P<password>\w+)','join_pool',              name='join_pool_info'),
    url(r'^pool/join/',                             'join_pool',              name='join_pool'),
    url(r'^pool/(?P<id>\d+)/leave$',                'leave_pool',           name='leave_pool'),
    url(r'^contact/$',                              'contact',              name='contact'),

    #url(r'^paypal/', include('paypal.standard.ipn.urls')),
    url(r'^success/$',        TemplateView.as_view(template_name='success.html'), name='success_url'),
    url(r'^fail/$',        TemplateView.as_view(template_name='fail.html'), name='fail_url'),


    url(r'^maltingame$',                                   TemplateView.as_view(template_name='base/maltingame.html')),
) + staticfiles_urlpatterns() + patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
