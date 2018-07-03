from party_calculator.adyen_api import list_reccuring_details, update_stored_details, disable_stored_details
from party_calculator_auth.models import Profile


class AdyenCardService():
    def get_all_cards(self, profile: Profile):
        adyen_response = list_reccuring_details(profile).json()

        cards = []
        for detail in adyen_response['details']:
            cards.append({
                'number': detail['RecurringDetail']['card']['number'],
                'exp_month': detail['RecurringDetail']['card']['expiryMonth'],
                'exp_year': detail['RecurringDetail']['card']['expiryYear'],
                'recurring_detail_reference': detail['RecurringDetail']['recurringDetailReference']
            })

        return cards

    def update_card(self, request, card, recurring_detail_reference):
        update_stored_details(request, card, recurring_detail_reference)

    def delete_card(self, profile: Profile, recurring_detail_reference):
        disable_stored_details(profile, recurring_detail_reference)