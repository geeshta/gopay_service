"""
Basic example of using the Gopay class provided.
"""

from gopay_service import Gopay

# GoPay configuration. Get these from GoPay.
config = {
    "client_id": "...",
    "client_secret": "...",
    "goid": "...",
    "api_root": "https://gw.sandbox.gopay.com/api",
}

# Example payment data
payment_data = {
    "amount": 12000,
    "currency": "CZK",
    "order_number": "Test order",
    "callback": {
        "return_url": "https://example.com/return",
        "notification_url": "https://example.com/notify",
    },
}


def main():
    # Initialize a gopay object, which provides an interface to interact with the GoPay payment system
    gopay = Gopay(**config)

    # Try to create a payment. If successful, print it's URL
    create_response = gopay.create_payment(body=payment_data)
    if create_response.success:
        print(create_response.body.get("gw_url"))

    # Make a payment status inquiry
    status_response = gopay.payment_status(id=create_response.body.get("id"))
    if status_response.success:
        print(status_response.body.get("state"))


if __name__ == "__main__":
    main()
