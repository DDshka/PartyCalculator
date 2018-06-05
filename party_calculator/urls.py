from django.conf.urls import url

from party_calculator.views import HomeView, CreatePartyView, PartyView, PartyAddFood, PartyExcludeFood, \
  PartyIncludeFood, PartyRemoveFood

urlpatterns = [
  url(r'^$', HomeView.as_view(),
      name="home"),

  url(r'^party/(?P<party_id>\d+)$', PartyView.as_view(),
      name='party'),

  url(r'^create/party', CreatePartyView.as_view(),
      name='create-party'),

  url(r'^party/(?P<party_id>\d+)/add/food', PartyAddFood.as_view(),
      name='add-food-to-party'),

  url(r'^party/(?P<party_id>\d+)/add/member', PartyAddFood.as_view(),
      name='invite-member-to-party'),

  url(r'^party/(?P<party_id>\d+)/remove/food', PartyRemoveFood.as_view(),
      name='remove-food'),

  url(r'^party/(?P<party_id>\d+)/exclude/food', PartyExcludeFood.as_view(),
      name='exclude-food'),

  url(r'^party/(?P<party_id>\d+)/include/food', PartyIncludeFood.as_view(),
      name='include-food'),
]
