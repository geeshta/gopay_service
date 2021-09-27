"""
Wrapper around the GoPay REST API: https://doc.gopay.com/. For low level API
communication. Request body needs to be provided as a dictionary.
"""
from typing import Dict, List
from requests.sessions import Session
from .gopay_types import numeric
from .core import api_call


def get_token(
    api_root: str,
    client_id: str,
    client_secret: str,
    body: Dict,
    session: Session = None,
) -> Dict:
    """
    Get an auth token from the GoPay payments system. See
    https://doc.gopay.com/#access-token for a description of the request body
    """
    return api_call(
        url=f"{api_root}/oauth2/token",
        method="POST",
        auth=(client_id, client_secret),
        body=body,
        content="FORM",
        session=session,
    )


def create_payment(
    api_root: str, token: str, body: Dict, session: Session = None
) -> Dict:
    """
    Create a payment. See https://doc.gopay.com/#payment-creation for
    a description of the request body
    """
    return api_call(
        url=f"{api_root}/payments/payment",
        method="POST",
        auth=token,
        body=body,
        content="JSON",
        session=session,
    )


def payment_status(
    api_root: str, token: str, id: numeric, session: Session = None
) -> Dict:
    """
    Get a payment's status. See https://doc.gopay.com/#payment-status
    """
    return api_call(
        url=f"{api_root}/payments/payment/{id}",
        method="GET",
        auth=token,
        session=session,
    )


def refund_payment(
    api_root: str, token: str, id: numeric, body: Dict, session: Session = None
) -> Dict:
    """
    Refund a payment, partially or fully. See
    https://doc.gopay.com/#payment-refund for a description of the request body
    """
    return api_call(
        url=f"{api_root}/payments/payment/{id}/refund",
        method="POST",
        auth=token,
        body=body,
        content="FORM",
        session=session,
    )


def create_recurrence(
    api_root: str, token: str, id: numeric, body: Dict, session: Session = None
) -> Dict:
    """
    Create an on-demand recurrence. See
    https://doc.gopay.com/#recurring-on-demand for description of the request
    body
    """
    return api_call(
        url=f"{api_root}/payments/payment/{id}/create-recurrence",
        method="POST",
        auth=token,
        body=body,
        content="JSON",
        session=session,
    )


def void_recurrence(
    api_root: str, token: str, id: numeric, session: Session = None
) -> Dict:
    """
    Cancel a payment recurrence. See
    https://doc.gopay.com/#recurring-payment-cancellation
    """
    return api_call(
        url=f"{api_root}/payments/payment/{id}/void-recurrence",
        method="POST",
        auth=token,
        session=session,
    )


def capture_preauthorization(
    api_root: str, token: str, id: numeric, session: Session = None
) -> Dict:
    """
    Capture a preauthorized payments. See
    https://doc.gopay.com/#capturing-a-preauthorized-payment
    """
    return api_call(
        url=f"{api_root}/payments/payment/{id}/capture",
        method="POST",
        auth=token,
        session=session,
    )


def capture_preauthorization_partial(
    api_root: str, token: str, id: numeric, body: Dict, session: Session = None
) -> Dict:
    """
    Capture a part of a preauthorized payment's amount. See
    https://doc.gopay.com/#partially-capturing-a-preauthorized-payment for
    a description of the request body
    """
    return api_call(
        url=f"{api_root}/payments/payment/{id}/capture",
        method="POST",
        auth=token,
        body=body,
        content="JSON",
        session=session,
    )


def void_preauthorization(
    api_root: str, token: str, id: numeric, session: Session = None
) -> Dict:
    """
    Void a payment preauthorization. See
    https://doc.gopay.com/#cancelling-a-preauthorized-payment
    """
    return api_call(
        url=f"{api_root}/payments/payment/{id}/void-authorization",
        method="POST",
        auth=token,
        session=session,
    )


def get_payment_methods(
    api_root: str,
    token: str,
    goid: numeric,
    currency: str = None,
    session: Session = None,
) -> Dict:
    """
    Get payment methods. See https://doc.gopay.com/#allowed-payment-methods
    If no currency is provided, list methods for all currencies. That is not
    documented in GoPay REST API.
    """
    return api_call(
        url=f"{api_root}/eshops/eshop/{goid}/payment-instruments/{currency if currency else ''}",
        method="GET",
        auth=token,
        session=session,
    )


def account_statement(
    api_root: str, token: str, body: Dict, session: Session = None
) -> Dict:
    """
    Download an account statement. See https://doc.gopay.com/#account-statement
    for description of the request body
    """
    return api_call(
        url=f"{api_root}/accounts/account-statement",
        method="POST",
        auth=token,
        body=body,
        content="JSON",
        session=session,
    )


def payment_eet_receipts(
    api_root: str, token: str, id: numeric, session: Session = None
) -> List[Dict]:
    """
    Get a list of EET receipts for a single payment. See
    (#TBA)
    """
    return api_call(
        url=f"{api_root}/payments/payment/{id}/eet-receipts",
        method="GET",
        auth=token,
        session=session,
    )


def eet_receipts(
    api_root: str, token: str, body: Dict, session: Session = None
) -> List[Dict]:
    """
    Get a list of EET receipts on an account. See (#TBA)
    """
    return api_root(
        url=f"{api_root}/eet-receipts",
        method="POST",
        auth=token,
        body=body,
        content="JSON",
        session=session,
    )
