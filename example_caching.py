"""
Examples for caching the Gopay object. This enables you to reuse it in
multiple HTTP request, without the need to initialize it or get new token
each time.
For this to work, you need to have Redis set up and running and the redis-py
library installed.
`pip install redis`
You also need to secure your Redis. Unpickling untrusted sources can lead to
severe security vulnerabilities
"""

from gopay_service import Gopay
from redis import Redis
import pickle

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

# Connect to redis. Change this to match your Redis configuration if neede.
r = Redis()


def save_gopay(gopay: Gopay) -> None:
    """
    Pickle a Gopay object and save it to Redis
    """
    gopay_pickled = pickle.dumps(gopay)
    r.set("gopay", gopay_pickled)


def load_gopay() -> Gopay:
    """
    Load a previously saved Gopay object from Redis, unpickle it and return it
    """
    gopay_pickled = r.get("gopay")
    gopay = pickle.loads(gopay_pickled)
    return gopay


def main():
    # Initialize a gopay object, which provides an interface to interact with the GoPay payment system
    gopay = Gopay(**config)

    # Try to create a payment. If successful, print it's URL
    create_response = gopay.create_payment(body=payment_data)
    if create_response.success:
        print(create_response.body.get("gw_url"))

    # Cache the object in Redis
    save_gopay(gopay)

    # Load the Gopay object to a new variable
    gopay_loaded = load_gopay()

    # Last response gets saved with the object.
    last_payment_id = gopay_loaded.last_response.body.get("id")

    # Make a payment status inquiry
    status_response = gopay_loaded.payment_status(id=last_payment_id)
    if status_response.success:
        print(status_response.body.get("state"))


if __name__ == "__main__":
    main()
