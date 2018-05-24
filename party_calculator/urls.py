from django.conf.urls import url

from party_calculator.views import HomeView, CreatePartyView

urlpatterns = [
  url(r'^$', HomeView.as_view(),
      name="home"),

  url(r'^create/party', CreatePartyView.as_view(),
      name='create-party')

]
