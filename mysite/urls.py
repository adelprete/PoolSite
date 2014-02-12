from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^accounts/login/$',       'django.contrib.auth.views.login',          {'template_name': 'login.html'},            name="login_user"),
    url(r'^accounts/logout/$',      'django.contrib.auth.views.logout_then_login',     name="logout_user"),
    url(r'^admin/', include(admin.site.urls)),
) + patterns('mysite.base.views',
    url(r'^$',                                      'root',                     name='root'),
) + staticfiles_urlpatterns()

