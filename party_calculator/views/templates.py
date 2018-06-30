from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.base import View, TemplateView

from party_calculator.common import get_form_errors_as_str
from party_calculator.exceptions import MemberAlreadyInPartyException, TemplatePartyScheduleIsNotSetException
from party_calculator.forms import CreateTemplateForm, AddMemberToTemplateForm, SetFrequencyForm, \
    AddCustomFoodToTemplateForm
from party_calculator.models import Food, TemplateParty
from party_calculator.services.food import FoodService
from party_calculator.services.party import PartyService
from party_calculator.services.template_member import TemplateMemberService
from party_calculator.services.template_order import TemplateOrderService
from party_calculator.services.template_party import TemplatePartyService
from party_calculator_auth.models import Profile


class TemplatesListView(ListView):
    name = 'templates'
    template_name = 'templates_list.html'
    context_object_name = 'templates'

    def get_queryset(self):
        return TemplatePartyService().filter(created_by=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TemplatesListView, self).get_context_data(object_list=object_list, **kwargs)
        context[CreateTemplateForm.form_name] = CreateTemplateForm(user=self.request.user)

        return context


class TemplateCreate(View):
    name = 'template-create'

    def post(self, request):
        form = CreateTemplateForm(request.POST, user=request.user)
        if not form.is_valid():
            errors = get_form_errors_as_str(form)
            messages.error(request, errors)
            return redirect(TemplatesListView.name)

        template_party = form.save()
        return redirect(reverse(TemplatePartyView.name, kwargs={'template_id': template_party.id}))


class TemplateCreateFromParty(View):
    name = 'template-create-from-party'

    def post(self, request, party_id: int):
        party = PartyService().get(id=party_id)
        template_party = TemplatePartyService().create_from_existing(party)
        return redirect(reverse(TemplatePartyView.name, kwargs={'template_id': template_party.id}))


class TemplateDelete(View):
    name = 'template-delete'

    def post(self, request, template_id: int):
        template = TemplatePartyService().get(id=template_id)
        TemplatePartyService().delete(template)

        return redirect(reverse(TemplatesListView.name))


class TemplatePartyView(TemplateView):
    name = 'template'
    template_name = 'party_template.html'

    def get_context_data(self, template_id: int, **kwargs):
        context = {}

        template_party = TemplatePartyService().get(id=template_id)
        template_members = TemplatePartyService().get_template_members(template_party)
        template_ordered_food = TemplatePartyService().get_template_ordered_food(template_party)

        context['template'] = template_party
        context['is_active'] = TemplatePartyService().is_active(template_party)
        context['members'] = template_members
        context['ordered_food'] = template_ordered_food

        context['food'] = Food.objects.all()

        context[AddMemberToTemplateForm.form_name] = AddMemberToTemplateForm(party=template_party)
        context[SetFrequencyForm.form_name] = SetFrequencyForm(template=template_party)
        context[AddCustomFoodToTemplateForm.form_name] = AddCustomFoodToTemplateForm(party=template_party)

        return context


class TemplateAddMemberView(View):
    name = 'template-add-member'

    def post(self, request, template_id, **kwargs):
        ps = TemplatePartyService()
        template = ps.get(id=template_id)

        form = AddMemberToTemplateForm(request.POST, party=template)
        if not form.is_valid():
            errors = get_form_errors_as_str(form)
            messages.error(request, errors)
        else:
            info = form.cleaned_data.get('info')
            message_level = messages.ERROR
            try:
                ps.add_member_to_template(template, info)
                message = 'User successfully invited'
                message_level = messages.SUCCESS
            except Profile.DoesNotExist:
                message = 'Such user does not found'
            except MemberAlreadyInPartyException:
                message = 'This member is already in template'

            messages.add_message(request, message_level, message)

        return redirect(reverse(TemplatePartyView.name, kwargs={'template_id': template_id}))


class TemplateKickMember(View):
    name = 'template-kick-member'

    def post(self, request, template_id: int, **kwargs):
        member_id = request.POST.get('member')
        member = TemplateMemberService().get(id=member_id)
        TemplatePartyService().remove_member_from_template(member)

        return redirect(reverse(TemplatePartyView.name, kwargs={'template_id': template_id}))


class TemplateAddFood(View):
    name = 'template-add-food'

    def post(self, request, template_id: int, **kwargs):
        food_id = int(request.POST.get('food'))
        quantity = abs(int(request.POST.get('quantity')))

        template = TemplatePartyService().get(id=template_id)
        food = FoodService().get(id=food_id)
        TemplatePartyService().order_food(template, food, quantity)

        return redirect(reverse(TemplatePartyView.name, kwargs={'template_id': template_id}))


class TemplateAddCustomFood(View):
    name = 'template-add-custom-food'

    def post(self, request, template_id: int, **kwargs):
        template = TemplatePartyService().get(id=template_id)
        form = AddCustomFoodToTemplateForm(request.POST, party=template)
        if not form.is_valid():
            errors = get_form_errors_as_str(form)
            messages.error(request, errors)
        else:
            form.save()

        return redirect(reverse(TemplatePartyView.name, kwargs={'template_id': template_id}))


class TemplateSetInactive(View):
    name = 'template-set-inactive'

    def post(self, request, template_id: int, **kwargs):
        template = TemplatePartyService().get(id=template_id)
        TemplatePartyService().set_state(template, TemplateParty.INACTIVE)

        return redirect(reverse(TemplatePartyView.name, kwargs={'template_id': template_id}))


class TemplateSetActive(View):
    name = 'template-set-active'

    def post(self, request, template_id: int, **kwargs):
        template = TemplatePartyService().get(id=template_id)
        try:
            TemplatePartyService().set_state(template, TemplateParty.ACTIVE)
        except TemplatePartyScheduleIsNotSetException:
            messages.error(request, 'Set template schedule first')
        return redirect(reverse(TemplatePartyView.name, kwargs={'template_id': template_id}))


class TemplateGrantOwnership(View):
    name = 'template-grant-ownership'

    def post(self, request, template_id: int, **kwargs):
        member_id = request.POST.get('member')
        member = TemplateMemberService().get(id=member_id)
        TemplateMemberService().set_owner(member, True)

        return redirect(reverse(TemplatePartyView.name, kwargs={'template_id': template_id}))


class TemplateRevokeOwnership(View):
    name = 'template-revoke-ownership'

    def post(self, request, template_id: int, **kwargs):
        member_id = request.POST.get('member')
        member = TemplateMemberService().get(id=member_id)
        TemplateMemberService().set_owner(member, False)

        return redirect(reverse(TemplatePartyView.name, kwargs={'template_id': template_id}))


class TemplateRemoveFood(View):
    name = 'template-remove-food'

    def post(self, request, template_id: int, **kwargs):
        order_item_id = int(request.POST.get('order_item'))

        order_item = TemplateOrderService().get(id=order_item_id)
        TemplatePartyService().remove_from_order(order_item)

        return redirect(reverse(TemplatePartyView.name, kwargs={'template_id': template_id}))


class TemplateSetFrequency(View):
    name = 'template-set-frequency'

    def post(self, request, template_id: int, **kwargs):
        template = TemplatePartyService().get(id=template_id)

        form = SetFrequencyForm(request.POST, template=template)
        if not form.is_valid():
            errors = get_form_errors_as_str(form)
            messages.error(request, errors)
        else:
            pattern = form.cleaned_data.get('pattern')
            TemplatePartyService().set_frequency(template, pattern)
            messages.success(request, 'Template schedule is set')

        return redirect(reverse(TemplatePartyView.name, kwargs={'template_id': template.id}))
