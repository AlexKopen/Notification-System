"""notificationsite URL Configuration

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
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', 'newsletter.views.home', name='home'),
    url(r'^api/$', 'newsletter.views.api', name='api'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', RedirectView.as_view(
        url='https://drchrono.com/o/authorize/?redirect_uri=http://localhost:8000/api/&response_type=code&client_id=kS9O05JP4l7pSMC7BObcU2bLOX2iS5QVSP2AyqKa')),
]
