from django.test import TestCase

from party_calculator.models import Membership, Party
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService
from party_calculator_auth.models import Profile


class CreatePartyTestCase(TestCase):
    party_service = PartyService()
    profile_service = ProfileService()

    def setUp(self):
        Profile.objects.create(username='test_user_one')
        Profile.objects.create(username='test_user_two')

    def test_create_party(self):
        creator = Profile.objects.get(username='test_user_one')

        party_to_create = self.party_service.create(name='test_party', creator=creator)

        actual_party = Party.objects.get(name='test_party')

        self.assertEqual(party_to_create, actual_party)


class AddMemberToPartyTestCase(TestCase):
    party_service = PartyService()
    profile_service = ProfileService()

    def setUp(self):
        creator = Profile.objects.create(username='test_user_one')
        Profile.objects.create(username='test_user_two')

        Party.objects.create(name='test_party', created_by=creator)

    def test_add_member(self):
        party = self.party_service.get(name='test_party')
        user_two = self.profile_service.get(username='test_user_two')

        self.party_service.add_member_to_party(party, user_two)

        party_membership = party.memberships.get(profile=user_two)
        actual_membership = Membership.objects.get(party=party, profile=user_two)

        self.assertEqual(party_membership, actual_membership)


class RemoveMemberFromPartyTestCase(TestCase):
    party_service = PartyService()
    profile_service = ProfileService()

    def setUp(self):
        creator = Profile.objects.create(username='test_user_one')
        member = Profile.objects.create(username='test_user_two')

        party = Party.objects.create(name='test_party', created_by=creator)
        Membership.objects.create(party=party, profile=member)

    def test_remove_member(self):
        party = self.party_service.get(name='test_party')
        user_two = Profile.objects.get(username='test_user_two')
        membership = Membership.objects.get(party=party, profile=user_two)

        self.party_service.remove_member_from_party(membership)

        is_in_party = party.memberships.filter(profile=user_two).exists()

        self.assertFalse(is_in_party)