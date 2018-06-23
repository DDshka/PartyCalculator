from crispy_forms.bootstrap import FormActions, FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit, HTML
from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.urls import reverse_lazy

from party_calculator.models import Party, Food, TemplateParty, OrderedFood
from party_calculator.services.order import OrderService
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService
from party_calculator.services.template_order import TemplateOrderService
from party_calculator.services.template_party import TemplatePartyService


class CreatePartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ('name', 'members')

    form_name = 'create_party_form'

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        self.crispy_helper()

        super(CreatePartyForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget = forms.widgets.TextInput(
            attrs={'placeholder': 'Enter party name here...'}
        )

        self.fields['members'].label = ''
        self.fields['members'].required = False
        self.fields['members'].queryset = ProfileService().get_all(excluding={'id': self.user.id})

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Party.objects.filter(name=name).exists():
            raise ValidationError("There can`t be two parties with the same name")

        return name

    def save(self, commit=True) -> Party:
        name = self.cleaned_data.get('name')
        members = self.cleaned_data.get('members')

        creator = ProfileService().get(id=self.user.id)
        party = PartyService().create(name=name, creator=creator, members=members)

        return party

    def crispy_helper(self):
        self.helper = FormHelper()
        self.helper.form_action = reverse_lazy('create-party')
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Div(
                Field('name', css_class='form-control'),
                css_class='form-group'
            ),
            Div(
                HTML('<strong>Select users below to invite them</strong>'),
                Field('members', css_class='form-control'),
                css_class='form-group',
            ),
            FormActions(
                Div(
                    Submit('create_party', 'Create party', css_class="btn-primary"),
                    css_class='form-group'
                )
            )
        )


class CreatePartyFromExistingForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ('name',)

    form_name = 'create_party_from_existing_form'

    name = forms.CharField(max_length=1024, label='Party name', widget=widgets.TextInput(
        attrs={'placeholder': 'Enter here your party name'}))
    existing_party_name = forms.CharField(max_length=1024,
                                          label='Existing party name',
                                          widget=widgets.TextInput(
                                                attrs={'placeholder': 'Enter here existing party name '}))

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        self.crispy_helper()
        super(CreatePartyFromExistingForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Party.objects.filter(name=name).exists():
            raise ValidationError("There can`t be two parties with the same name")

        return name

    def clean_existing_party_name(self):
        existing_party_name = self.cleaned_data.get('existing_party_name')
        if not Party.objects.filter(name=existing_party_name).exists():
            raise ValidationError("There no party with name {0}".format(existing_party_name))

        return existing_party_name

    def save(self, commit=True):
        name = self.cleaned_data.get('name')
        existing_party_name = self.cleaned_data.get('existing_party_name')

        ps = PartyService()
        existing_party = ps.get(name=existing_party_name)
        creator = ProfileService().get(id=self.user.id)
        members = ps.get_party_profiles(existing_party, excluding={'id': creator.id})

        return ps.create(name=name, creator=creator, members=members)

    def crispy_helper(self):
        self.helper = FormHelper()
        self.helper.form_action = reverse_lazy('create-party-from-existing')
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Div(
                Field('name', css_class='form-control'),
                css_class='form-group'
            ),
            Div(
                Field('existing_party_name', css_class='form-control'),
                css_class='form-group'
            ),
            FormActions(
                Div(
                    Submit('create_party_from_existing',
                           'Create party from existing one',
                           css_class="btn-primary"),
                    css_class='form-group'
                )
            )
        )


class AddMemberToPartyForm(forms.Form):
    form_name = 'add_member_to_party_form'

    info = forms.CharField(max_length=1024, label='Username', widget=widgets.TextInput(
        attrs={'placeholder': 'Enter here username'}))

    def __init__(self, *args, party=None, **kwags):
        self.party = party
        self.crispy_helper()

        super(AddMemberToPartyForm, self).__init__(*args, **kwags)

    def crispy_helper(self):
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_action = reverse_lazy('invite-member',
                                               kwargs={'party_id': self.party.id})
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            FieldWithButtons(
                Field('info', css_class='form-control'),
                Submit('invite-member', 'Invite', css_class="btn-success"))
        )


class AddMemberToTemplateForm(AddMemberToPartyForm):
    form_name = 'add_member_to_template_form'

    def __init__(self, *args, **kwargs):
        super(AddMemberToTemplateForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse_lazy('template-add-member',
                                               kwargs={'template_id': self.party.id})


class SetFrequencyForm(forms.Form):
    form_name = 'set_frequency_form'

    pattern = forms.CharField()

    def __init__(self, *args, template=None, **kwargs):
        super(SetFrequencyForm, self).__init__(*args, **kwargs)

        self.template = template
        self.crispy_helper()

        self.fields['pattern'].widget = forms.TextInput(
            attrs={'placeholder': 'Enter crontab pattern here...'}
        )

    def clean_pattern(self):
        pattern = self.cleaned_data.get('pattern')
        splitted = pattern.split(sep=' ')
        if len(splitted) < 5:
            raise ValidationError("Crontab pattern must be made of 5 statements (e.g. * * * * *)")

        return pattern

    def crispy_helper(self):
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_action = reverse_lazy('template-set-frequency',
                                               kwargs={'template_id': self.template.id})
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            FieldWithButtons(
                Field('pattern', css_class='form-control'),
                Submit('set-frequency', 'Set frequency', css_class="btn-success"))
        )


class CreateTemplateForm(CreatePartyForm):
    form_name = 'create_template_form'

    food = forms.ModelMultipleChoiceField(queryset=Food.objects.all())

    def __init__(self, *args, user=None, **kwargs):
        super(CreateTemplateForm, self).__init__(*args, user=user, **kwargs)

        self.crispy_helper()
        self.fields['food'].required = False
        self.fields['members'].required = False

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if TemplatePartyService().filter(name=name).exists():
            raise ValidationError("Template with such name already exists")

        return name

    def save(self, commit=True) -> TemplateParty:
        name = self.cleaned_data.get('name')
        members = self.cleaned_data.get('members')
        food = self.cleaned_data.get('food')

        creator = ProfileService().get(id=self.user.id)
        return TemplatePartyService().create(name=name,
                                             creator=creator,
                                             members=members,
                                             food=food)

    def crispy_helper(self):
        self.helper = FormHelper()
        self.helper.form_action = reverse_lazy('create-template')
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Div(
                Field('name', css_class='form-control'),
                css_class='form-group'
            ),
            Div(
                Field('members', css_class='form-control'),
                css_class='form-group'
            ),
            Div(
                Field('food', css_class='form-control'),
                css_class='form-group'
            ),
            FormActions(
                Div(
                    Submit('create_template', 'Create template', css_class="btn-primary"),
                    css_class='form-group'
                )
            )
        )


class SponsorPartyForm(forms.Form):
    form_name = 'sponsor_party_form'

    amount = forms.DecimalField()

    def __init__(self, *args, member=None, **kwargs):
        self.member = member
        self.crispy_helper()
        super(SponsorPartyForm, self).__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 1:
            raise ValidationError('Sponsor amount can`t be less than 1')

        return amount

    def crispy_helper(self):
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_action = reverse_lazy('sponsor-party',
                                               kwargs={'party_id': self.member.party.id})
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            FieldWithButtons(
                Field('amount', css_class='form-control'),
                Submit('sponsor-party', 'Sponsor', css_class="btn-success"))
        )


class AddCustomFoodToPartyForm(forms.ModelForm):
    class Meta:
        model = OrderedFood
        fields = ('name', 'price', 'quantity')

    form_name = 'add_custom_food_to_party_form'

    def __init__(self, *args, party=None, **kwargs):
        self.party = party
        self.crispy_helper()
        super(AddCustomFoodToPartyForm, self).__init__(*args, **kwargs)

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise ValidationError("Price can`t be negative")

        return price

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise ValidationError("Quantity must be more than 0")

        return quantity

    def save(self, commit=True):
        name = self.cleaned_data.get('name')
        price = self.cleaned_data.get('price')
        quantity = int(self.cleaned_data.get('quantity'))

        if commit:
            return OrderService().create_or_update_order_item(party=self.party,
                                                              name=name,
                                                              price=price,
                                                              quantity=quantity)

    def crispy_helper(self):
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_action = reverse_lazy('add-custom-food-to-party',
                                               kwargs={'party_id': self.party.id})
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Div(
                Field('name', css_class='form-control'),
                css_class='form-group'
            ),
            Div(
                Field('price', css_class='form-control'),
                css_class='form-group'
            ),
            Div(
                Field('quantity', css_class='form-control'),
                css_class='form-group'
            ),
            FormActions(
                Div(
                    Submit('add_custom_food',
                           'Add custom food'),
                    css_class='form-group'
                )
            )
        )


class AddCustomFoodToTemplateForm(AddCustomFoodToPartyForm):
    form_name = 'add_custom_food_to_template_form'

    def __init__(self, *args, **kwargs):
        super(AddCustomFoodToTemplateForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse_lazy('template-add-custom-food',
                                               kwargs={'template_id': self.party.id})

    def save(self, commit=True):
        name = self.cleaned_data.get('name')
        price = self.cleaned_data.get('price')
        quantity = int(self.cleaned_data.get('quantity'))

        if commit:
            return TemplateOrderService().create_or_update_order_item(party=self.party,
                                                                      name=name,
                                                                      price=price,
                                                                      quantity=quantity)
