from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

from mysite.base.views import CustomActivationView

admin.autodiscover()

urlpatterns = patterns('',

    #url(r'^accounts/login/$',       'django.contrib.auth.views.login',          {'template_name': 'login.html'},            name="login_user"),
    url(r'^accounts/logout/$',      'django.contrib.auth.views.logout_then_login',     name="logout_user"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
) + patterns('mysite.base.views',
    url(r'^activate/(?P<activation_key>\w+)/$',     CustomActivationView.as_view(),   name='registration_activate'),
    url(r'^$',                                      'root',                     name='root'),
    url(r'^signup/$',                               'signup',                   name='signup'),
    url(r'^pool/add/$',                             'pool_basic',              name='pool_add'),
    url(r'^pool/list/$',                            'your_pools',              name='your_pools'),

) + staticfiles_urlpatterns()

