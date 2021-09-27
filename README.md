# GoPay Service

Interface for interacting with the [GoPay REST API](https://doc.gopay.com/).

## Installation

Requires Python >= 3.7

- Create a virtual env: `python -m venv venv`
- Activate it: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- [Optional] to make the caching example work, install redis-py: `pip install redis`

## Usage

- Using the Gopay class, which does a lot of things for you (see `example.py`)
- Using the `rest` module, which is a low-level wrapper around the GoPay REST API (see `example_rest.py`)

To reuse the keep the Gopay object instance between multiple request, you can pickle and cache it. See `example_caching.py`, which shows caching in Redis.
