from django.conf.urls import url

from party_calculator_api.views import profile_list, profile_list_by_term

urlpatterns = [
    url(r'^profiles/$', profile_list),
    url(r'^profiles/term/', profile_list_by_term,
        name='profile-list-by-term'),
]