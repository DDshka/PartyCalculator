from party_calculator.common.service import Service
from party_calculator.models import TemplateMembership, TemplateParty
from party_calculator_auth.models import Profile


class TemplateMemberService(Service):
    model = TemplateMembership

    def grant_membership(self, party: TemplateParty, profile: Profile):
        self.model.objects.create(profile=profile, party=party)

    def revoke_membership(self, member: model):
        member.delete()

    def grant_ownership(self, member: TemplateMembership):
        member.is_owner = True
        member.save()

    def revoke_ownership(self, member: TemplateMembership):
        member.is_owner = False
        member.save()

    def is_party_member(self, profile: Profile, party: TemplateParty) -> bool:
        return self.model.objects.filter(profile=profile, party=party).exists()
