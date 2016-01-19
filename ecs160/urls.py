"""ecs160 URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^warcraft/', include('warcraft.urls', namespace="warcraft")),
    url(r'^/$', include('warcraft.urls', namespace="warcraft")),
    url(r'', include('warcraft.urls', namespace="warcraft")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^messages/', include('django_messages.urls')),
    url(r'^accounts/login/$', 'warcraft.views.login'),
    url(r'^accounts/logout/$', 'warcraft.views.logout'),
    url(r'^accounts/loggedin/$', 'warcraft.views.loggedin'),
    url(r'^accounts/invalid/$', 'warcraft.views.invalid_login'),
    url(r'^accounts/register/$', 'warcraft.views.register_user'),
    url(r'^accounts/register_success/$', 'warcraft.views.register_success'),
    url(r'^accounts/internalLogin/$', 'warcraft.views.internalLogin'),
    url(r'^accounts/activate/(?P<userName>\w{1,50})/(?P<activation_key>\w{1,50})/$', 'warcraft.views.activate'),
	url(r'^web-players-status/$', 'warcraft.views.webLoggedIn'),
    url(r'^game-players-status/$', 'warcraft.views.internalLoggedIn'),
    url(r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset', kwargs={'template_name' : 'password_reset.html'}),
    url(r'^accounts/password_reset_done/$', 'django.contrib.auth.views.password_reset_done', kwargs={'template_name' : 'password_reset_done.html'}, name='password_reset_done'),
    url(r'^accounts/password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'django.contrib.auth.views.password_reset_confirm', kwargs={'template_name' : 'password_reset_confirm.html'}, name='password_reset_confirm'),
    url(r'^accounts/password_reset_complete/$', 'django.contrib.auth.views.password_reset_complete', kwargs={'template_name' : 'password_reset_complete.html'}, name='password_reset_complete'),
    url(r'^downloads/$', 'warcraft.views.downloads'),
    url(r'^accounts/edit/$', 'warcraft.views.edit_profile'),
    url(r'^accounts/edit_profile_success/$', 'warcraft.views.edit_profile_success'),
    url(r'^accounts/change_password/$', 'warcraft.views.change_password'),
    url(r'^accounts/change_password_success/$', 'warcraft.views.change_password_success'),
    url(r'^compose_success/$', 'warcraft.views.compose_success'),    
    url(r'^send_something/$', 'warcraft.views.send_something'),
    url(r'^accounts/friends/$', 'warcraft.views.friends'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)