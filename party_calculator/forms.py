from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets, BaseFormSet, formset_factory

from party_calculator.models import Party, Food, TemplateParty, OrderedFood, Membership
from party_calculator.services.order import OrderService
from party_calculator.services.party import PartyService
from party_calculator.services.profile import ProfileService
from party_calculator.services.template_order import TemplateOrderService
from party_calculator.services.template_party import TemplatePartyService
from party_calculator_auth.models import Profile


class CreatePartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ('name',)

    form_name = 'create_party_form'

    # count = forms.CharField(widget=forms.HiddenInput(attrs={'value': '1'}))
    # member0 = forms.CharField()

    def __init__(self, *args, user=None, **kwargs):
        self.user = user

        super(CreatePartyForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget = forms.widgets.TextInput(
            attrs={'placeholder': 'Enter party name here...'}
        )

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


class MemberForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ('profile',)

    profile = forms.CharField()

    def clean_profile(self):
        username = self.cleaned_data.get('profile')
        return Profile.objects.get(username=username)


class BasePartyMemberFormSet(BaseFormSet):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super(BasePartyMemberFormSet, self).__init__(*args, **kwargs)

    def clean(self):
        if any(self.errors):
            return
        profiles = []
        for form in self.forms:
            profile = form.cleaned_data.get('profile')
            if profile in profiles:
                raise ValidationError('Users in a set must have distinct usernames')
            profiles.append(profile)


PartyMemberFormSet = formset_factory(MemberForm, formset=BasePartyMemberFormSet)


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


class AddMemberToPartyForm(forms.Form):
    form_name = 'add_member_to_party_form'

    info = forms.CharField(max_length=1024, label='Username', widget=widgets.TextInput(
        attrs={'placeholder': 'Enter here username'}))

    def __init__(self, *args, party=None, **kwags):
        self.party = party

        super(AddMemberToPartyForm, self).__init__(*args, **kwags)


class AddMemberToTemplateForm(AddMemberToPartyForm):
    form_name = 'add_member_to_template_form'


class SetFrequencyForm(forms.Form):
    form_name = 'set_frequency_form'

    pattern = forms.CharField()

    def __init__(self, *args, template=None, **kwargs):
        super(SetFrequencyForm, self).__init__(*args, **kwargs)

        self.template = template

        self.fields['pattern'].widget = forms.TextInput(
            attrs={'placeholder': 'Enter crontab pattern here...'}
        )

    def clean_pattern(self):
        pattern = self.cleaned_data.get('pattern')
        splitted = pattern.split(sep=' ')
        # TODO: secure crontab
        if len(splitted) < 5:
            raise ValidationError("Crontab pattern must be made of 5 statements (e.g. * * * * *)")

        return pattern


class CreateTemplateForm(forms.ModelForm):
    class Meta:
        model = TemplateParty
        fields = ('name', 'members', 'food')

    form_name = 'create_template_form'

    food = forms.ModelMultipleChoiceField(queryset=Food.objects.all())

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super(CreateTemplateForm, self).__init__(*args, **kwargs)

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


class SponsorPartyForm(forms.Form):
    form_name = 'sponsor_party_form'

    amount = forms.DecimalField()

    def __init__(self, *args, member=None, **kwargs):
        self.member = member
        super(SponsorPartyForm, self).__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 1:
            raise ValidationError('Sponsor amount can`t be less than 1')

        return amount


class AddCustomFoodToPartyForm(forms.ModelForm):
    class Meta:
        model = OrderedFood
        fields = ('name', 'price', 'quantity')

    form_name = 'add_custom_food_to_party_form'

    def __init__(self, *args, party=None, **kwargs):
        self.party = party
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


class AddCustomFoodToTemplateForm(AddCustomFoodToPartyForm):
    form_name = 'add_custom_food_to_template_form'

    def save(self, commit=True):
        name = self.cleaned_data.get('name')
        price = self.cleaned_data.get('price')
        quantity = int(self.cleaned_data.get('quantity'))

        if commit:
            return TemplateOrderService().create_or_update_order_item(party=self.party,
                                                                      name=name,
                                                                      price=price,
                                                                      quantity=quantity)
