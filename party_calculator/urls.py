from django.conf.urls import url

from party_calculator.views import HomeView, ProfileView, CardAdd, CardUpdate, CardDelete
from party_calculator.views.parties import PartyCreateView, PartyCreateFromExisting, \
    PartyDelete, PartyMakeInactive, \
    PartyRevokeOwnership, PartyGrantOwnership, \
    PartySponsor, PartyIncludeFood, \
    PartyExcludeFood, PartyKickMember, \
    PartyRemoveFood, PartyInvite, \
    PartyAddCustomFood, PartyAddFood, \
    PartyView
from party_calculator.views.templates import TemplateDelete, TemplateSetFrequency, \
    TemplateRevokeOwnership, \
    TemplateGrantOwnership, TemplateSetActive, \
    TemplateSetInactive, TemplateRemoveFood, \
    TemplateAddCustomFood, TemplateAddFood, \
    TemplateKickMember, TemplateAddMemberView, \
    TemplatePartyView, TemplateCreateFromParty, \
    TemplateCreate, TemplatesListView

urlpatterns = [
    url(r'^$', HomeView.as_view(),
        name=HomeView.name),

    url(r'^profile$', ProfileView.as_view(),
        name=ProfileView.name),

    url(r'^card/add$', CardAdd.as_view(),
        name=CardAdd.name),

    url(r'^card/update/(?P<recurring_detail_reference>\d+)$', CardUpdate.as_view(),
        name=CardUpdate.name),

    url(r'^card/delete/(?P<recurring_detail_reference>\d+)$', CardDelete.as_view(),
        name=CardDelete.name),

    url(r'^party/(?P<party_id>\d+)$', PartyView.as_view(),
        name=PartyView.name),

    url(r'^create/party$', PartyCreateView.as_view(),
        name=PartyCreateView.name),

    url(r'^create/party/from-existing$', PartyCreateFromExisting.as_view(),
        name=PartyCreateFromExisting.name),

    url(r'^party/(?P<party_id>\d+)/add/food', PartyAddFood.as_view(),
        name=PartyAddFood.name),

    url(r'^party/(?P<party_id>\d+)/add/custom-food', PartyAddCustomFood.as_view(),
        name=PartyAddCustomFood.name),

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

    url(r'^party/(?P<party_id>\d+)/add/owner', PartyGrantOwnership.as_view(),
        name=PartyGrantOwnership.name),

    url(r'^party/(?P<party_id>\d+)/remove/owner', PartyRevokeOwnership.as_view(),
        name=PartyRevokeOwnership.name),

    url(r'^party/(?P<party_id>\d+)/inactive', PartyMakeInactive.as_view(),
        name=PartyMakeInactive.name),

    url(r'^party/(?P<party_id>\d+)/delete', PartyDelete.as_view(),
        name=PartyDelete.name),

    # --------------------------------

    url(r'^templates$', TemplatesListView.as_view(),
        name=TemplatesListView.name),

    url(r'^templates/create$', TemplateCreate.as_view(),
        name=TemplateCreate.name),

    url(r'^templates/create/(?P<party_id>\d+)$', TemplateCreateFromParty.as_view(),
        name=TemplateCreateFromParty.name),

    url(r'^templates/(?P<template_id>\d+)$', TemplatePartyView.as_view(),
        name=TemplatePartyView.name),

    url(r'^templates/(?P<template_id>\d+)/add/member', TemplateAddMemberView.as_view(),
        name=TemplateAddMemberView.name),

    url(r'^templates/(?P<template_id>\d+)/remove/member', TemplateKickMember.as_view(),
        name=TemplateKickMember.name),

    url(r'^templates/(?P<template_id>\d+)/add/food', TemplateAddFood.as_view(),
        name=TemplateAddFood.name),

    url(r'^templates/(?P<template_id>\d+)/add/custom-food', TemplateAddCustomFood.as_view(),
        name=TemplateAddCustomFood.name),

    url(r'^templates/(?P<template_id>\d+)/remove/food', TemplateRemoveFood.as_view(),
        name=TemplateRemoveFood.name),

    url(r'^templates/(?P<template_id>\d+)/inactive', TemplateSetInactive.as_view(),
        name=TemplateSetInactive.name),

    url(r'^templates/(?P<template_id>\d+)/active', TemplateSetActive.as_view(),
        name=TemplateSetActive.name),

    url(r'^templates/(?P<template_id>\d+)/add/owner', TemplateGrantOwnership.as_view(),
        name=TemplateGrantOwnership.name),

    url(r'^templates/(?P<template_id>\d+)/remove/owner', TemplateRevokeOwnership.as_view(),
        name=TemplateRevokeOwnership.name),

    url(r'^templates/(?P<template_id>\d+)/frequency', TemplateSetFrequency.as_view(),
        name=TemplateSetFrequency.name),

    url(r'^templates/(?P<template_id>\d+)/delete', TemplateDelete.as_view(),
        name=TemplateDelete.name),
]
