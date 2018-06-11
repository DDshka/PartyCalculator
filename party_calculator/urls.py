from django.conf.urls import url

from party_calculator.views import HomeView, PartyView, CreatePartyView, \
    CreatePartyFromExisting, PartyAddFood, PartyInvite, \
    PartyRemoveFood, PartyKickMember, PartyExcludeFood, \
    PartyIncludeFood, PartySponsor, PartyMakeInactive

urlpatterns = [
    url(r'^$', HomeView.as_view(),
        name=HomeView.name),

    url(r'^party/(?P<party_id>\d+)$', PartyView.as_view(),
        name=PartyView.name),

    url(r'^create/party$', CreatePartyView.as_view(),
        name=CreatePartyView.name),

    url(r'^create/party/from-existing$', CreatePartyFromExisting.as_view(),
        name=CreatePartyFromExisting.name),

    url(r'^party/(?P<party_id>\d+)/add/food', PartyAddFood.as_view(),
        name=PartyAddFood.name),

    url(r'^party/(?P<party_id>\d+)/add/member', PartyInvite.as_view(),
        name=PartyInvite.name),

    url(r'^party/(?P<party_id>\d+)/remove/food', PartyRemoveFood.as_view(),
        name=PartyRemoveFood.name),

    url(r'^party/(?P<party_id>\d+)/remove/member', PartyKickMember.as_view(),
        name=PartyKickMember.name),

    url(r'^party/(?P<party_id>\d+)/exclude/food', PartyExcludeFood.as_view(),
        name=PartyExcludeFood.name),

    url(r'^party/(?P<party_id>\d+)/include/food', PartyIncludeFood.as_view(),
        name=PartyIncludeFood.name),

    url(r'^party/(?P<party_id>\d+)/sponsor', PartySponsor.as_view(),
        name=PartySponsor.name),

    url(r'^party/(?P<party_id>\d+)/inactive', PartyMakeInactive.as_view(),
        name=PartyMakeInactive.name),
]
