from django.conf.urls import url

from party_calculator_api.views import profile_list

urlpatterns = [
    url(r'^profiles/$', profile_list),
]