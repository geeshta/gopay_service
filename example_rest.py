"""
Example showing the usage of the low-level rest module. This is just a wrapper
around the GoPay REST API available here: https://doc.gopay.com.
An optional session parameter can be passed to use the Session object of the
request library, which enables TCP connection reuse
"""

from gopay_service import rest

# GoPay configuration. Get these from GoPay.
client_id = "..."
client_secret = "..."
goid = "..."
api_root = "https://gw.sandbox.gopay.com/api"

# Example payment data
payment_data = {
    "amount": 12000,
    "currency": "CZK",
    "order_number": "Test order",
    "target": {"type": "ACCOUNT", "goid": goid},
    "callback": {
        "return_url": "https://example.com/return",
        "notification_url": "https://example.com/notify",
    },
}


def main():
    # Create an auth token with the provided credentials
    token_response = rest.get_token(
        api_root=api_root,
        client_id=client_id,
        client_secret=client_secret,
        body={"scope": "payment-all", "grant_type": "client_credentials"},
    )

    if token_response.get("success"):
        token = token_response.get("body").get("access_token")

    # Create a payment. Use the token to authenticate. Print the payment URL
    create_response = rest.create_payment(
        api_root=api_root, token=token, body=payment_data
    )

    if create_response.get("success"):
        print(create_response.get("body").get("gw_url"))

    # Payment status inquiry. The token can be reused until it expires
    status_response = rest.payment_status(
        api_root=api_root, token=token, id=create_response.get("body").get("id")
    )

    if status_response.get("success"):
        print(status_response.get("body").get("state"))


def main_with_session():
    from requests import Session

    # Use a request Session object to enable TCP connection reuse
    with Session() as session:
        # Create an auth token with the provided credentials
        token_response = rest.get_token(
            session=session,
            api_root=api_root,
            client_id=client_id,
            client_secret=client_secret,
            body={"scope": "payment-all", "grant_type": "client_credentials"},
        )

        if token_response.get("success"):
            token = token_response.get("body").get("access_token")

        # Create a payment. Use the token to authenticate. Print the payment URL
        create_response = rest.create_payment(
            session=session, api_root=api_root, token=token, body=payment_data
        )

        if create_response.get("success"):
            print(create_response.get("body").get("gw_url"))

        # Payment status inquiry. The token can be reused until it expires
        status_response = rest.payment_status(
            session=session,
            api_root=api_root,
            token=token,
            id=create_response.get("body").get("id"),
        )

        if status_response.get("success"):
            print(status_response.get("body").get("state"))


if __name__ == "__main__":
    main()
    main_with_session()
