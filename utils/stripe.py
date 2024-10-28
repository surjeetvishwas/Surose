import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_account(email):
    return stripe.Account.create(
        type='express',
        email=email,
        capabilities={"card_payments": {"requested": True}, "transfers": {"requested": True}},
    )

def create_account_link(account_id, page):
    return stripe.AccountLink.create(
        account=account_id,
        refresh_url=page,
        return_url=page,
        type='account_onboarding',
    )

def delete_account(account_id):
    return stripe.Account.delete(account_id)

def retrieve_account(account_id):
    return stripe.Account.retrieve(account_id)

def create_payment(account_id, items, fee, page):
    return stripe.checkout.Session.create(
        # payment_method_types=['card', 'paypal'],
        line_items=items,
        payment_intent_data={
            'application_fee_amount': fee,
            'transfer_data': {
                'destination': account_id,
            },
        },
        mode='payment',
        return_url=page,
        ui_mode='embedded'
    )

def retrieve_payment(session_id):
    return stripe.checkout.Session.retrieve(session_id)