from .views import *
from django.conf.urls import include, url

from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^richiami.json$', login_required(StatoUtenzaCorso_DTJson), name='viewname_json'),
]
