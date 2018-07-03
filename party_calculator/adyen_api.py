import json

import requests

from PartyCalculator.settings import ADYEN_CURRENCY, ADYEN_REFERENCE, ADYEN_MERCHANT_ACCOUNT, \
    ADYEN_AUTORIZE_CARD_ENDPOINT, ADYEN_LIST_RECCURRING_DETAILS_ENDPOINT, ADYEN_USER, ADYEN_DISABLE_CARD_ENDPOINT, \
    ADYEN_PASSWORD
from party_calculator.services.profile import ProfileService
from party_calculator.utils import get_client_ip
from party_calculator_auth.models import Profile


def make_bin_verification(request, card_encrypted_data):
    profile = ProfileService().get(id=request.user.id)
    client_ip = get_client_ip(request)

    dictionary = {
        'amount': {
            'value': 0,
            'currency': ADYEN_CURRENCY
        },
        'additionalData': {
            'card.encrypted.json': card_encrypted_data
        },
        'reference': ADYEN_REFERENCE,
        'merchantAccount': ADYEN_MERCHANT_ACCOUNT,
        'shopperEmail' : profile.email,
        'shopperIP': client_ip,
        'shopperReference': profile.email,
        'recurring':{
            'contract': 'RECURRING'
       }
    }

    json_data = json.dumps(dictionary)
    response = send_post(ADYEN_AUTORIZE_CARD_ENDPOINT, json_data)

    return response


def list_reccuring_details(profile: Profile):
    dictionary = {
        'merchantAccount': ADYEN_MERCHANT_ACCOUNT,
        'shopperReference': profile.email
    }

    json_data = json.dumps(dictionary)
    response = send_post(ADYEN_LIST_RECCURRING_DETAILS_ENDPOINT, json_data)

    return response


def update_stored_details(request, card, recurring_detail_reference):
    profile = ProfileService().get(id=request.user.id)
    client_ip = get_client_ip(request)

    dictionary = {
        'amount': {
          'value': '0',
          'currency': ADYEN_CURRENCY
        },
        "card":{
            "expiryMonth": card['expiryMonth'],
            "expiryYear": card['expiryYear']
        },
        'merchantAccount': ADYEN_MERCHANT_ACCOUNT,
        'recurring': {
          'contract': 'RECURRING'
        },
        'reference': ADYEN_REFERENCE,
        'shopperEmail': profile.email,
        'shopperIP': client_ip,
        "shopperInteraction": "ContAuth",
        'shopperReference': profile.email,
        'selectedRecurringDetailReference': recurring_detail_reference
    }

    json_data = json.dumps(dictionary)
    response = send_post(ADYEN_AUTORIZE_CARD_ENDPOINT, json_data)

    return response


def disable_stored_details(profile: Profile, recurring_detail_reference):
    dictionary = {
        'merchantAccount': ADYEN_MERCHANT_ACCOUNT,
        'shopperReference': profile.email,
        'recurringDetailReference': recurring_detail_reference,
        'contract': 'RECURRING'
    }

    json_data = json.dumps(dictionary)
    response = send_post(ADYEN_DISABLE_CARD_ENDPOINT, json_data)

    return response


def send_post(endpoint, data):
    return requests.post(endpoint,
                         auth=(ADYEN_USER, ADYEN_PASSWORD),
                         data=data,
                         headers={
                             'Content-Type': 'application/json',
                         })
