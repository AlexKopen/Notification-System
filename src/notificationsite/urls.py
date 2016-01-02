from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$', 'newsletter.views.home', name='home'),
    url(r'^api/$', 'newsletter.views.api', name='api'),
    url(r'^admin/', include(admin.site.urls)),
]
