"""betaCRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views import *

urlpatterns = [

    url(r'^login/$', Login, name='login'),
    url(r'^logout/$', Logout, name='logout'),

    url(
        r'online$',
        OnlineUsers,
        name='online_users',
    ),
    
    url(
        r'^user-autocomplete/$',
        UserAutocomplete.as_view(),
        name='user-autocomplete',
    ),
    
    url(r'calendar/$', UserCalendar, name='user_calendar'),
    url(r'profile/$', UserProfile, name='user_profile'),    
    url(r'edit/$', EditUserProfile, name='edit_profile'),
    
]
