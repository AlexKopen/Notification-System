from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', 'birthday.views.home', name='home'),
    url(r'^api/$', 'birthday.views.api', name='api'),
    url(r'^logout/$', 'birthday.views.logout', name='logout'),
    url(r'^admin/', include(admin.site.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
